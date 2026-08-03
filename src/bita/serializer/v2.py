from __future__ import annotations

import json
from typing import TYPE_CHECKING

from bita.model.canvas import Canvas
from bita.model.range import Range
from bita.serializer.builder import Builder
from bita.vocabulary import DEFAULT_LANGUAGE

if TYPE_CHECKING:
    from bita import Image, Manifest


class V2Builder(Builder):
    CONTEXT = "http://iiif.io/api/presentation/2/context.json"

    def search_id(self, identifier: str) -> str:
        id_ = super().search_id(identifier)
        return f"{id_}?q=v2_"

    def serialize(self, manifest: Manifest) -> dict:
        self.annotations = {}
        data = {
            "@context": self.CONTEXT,
            "@id": self.presentation_id(manifest.identifier_),
            "@type": "sc:Manifest",
        }
        data |= self.serialize_resources(manifest)
        data |= self.serialize_metadata(manifest)
        data |= self.serialize_sequences(manifest)
        data |= self.serialize_structures(manifest)
        if service := self.serialize_search_service(manifest):
            data["service"] = [service]  # type: ignore  # noqa: PGH003
        return data

    def serialize_metadata(self, manifest: Manifest) -> dict:
        data = []
        for meta in manifest.metadata_:
            if label := meta.data.get("label", {}).get(DEFAULT_LANGUAGE):
                value = meta.data.get("value", {}).get(DEFAULT_LANGUAGE)
                value = value if value else meta.data.get("value", {}).get("none")
                if value:
                    data.append({"label": label, "value": value})
        if hasattr(manifest, "attribution_") and manifest.attribution.default_lang_value():
            data.append({"label": "帰属", "value": manifest.attribution.default_lang_value()})
        if hasattr(manifest, "terms_") and manifest.terms_:
            data.append({"label": "利用規約", "value": manifest.terms_})
        if data:
            return {"metadata": data}
        return {}

    def serialize_resources(self, manifest: Manifest) -> dict:
        data = {}
        if manifest.label_ and manifest.label.default_lang_value():
            data["label"] = manifest.label.default_lang_value()
        if manifest.description_ and manifest.description.default_lang_value():
            data["description"] = manifest.description.default_lang_value()
        if manifest.attribution_ and manifest.attribution.default_lang_value():
            data["attribution"] = manifest.attribution.default_lang_value()

        if hasattr(manifest, "license_") and manifest.license_:
            data["license"] = manifest.license_
        if hasattr(manifest, "nav_date_") and manifest.nav_date_:
            data["navDate"] = self.format_nav_date(manifest.nav_date_)

        if (
            hasattr(manifest, "provider_")
            and manifest.provider_
            and hasattr(manifest.provider_, "logo_")
        ):
            data["logo"] = manifest.provider_.logo_
        return data

    def serialize_view_settings(self, manifest: Manifest) -> dict:
        data = {}
        if manifest.viewing_direction.values:
            data["viewingDirection"] = manifest.viewing_direction.value
        if manifest.behavior.values:
            data["viewingHint"] = manifest.behavior.value
        return data

    def serialize_sequences(self, manifest: Manifest) -> dict:
        data = {
            "@id": self.sequence_id(manifest.identifier_),
            "@type": "sc:Sequence",
            "canvases": [],
        }
        data |= self.serialize_view_settings(manifest)
        data |= self.serialize_canvases(manifest)
        return {"sequences": [data]}

    def serialize_canvases(self, manifest: Manifest) -> dict:
        data = []
        for n, cv in enumerate(manifest.canvas_):
            idx = n + 1
            canvas_id = self.canvas_id(manifest.identifier_, idx)
            cv.id_ = canvas_id
            canv = {
                "@id": canvas_id,
                "@type": "sc:Canvas",
                "width": cv.width,
                "height": cv.height,
            }

            label = str(idx)
            if cv.label_:
                label = cv.label_.get(DEFAULT_LANGUAGE) or cv.label_.get("none")
            canv["label"] = label

            canv |= self.serialize_images(cv)

            if cv.has_annotation():
                annot_id = f"{canvas_id}/annotation/0"
                canv["otherContent"] = [
                    {
                        "@id": annot_id,
                        "@type": "sc:AnnotationList",
                    },
                ]
                self.annotations[annot_id] = self.serialize_annotations(cv, annot_id)

            data.append(canv)
        return {"canvases": data}

    def serialize_images(self, canvas: Canvas) -> dict:
        data = []
        for n, img in enumerate(canvas.images):
            on = canvas.id_
            if (
                img.x is not None
                and img.y is not None
                and img.width is not None
                and img.height is not None
            ):
                on = f"{on}#xywh={img.x},{img.y},{img.width},{img.height}"
            im = {
                "@id": f"{canvas.id_}/image/{n}",
                "@type": "oa:Annotation",
                "motivation": "sc:painting",
                "on": on,
                "resource": self.serialize_image(img),
            }
            data.append(im)
        return {"images": data}

    def serialize_image(self, image: Image) -> dict:
        data = {
            "@id": self.image_id(image),
            "@type": "dctypes:Image",
            "format": "image/jpeg",
            "height": image.height,
            "width": image.width,
            "service": self.image_service(image),
        }
        if image.label_ and image.label.default_lang_value():
            data["label"] = image.label.default_lang_value()
        return data

    def serialize_structures(self, manifest: Manifest) -> dict:
        data = []
        for n, item in enumerate(manifest.structure_):
            range_id = self.range_id(manifest.identifier_, n)
            structure = {
                "@id": range_id,
                "@type": "sc:Range",
                "members": [],
            }

            if label := item.label.default_lang_value():
                structure["label"] = label

            structure["members"] = self.serialize_members(item, range_id)
            data.append(structure)

        if data:
            return {"structures": data}
        return {}

    def serialize_members(self, item: Range | Canvas, range_id: str) -> list:
        if isinstance(item, Canvas):
            return [
                {
                    "@id": item.id_,
                    "@type": "sc:Canvas",
                },
            ]

        canvases = []
        labels = []
        if isinstance(item, Range):
            for itm in item.members_:
                canvases.extend(self.serialize_members(itm, range_id))
                if isinstance(itm, Range):
                    labels.append(itm.label.default_lang_value())
                else:
                    labels.append(None)

        if len(canvases) == 1:
            return canvases

        members = []
        for n, cv in enumerate(canvases):
            id_ = f"{range_id}/canvas/{n}"
            member = {
                "@id": id_,
                "@type": "sc:Range",
                "canvases": [cv["@id"]],
            }
            if label := labels[n]:
                member["label"] = label
            members.append(member)

        return members

    def serialize_search_service(self, manifest: Manifest) -> dict:
        data = {}
        if bool([x for x in manifest.canvas_ if x.has_annotation()]):
            data = self.search_service(2, manifest.identifier_)
        return data

    def serialize_annotations(self, canvas: Canvas, annotation_id: str) -> dict:
        data = []
        for n, annot in enumerate(canvas.annotations):
            on = canvas.id_
            if (
                annot.x is not None
                and annot.y is not None
                and annot.w is not None
                and annot.h is not None
            ):
                on = f"{on}#xywh={annot.x},{annot.y},{annot.w},{annot.h}"
            item = {
                "@id": f"{annotation_id}/{n}",
                "@type": "oa:Annotation",
                "motivation": f"oa:{annot.motivation.value}",
                "on": on,
                "resource": {
                    "@type": "cnt:ContentAsText",
                    "chars": annot.value,
                    "format": "text/plain",
                },
            }
            data.append(item)
        return {
            "@context": self.CONTEXT,
            "@id": annotation_id,
            "@type": "sc:AnnotationList",
            "resources": data,
        }

    def create_annotation_list(self, manifest: Manifest) -> dict:
        self.serialize(manifest)
        return self.annotations
