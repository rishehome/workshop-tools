"""Explicit source-coordinate face directions for studio cameras (no Blender dependency)."""
import json

AXES = {sign + axis: tuple(direction if i == index else 0 for i in range(3))
        for index, axis in enumerate("XYZ") for sign, direction in (("+", 1), ("-", -1))}


def add_orientation_arguments(cli):
    for face in ("top", "front"):
        cli.add_argument(f"--{face}-axis", type=str.upper, choices=AXES,
                         help=f"Source axis pointing out of the {face} face; overrides SOURCE.render.json")


def model_orientation(model_dir):
    """Read authored orientation from native model metadata or a standalone facts file."""
    from export_metadata import read_model_metadata
    owner, facts = read_model_metadata(model_dir)
    path = model_dir / "model-facts.json"
    if facts is None and path.is_file():
        try:
            facts = json.loads(path.read_text())
        except (OSError, ValueError) as exc:
            raise ValueError(f"{path}: {exc}") from exc
    if facts is not None and not isinstance(facts, dict):
        raise ValueError(f"{model_dir}: model facts must be an object")
    orientation = facts.get("orientation", {}) if facts is not None else {}
    if not isinstance(orientation, dict) or set(orientation) - {"top", "front"}:
        raise ValueError(f"{model_dir}: orientation must be an object containing only top and front")
    return orientation


def resolve_orientation(source, top=None, front=None, model_dir=None):
    """Read per-source settings, then apply CLI overrides and validate the frame."""
    config = source.with_name(source.name + ".render.json")
    data = model_orientation(model_dir) if model_dir is not None else {}
    if config.exists():
        try:
            overrides = json.loads(config.read_text())
        except (OSError, ValueError) as exc:
            raise ValueError(f"{config}: {exc}") from exc
        if not isinstance(overrides, dict) or set(overrides) - {"top", "front"}:
            raise ValueError(f"{config}: expected an object containing only top and front")
        data = {**data, **overrides}
    result = {"top": top if top is not None else data.get("top", "+Z"),
              "front": front if front is not None else data.get("front", "-Y")}
    for face, axis in result.items():
        if not isinstance(axis, str) or axis.upper() not in AXES:
            raise ValueError(f"{config}: {face} must be one of {', '.join(AXES)}")
        result[face] = axis.upper()
    if result["top"][-1] == result["front"][-1]:
        raise ValueError(f"{config}: top and front must be perpendicular axes")
    return result


def face_vectors(orientation):
    top, front = (AXES[orientation[face]] for face in ("top", "front"))
    right = (top[1]*front[2] - top[2]*front[1],
             top[2]*front[0] - top[0]*front[2],
             top[0]*front[1] - top[1]*front[0])
    return {"top": top, "front": front, "right": right,
            "bottom": tuple(-v for v in top), "back": tuple(-v for v in front),
            "left": tuple(-v for v in right)}
