from __future__ import annotations

import mimetypes
from typing import TYPE_CHECKING

from bita.model.canvas import Canvas
from bita.model.range import Range
from bita.serializer.builder import Builder

if TYPE_CHECKING:
    from bita import Image, Manifest


class V3Builder(Builder):
    CONTEXT = "http://iiif.io/api/presentation/3/context.json"

    def serialize(self, manifest: Manifest) -> dict:
        data = {
            "@context": self.CONTEXT,
            "id": self.presentation_id(manifest.identifier_),
            "type": "Manifest",
        }
        data |= self.serialize_resources(manifest)
        data |= self.serialize_metadata(manifest)
        data |= self.serialize_view_settings(manifest)
        data |= self.serialize_canvas(manifest)
        data |= self.serialize_structures(manifest)
        if service := self.serialize_search_service(manifest):
            data["service"] = [service]  # pyright: ignore[reportArgumentType]
        return data

    def serialize_attribution(self, manifest: Manifest) -> dict:
        if manifest.attribution_:
            LABEL = {"ja": ["帰属"], "en": ["Attribution"]}  # noqa: N806
            label = {}
            value = manifest.attribution.value()
            for k in value:
                label |= {k: LABEL.get(k)}
            return {"label": label, "value": value}
        return {}

    def serialize_metadata(self, manifest: Manifest) -> dict:
        data = []
        data.extend(
            [
                {
                    "label": {k: [v] for k, v in meta.data["label"].items()},
                    "value": {k: [v] for k, v in meta.data["value"].items()},
                }
                for meta in manifest.metadata_
            ],
        )
        if attr := self.serialize_attribution(manifest):
            data.append(attr)
        if hasattr(manifest, "terms_") and manifest.terms_:
            terms = {
                "label": {"en": ["Terms of Use"], "ja": ["利用規約"]},
                "value": {"none": [manifest.terms_]},
            }
            data.append(terms)
        if data:
            return {"metadata": data}
        return {}

    def serialize_resources(self, manifest: Manifest) -> dict:
        data = {}
        if manifest.label_:
            data["label"] = manifest.label.value()
        if manifest.description_:
            data["summary"] = manifest.description.value()
        if attr := self.serialize_attribution(manifest):
            data["requiredStatement"] = attr

        if hasattr(manifest, "license_") and manifest.license_:
            data["rights"] = manifest.license_
        if hasattr(manifest, "nav_date_") and manifest.nav_date_:
            data["navDate"] = self.format_nav_date(manifest.nav_date_)

        if hasattr(manifest, "provider_") and manifest.provider_ and manifest.provider_.homepage_:
            homepage = {
                "format": "text/html",
                "id": manifest.provider_.homepage_,
                "type": "Text",
            }
            provider = {
                "id": manifest.provider_.homepage_,
                "type": "Agent",
                "homepage": [homepage],
            }

            if manifest.provider_.name_:
                provider["label"] = manifest.provider_.name.value()
                homepage["label"] = manifest.provider_.name.value()  # pyright: ignore[reportArgumentType]

            if logo := manifest.provider_.logo_:
                mime_type, _ = mimetypes.guess_type(logo)
                provider["logo"] = [
                    {
                        "format": mime_type,
                        "id": logo,
                        "type": "Image",
                    },
                ]
            data["provider"] = [provider]
        return data

    def serialize_view_settings(self, manifest: Manifest) -> dict:
        data = {}
        if manifest.viewing_direction.values:
            data["viewingDirection"] = manifest.viewing_direction.value
        if manifest.behavior.values:
            data["behavior"] = manifest.behavior.values
        return data

    def serialize_canvas(self, manifest: Manifest) -> dict:
        data = []
        for n, cv in enumerate(manifest.canvas_):
            idx = n + 1
            canvas_id = self.canvas_id(manifest.identifier_, idx)
            cv.id_ = canvas_id
            canv = {
                "id": canvas_id,
                "type": "Canvas",
                "width": cv.width,
                "height": cv.height,
            }

            label = {"none": [str(idx)]}
            if cv.label_:
                label = cv.label.value()
            canv["label"] = label

            canv |= self.serialize_images(cv)
            if cv.has_annotation():
                canv |= {"annotations": [self.serialize_annotations(cv)]}

            data.append(canv)
        return {"items": data}

    def serialize_images(self, canvas: Canvas) -> dict:
        data = []
        item_id = f"{canvas.id_}/item/0"
        for n, img in enumerate(canvas.images):
            im = self.serialize_image(img)
            im["id"] = f"{item_id}/image/{n}"
            target = canvas.id_
            if (
                img.x is not None
                and img.y is not None
                and img.width is not None
                and img.height is not None
            ):
                target = f"{target}#xywh={img.x},{img.y},{img.width},{img.height}"
            im["target"] = target
            data.append(im)
        return {
            "items": [
                {
                    "id": item_id,
                    "type": "AnnotationPage",
                    "items": data,
                },
            ],
        }

    def serialize_image(self, image: Image) -> dict:
        img = {
            "body": {
                "id": self.image_id(image),
                "type": "Image",
                "format": "image/jpeg",
                "height": image.height,
                "width": image.width,
                "service": [self.image_service(image)],
            },
            "motivation": "painting",
            "type": "Annotation",
        }
        if label := image.label.value():
            img["body"]["label"] = label
        return img

    def serialize_structures(self, manifest: Manifest) -> dict:
        data = []
        for n, item in enumerate(manifest.structure_):
            range_id = self.range_id(manifest.identifier_, n)
            structure = {
                "id": range_id,
                "type": "Range",
                "items": [],
            }

            if label := item.label.value():
                structure["label"] = label

            structure["items"] = self.serialize_items(item, range_id)
            data.append(structure)

        if data:
            return {"structures": data}
        return {}

    def serialize_items(self, item: Range | Canvas, range_id: str) -> list:
        if isinstance(item, Canvas):
            return [
                {
                    "id": item.id_,
                    "type": "Canvas",
                },
            ]

        canvases = []
        labels = []
        if isinstance(item, Range):
            for itm in item.members_:
                canvases.extend(self.serialize_items(itm, range_id))
                if isinstance(itm, Range):
                    labels.append(itm.label.value())
                else:
                    labels.append(None)

        if len(canvases) == 1:
            return canvases

        items = []
        for n, cv in enumerate(canvases):
            id_ = f"{range_id}/canvas/{n}"
            itm = {
                "id": id_,
                "type": "Range",
                "items": [cv],
            }
            if label := labels[n]:
                itm["label"] = label
            items.append(itm)

        return items

    def serialize_search_service(self, manifest: Manifest) -> dict:
        data = {}
        if bool([x for x in manifest.canvas_ if x.has_annotation()]):
            data = self.search_service(3, manifest.identifier_)
        return data

    def serialize_annotations(self, canvas: Canvas) -> dict:
        data = []
        annot_id = f"{canvas.id_}/annotation/0"
        for n, annot in enumerate(canvas.annotations):
            target = canvas.id_
            if (
                annot.x is not None
                and annot.y is not None
                and annot.w is not None
                and annot.h is not None
            ):
                target = f"{target}#xywh={annot.x},{annot.y},{annot.w},{annot.h}"
            item = {
                "body": {
                    "format": "text/plain",
                    "language": annot.language,
                    "type": "TextualBody",
                    "value": annot.value,
                },
                "id": f"{annot_id}/{n}",
                "target": target,
                "motivation": annot.motivation.value,
                "type": "Annotation",
            }
            data.append(item)
        return {"id": annot_id, "type": "AnnotationPage", "items": data}
