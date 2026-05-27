"""Roboflow SAM3 segmentation for existing scientific figures."""

from __future__ import annotations

import argparse
import base64
import json
import os
import time
from pathlib import Path
from typing import Optional

import requests
from PIL import Image, ImageDraw, ImageFont


DEFAULT_ENDPOINT = "https://serverless.roboflow.com/sam3/concept_segment"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAM3 text-prompt segmentation via Roboflow.")
    parser.add_argument("--image", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--prompts",
        default=(
            "molecular node,reaction equation box,step label,legend,"
            "curved arrow,dashed side product bubble,circle,rectangle,arrow,text box"
        ),
    )
    parser.add_argument("--min-score", type=float, default=0.0)
    parser.add_argument("--min-area", type=int, default=900)
    parser.add_argument("--merge-threshold", type=float, default=0.65)
    parser.add_argument("--endpoint", default=os.environ.get("ROBOFLOW_API_URL", DEFAULT_ENDPOINT))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    api_key = os.environ.get("ROBOFLOW_API_KEY") or os.environ.get("API_KEY")
    if not api_key:
        raise RuntimeError("ROBOFLOW_API_KEY is required in the environment.")

    image_path = Path(args.image)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image = Image.open(image_path).convert("RGB")
    image_b64 = image_to_base64(image)
    prompts = [p.strip() for p in args.prompts.split(",") if p.strip()]

    all_boxes: list[dict] = []
    raw_responses: dict[str, dict] = {}
    for prompt in prompts:
        print(f"Roboflow SAM3 prompt: {prompt}")
        result = call_roboflow(
            endpoint=args.endpoint,
            image_base64=image_b64,
            prompt=prompt,
            api_key=api_key,
            min_score=args.min_score,
        )
        raw_responses[prompt] = result
        detections = extract_roboflow_detections(result, image.size)
        for det in detections:
            score = float(det.get("score") or 0.0)
            if score < args.min_score:
                continue
            det["prompt"] = prompt
            det["score"] = score
            all_boxes.append(det)

    boxes = label_boxes(all_boxes)
    boxes = [box for box in boxes if box_area(box) >= args.min_area]
    boxes = merge_overlapping_boxes(boxes, args.merge_threshold) if args.merge_threshold > 0 else boxes
    boxes = sorted(boxes, key=lambda b: (b["y1"], b["x1"]))
    for idx, box in enumerate(boxes, start=1):
        box["id"] = idx - 1
        box["label"] = f"<AF>{idx:02d}"

    samed_path = output_dir / "samed_roboflow.png"
    boxlib_path = output_dir / "boxlib_roboflow.json"
    raw_path = output_dir / "roboflow_raw.json"

    draw_samed(image, boxes, samed_path)
    crop_dir = output_dir / "icons"
    crop_dir.mkdir(parents=True, exist_ok=True)
    write_crops(image, boxes, crop_dir)
    boxlib = {
        "image_size": {"width": image.width, "height": image.height},
        "prompts_used": prompts,
        "min_area": args.min_area,
        "boxes": boxes,
        "no_icon_mode": len(boxes) == 0,
    }
    boxlib_path.write_text(json.dumps(boxlib, indent=2, ensure_ascii=False), encoding="utf-8")
    raw_path.write_text(json.dumps(raw_responses, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Detected boxes: {len(boxes)}")
    print(f"SAM overlay: {samed_path.resolve()}")
    print(f"Box library: {boxlib_path.resolve()}")
    print(f"Raw responses: {raw_path.resolve()}")
    return 0


def image_to_base64(image: Image.Image) -> str:
    from io import BytesIO

    buf = BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def call_roboflow(
    endpoint: str,
    image_base64: str,
    prompt: str,
    api_key: str,
    min_score: float,
) -> dict:
    payload = {
        "image": {"type": "base64", "value": image_base64},
        "prompts": [{"type": "text", "text": prompt}],
        "format": "polygon",
        "output_prob_thresh": min_score,
    }
    url = f"{endpoint}?api_key={api_key}"
    last_error: Optional[Exception] = None
    for attempt in range(1, 4):
        try:
            response = requests.post(url, json=payload, timeout=300)
            if response.status_code != 200:
                raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
            result = response.json()
            if isinstance(result, dict) and result.get("error"):
                raise RuntimeError(str(result["error"]))
            return result
        except Exception as exc:  # noqa: BLE001 - include HTTP and network errors.
            last_error = exc
            if attempt < 3:
                time.sleep(1.5 * attempt)
    message = str(last_error).replace(api_key, "***") if last_error else "unknown error"
    raise RuntimeError(f"Roboflow SAM3 request failed: {message}") from last_error


def extract_roboflow_detections(response_json: dict, image_size: tuple[int, int]) -> list[dict]:
    width, height = image_size
    detections: list[dict] = []
    prompt_results = response_json.get("prompt_results") if isinstance(response_json, dict) else None
    if not isinstance(prompt_results, list):
        return detections

    for prompt_result in prompt_results:
        predictions = prompt_result.get("predictions", []) if isinstance(prompt_result, dict) else []
        if not isinstance(predictions, list):
            continue
        for prediction in predictions:
            confidence = prediction.get("confidence") if isinstance(prediction, dict) else None
            masks = prediction.get("masks", []) if isinstance(prediction, dict) else []
            if not isinstance(masks, list):
                continue
            for mask in masks:
                points = flatten_points(mask)
                if not points:
                    continue
                xyxy = polygon_to_bbox(points, width, height)
                if not xyxy:
                    continue
                detections.append(
                    {"x1": xyxy[0], "y1": xyxy[1], "x2": xyxy[2], "y2": xyxy[3], "score": confidence}
                )
    return detections


def flatten_points(mask) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    if not isinstance(mask, list):
        return points
    stack = list(mask)
    while stack:
        item = stack.pop()
        if isinstance(item, (list, tuple)) and len(item) >= 2 and all(
            isinstance(v, (int, float)) for v in item[:2]
        ):
            points.append((float(item[0]), float(item[1])))
        elif isinstance(item, (list, tuple)):
            stack.extend(item)
    return points


def polygon_to_bbox(points: list[tuple[float, float]], width: int, height: int) -> tuple[int, int, int, int] | None:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x1 = max(0, min(width, int(round(min(xs)))))
    y1 = max(0, min(height, int(round(min(ys)))))
    x2 = max(0, min(width, int(round(max(xs)))))
    y2 = max(0, min(height, int(round(max(ys)))))
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2


def label_boxes(boxes: list[dict]) -> list[dict]:
    labeled = []
    for idx, box in enumerate(boxes):
        labeled.append(
            {
                "id": idx,
                "label": f"<AF>{idx + 1:02d}",
                "x1": int(box["x1"]),
                "y1": int(box["y1"]),
                "x2": int(box["x2"]),
                "y2": int(box["y2"]),
                "score": float(box.get("score") or 0.0),
                "prompt": box.get("prompt", ""),
            }
        )
    return labeled


def merge_overlapping_boxes(boxes: list[dict], threshold: float) -> list[dict]:
    merged: list[dict] = []
    for box in boxes:
        target = None
        for existing in merged:
            if overlap_ratio(box, existing) >= threshold:
                target = existing
                break
        if target is None:
            merged.append(dict(box))
            continue
        target["x1"] = min(target["x1"], box["x1"])
        target["y1"] = min(target["y1"], box["y1"])
        target["x2"] = max(target["x2"], box["x2"])
        target["y2"] = max(target["y2"], box["y2"])
        target["score"] = max(target.get("score", 0.0), box.get("score", 0.0))
        prompts = set(str(target.get("prompt", "")).split("|")) | {str(box.get("prompt", ""))}
        target["prompt"] = "|".join(sorted(p for p in prompts if p))
    return merged


def box_area(box: dict) -> int:
    return max(0, int(box["x2"]) - int(box["x1"])) * max(0, int(box["y2"]) - int(box["y1"]))


def overlap_ratio(a: dict, b: dict) -> float:
    ix1 = max(a["x1"], b["x1"])
    iy1 = max(a["y1"], b["y1"])
    ix2 = min(a["x2"], b["x2"])
    iy2 = min(a["y2"], b["y2"])
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0
    intersection = (ix2 - ix1) * (iy2 - iy1)
    area_a = max(1, (a["x2"] - a["x1"]) * (a["y2"] - a["y1"]))
    area_b = max(1, (b["x2"] - b["x1"]) * (b["y2"] - b["y1"]))
    return intersection / min(area_a, area_b)


def draw_samed(image: Image.Image, boxes: list[dict], output_path: Path) -> None:
    samed = image.convert("RGBA")
    draw = ImageDraw.Draw(samed, "RGBA")
    try:
        font = ImageFont.truetype("arial.ttf", 26)
    except OSError:
        font = ImageFont.load_default()
    for box in boxes:
        x1, y1, x2, y2 = box["x1"], box["y1"], box["x2"], box["y2"]
        label = box["label"]
        draw.rectangle([x1, y1, x2, y2], fill=(128, 128, 128, 180), outline=(0, 0, 0, 255), width=3)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        draw.text((cx, cy), label, fill=(255, 255, 255, 255), anchor="mm", font=font)
    samed.save(output_path)


def write_crops(image: Image.Image, boxes: list[dict], output_dir: Path) -> None:
    for box in boxes:
        crop = image.crop((box["x1"], box["y1"], box["x2"], box["y2"]))
        safe_label = box["label"].replace("<", "").replace(">", "")
        crop.save(output_dir / f"icon_{safe_label}.png")


if __name__ == "__main__":
    raise SystemExit(main())
