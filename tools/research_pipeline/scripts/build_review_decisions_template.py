import argparse
import json
from pathlib import Path
import site
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
VENDOR = ROOT / ".vendor"

if VENDOR.exists():
    site.addsitedir(str(VENDOR))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def build_template(review_queue_path: Path) -> dict:
    payload = json.loads(review_queue_path.read_text(encoding="utf-8"))
    decisions = []
    for bucket_name in ("promotion_review", "ontology_conflict", "merge_review", "contradiction_review"):
        for item in payload.get(bucket_name, []):
            decisions.append(
                {
                    "review_id": item["review_id"],
                    "review_target_id": item["review_target_id"],
                    "bucket": bucket_name,
                    "object_type": item["object_type"],
                    "status": "pending",
                    "modified_object": None,
                    "notes": "",
                }
            )
    return {"decisions": decisions}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a review decisions template from review_queue.json")
    parser.add_argument(
        "--review-queue",
        type=Path,
        default=ROOT / "output" / "review_queue.json",
        help="Path to review_queue.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "review_decisions.template.json",
        help="Path to write the review decisions template",
    )
    args = parser.parse_args(argv)

    template = build_template(args.review_queue)
    args.output.write_text(json.dumps(template, indent=2), encoding="utf-8")
    print(f"[review-template] wrote {len(template['decisions'])} decisions to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
