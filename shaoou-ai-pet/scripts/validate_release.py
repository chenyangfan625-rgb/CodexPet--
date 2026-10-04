#!/usr/bin/env python3
"""Validate this offline, AI-generated unofficial fan-animation release."""
# SPDX-License-Identifier: MIT
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
GENERATED = {"checksums.json", "qa/release-validation.json"}
PRIVATE_PATTERNS = {
    "absolute user path": re.compile(rb"[A-Za-z]:[\\/]+(?:Users|Documents and Settings)[\\/]+", re.I),
    "absolute drive path": re.compile(rb"\b[A-Za-z]:[\\/]"),
    "private pet or session ID": re.compile(rb"\b(?:pet|upload_session)_[0-9a-f]{16,64}\b", re.I),
    "credential-shaped token": re.compile(rb"\b(?:sk-proj-|ghp_|github_pat_)[A-Za-z0-9_-]{16,}\b"),
    "signed URL parameter": re.compile(rb"(?:X-Amz-Signature|sig|token)=[A-Za-z0-9%+/]{12,}", re.I),
}


def release_files() -> dict[str, Path]:
    """List release files, excluding local tool caches and generated reports."""
    ignored_parts = {".git", "__pycache__", ".venv", "venv"}
    return {
        p.relative_to(ROOT).as_posix(): p
        for p in ROOT.rglob("*")
        if p.is_file() and not (set(p.relative_to(ROOT).parts) & ignored_parts)
        and p.suffix not in {".pyc", ".pyo"}
    }


def local_file(name: str) -> Path:
    """Resolve a manifest path within this release directory."""
    path = (ROOT / name).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Manifest path leaves the release directory")
    return path


def validate() -> dict:
    errors: list[str] = []
    files = release_files()
    inventory = json.loads((ROOT / "checksums.json").read_text(encoding="utf-8"))["files"]
    tracked = {name: path for name, path in files.items() if name not in GENERATED}
    for name in sorted(set(tracked) ^ set(inventory)):
        errors.append(f"Checksum inventory mismatch: {name}")
    for name, expected in inventory.items():
        path = tracked.get(name)
        if path is None:
            continue
        data = path.read_bytes()
        if len(data) != expected["bytes"] or hashlib.sha256(data).hexdigest() != expected["sha256"]:
            errors.append(f"File checksum or size mismatch: {name}")

    privacy_matches: list[dict] = []
    for name, path in sorted(files.items()):
        raw = path.read_bytes()
        # Check UTF-8/ASCII and common UTF-16 metadata without printing matched data.
        candidates = [raw, raw[::2], raw[1::2]]
        text_file = path.suffix.lower() in {".md", ".py", ".json", ".txt", ".yml", ".yaml"} or path.name in {"LICENSE", ".gitignore", ".gitattributes"}
        metadata = b""
        if path.suffix.lower() in {".png", ".webp", ".gif"}:
            with Image.open(path) as image:
                metadata = repr(image.info).encode("utf-8")
        for label, pattern in PRIVATE_PATTERNS.items():
            # A three-byte drive prefix can occur by chance in compressed media.
            # Search that broad pattern only in text and decoded image metadata.
            scan = candidates if label != "absolute drive path" or text_file else [metadata]
            if any(pattern.search(data) for data in scan):
                privacy_matches.append({"file": name, "category": label})
                errors.append(f"Privacy pattern detected in {name}: {label}")

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    layout = manifest["spritesheetLayout"]
    cols, rows = layout["columns"], layout["rows"]
    cw, ch = layout["cellWidth"], layout["cellHeight"]
    if (cols, rows, cw, ch) != (8, 11, 192, 208):
        errors.append("Unexpected v2 atlas geometry")
    with Image.open(local_file(manifest["spritesheetPath"])) as source:
        if source.format != "PNG" or source.mode != "RGBA":
            errors.append("Main atlas must be an RGBA PNG")
        png = source.convert("RGBA")
    if png.size != (cols * cw, rows * ch):
        errors.append("PNG dimensions do not match the grid")
    with Image.open(local_file(manifest["spritesheetWebpPath"])) as source:
        webp = source.convert("RGBA")
    # Compare all channels explicitly; alpha-only bbox checks miss RGB differences.
    webp_equal = png.size == webp.size and png.tobytes() == webp.tobytes()
    if not webp_equal:
        errors.append("PNG and WebP pixels differ")

    expected_states = ["idle", "running-right", "running-left", "waving", "jumping", "failed", "waiting", "running", "review"]
    expected_counts = [6, 8, 8, 4, 5, 8, 6, 6, 6]
    states = manifest["states"]
    if [s["name"] for s in states] != expected_states:
        errors.append("State order does not match the v2 atlas")
    used: set[tuple[int, int]] = set()
    gif_frames = 0
    for index, state in enumerate(states):
        row, count = state["rowIndex"], state["frameCount"]
        if index >= len(expected_counts) or row != index or count != expected_counts[index]:
            errors.append(f"Invalid row/frame count for {state['name']}")
        used.update((row, column) for column in range(count))
        with Image.open(local_file(state["previewPath"])) as gif:
            durations = []
            if gif.format != "GIF" or gif.size != (cw, ch) or gif.n_frames != count:
                errors.append(f"GIF geometry/frame mismatch: {state['name']}")
            if gif.info.get("loop") != 0:
                errors.append(f"GIF must loop: {state['name']}")
            for frame in range(gif.n_frames):
                gif.seek(frame)
                durations.append(gif.info.get("duration", 0))
            gif_frames += gif.n_frames
            if durations != state["previewDurationsMs"] or any(d <= 0 for d in durations):
                errors.append(f"GIF timing mismatch: {state['name']}")

    looks = manifest["lookDirections"]
    if len(looks) != 16 or layout["lookDirectionCount"] != 16:
        errors.append("Expected sixteen look directions")
    for index, look in enumerate(looks):
        if (look["degrees"], look["rowIndex"], look["columnIndex"]) != (index * 22.5, 9 + index // 8, index % 8):
            errors.append(f"Invalid look direction at index {index}")
        used.add((look["rowIndex"], look["columnIndex"]))
    alpha = png.getchannel("A")
    for row in range(rows):
        for col in range(cols):
            occupied = alpha.crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch)).getbbox() is not None
            if occupied != ((row, col) in used):
                errors.append(f"Cell occupancy mismatch at row {row}, column {col}")

    pixels = memoryview(png.tobytes())
    transparent_rgb = sum(1 for i in range(0, len(pixels), 4) if pixels[i+3] == 0 and any(pixels[i:i+3]))
    if transparent_rgb:
        errors.append("RGB residue in fully transparent pixels")
    mask = alpha.point(lambda a: 255 if a else 0)
    edge = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(3))).tobytes()
    green_edges = 0
    for offset, is_edge in enumerate(edge):
        if is_edge:
            i = offset * 4
            r, g, b, a = pixels[i:i+4]
            if a and g > 180 and g - r > 80 and g - b > 80:
                green_edges += 1
    if green_edges:
        errors.append("Saturated green pixels detected on silhouette edges")

    return {
        "ok": not errors,
        "releaseVersion": manifest["releaseVersion"],
        "aiGenerated": manifest["aiGenerated"],
        "unofficialFanWork": manifest["unofficialFanWork"],
        "checksummedFiles": len(inventory),
        "atlas": {"path": manifest["spritesheetPath"], "size": list(png.size), "mode": png.mode,
                  "usedCells": len(used), "unusedTransparentCells": cols * rows - len(used),
                  "animationFrames": sum(s["frameCount"] for s in states), "lookDirections": len(looks),
                  "transparentRgbResiduePixels": transparent_rgb, "saturatedGreenEdgePixels": green_edges,
                  "pngWebpPixelsIdentical": webp_equal},
        "stateGifFramesChecked": gif_frames,
        "privacyPatternMatches": privacy_matches,
        "scope": "Offline file/layout/timing checks and heuristic privacy/chroma scans; not third-party authorization or an artistic review.",
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", help="Optional JSON output path inside the release directory")
    args = parser.parse_args()
    try:
        report = validate()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Validation could not complete ({type(exc).__name__}). Check the release files and manifest.")
        return 2
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        path = local_file(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
