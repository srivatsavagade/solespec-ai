import json
from dataclasses import fields
from pathlib import Path
from typing import Any

from src.solespec.schemas.techpack_schema import ComponentSpec, MaterialSpec


class ReviewOverrideError(ValueError):
    pass


def load_review_overrides(path: Path | str | None) -> dict[str, Any]:
    if path is None:
        return {}

    override_path = Path(path)
    if not override_path.exists():
        raise FileNotFoundError(f"Review override file not found: {override_path}")

    if override_path.suffix.lower() != ".json":
        raise ReviewOverrideError(
            "Review overrides currently support JSON files. "
            "Use a .json file such as configs/review_overrides.example.json."
        )

    with override_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ReviewOverrideError("Review override file must contain a JSON object.")

    return data


def apply_review_overrides(
    components: list[ComponentSpec],
    materials: list[MaterialSpec],
    overrides: dict[str, Any] | None,
) -> tuple[list[ComponentSpec], list[MaterialSpec], list[str]]:
    if not overrides:
        return components, materials, []

    notes: list[str] = []
    component_overrides = _normalise_override_entries(
        overrides.get("components", []),
        fallback_key="mesh_name",
    )
    material_overrides = _normalise_override_entries(
        overrides.get("materials", []),
        fallback_key="name",
    )

    for override in component_overrides:
        matched = False
        for component in components:
            if _matches(component, override.get("match", {}), fallback_key="mesh_name"):
                _apply_dataclass_updates(component, override, ComponentSpec)
                matched = True
        if matched:
            notes.append(f"Applied component review override: {override.get('match', {})}")

    for override in material_overrides:
        matched = False
        for material in materials:
            if _matches(material, override.get("match", {}), fallback_key="name"):
                _apply_dataclass_updates(material, override, MaterialSpec)
                matched = True
        if matched:
            notes.append(f"Applied material review override: {override.get('match', {})}")

    explicit_notes = overrides.get("notes", [])
    if isinstance(explicit_notes, str):
        notes.append(explicit_notes)
    elif isinstance(explicit_notes, list):
        notes.extend(str(note) for note in explicit_notes)

    return components, materials, notes


def _normalise_override_entries(raw_entries: Any, fallback_key: str) -> list[dict[str, Any]]:
    if isinstance(raw_entries, dict):
        return [
            {"match": {fallback_key: key}, **value}
            if isinstance(value, dict)
            else {"match": {fallback_key: key}}
            for key, value in raw_entries.items()
        ]

    if not isinstance(raw_entries, list):
        return []

    return [entry for entry in raw_entries if isinstance(entry, dict)]


def _matches(item: Any, match: dict[str, Any], fallback_key: str) -> bool:
    if not match:
        return False

    for key, expected in match.items():
        if not hasattr(item, key) or getattr(item, key) != expected:
            return False

    return True


def _apply_dataclass_updates(item: Any, override: dict[str, Any], spec_type: type) -> None:
    allowed_fields = {field.name for field in fields(spec_type)}
    skipped_keys = {"match"}

    for key, value in override.items():
        if key in skipped_keys or key not in allowed_fields:
            continue
        setattr(item, key, value)
