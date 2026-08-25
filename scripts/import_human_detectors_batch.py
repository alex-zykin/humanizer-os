#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "benchmarks" / "real-world-v1" / "candidates"
SOURCE_REPOSITORY = "jenna-russell/human_detectors"
SOURCE_COMMIT = "afcf03d14d2da4a038d8d0fafa5ec779dd858181"
SOURCE_FILE = "human_detectors.json"
SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    f"{SOURCE_REPOSITORY}/{SOURCE_COMMIT}/{SOURCE_FILE}"
)
WORD_RE = re.compile(r"[A-Za-z]+(?:['’\-][A-Za-z]+)*|\d+(?:[.,]\d+)?")
SIGNAL_TERMS = (
    "ai",
    "generic",
    "formulaic",
    "repetitive",
    "repetition",
    "conclusion",
    "introduction",
    "structure",
    "formal",
    "vocabulary",
    "phrasing",
    "polished",
    "verbose",
    "overly",
    "transition",
)


class ImportError(RuntimeError):
    pass


def _download_json(url: str) -> Any:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "raw.githubusercontent.com":
        raise ImportError(f"refusing unsupported dataset URL: {url}")

    # The pinned HTTPS host is checked above; noqa records that boundary.
    request = urllib.request.Request(  # noqa: S310
        url,
        headers={"User-Agent": "HumanizerOS benchmark importer"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
            payload = response.read()
    except OSError as exc:
        raise ImportError(f"failed to download {url}: {exc}") from exc
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ImportError(f"invalid JSON downloaded from {url}: {exc}") from exc


def _records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        values = payload.values()
    elif isinstance(payload, list):
        values = payload
    else:
        raise ImportError("dataset root must be an object or array")
    records = [value for value in values if isinstance(value, dict)]
    if not records:
        raise ImportError("dataset contains no record objects")
    return records


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def _slug(value: object) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).casefold()).strip("-")
    return slug or "unknown"


def _is_machine_generated(record: dict[str, Any]) -> bool:
    value = str(record.get("ground_truth", "")).casefold().replace("_", "-")
    return value in {"ai-generated", "machine-generated"}


def _annotations(record: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index in range(1, 6):
        raw = record.get(f"annotator_{index}")
        if not isinstance(raw, dict):
            continue
        comment = str(raw.get("comment", "")).strip()
        if not comment:
            continue
        rows.append(
            {
                "annotator": index,
                "guess": str(raw.get("guess", "")).strip(),
                "confidence": raw.get("confidence"),
                "comment": comment,
            }
        )
    return rows


def _signal_score(record: dict[str, Any]) -> int:
    comments = " ".join(row["comment"] for row in _annotations(record)).casefold()
    return sum(comments.count(term) for term in SIGNAL_TERMS)


def _candidate(record: dict[str, Any]) -> dict[str, Any] | None:
    if not _is_machine_generated(record):
        return None
    try:
        record_id = int(record.get("id"))
    except (TypeError, ValueError):
        return None
    if record_id == 4:
        return None

    article = str(record.get("article", "")).strip()
    model = str(record.get("generation_model", "")).strip()
    if not article or not model:
        return None
    words = _word_count(article)
    if not 100 <= words <= 2000:
        return None

    annotations = _annotations(record)
    digest = hashlib.sha256(article.encode("utf-8")).hexdigest()
    sample_id = f"human-detectors-{_slug(model)}-record-{record_id}"
    return {
        "sample_id": sample_id,
        "record_id": record_id,
        "prompt_id": record.get("prompt_id"),
        "model": model,
        "ground_truth": str(record.get("ground_truth", "")).strip(),
        "expert_majority_vote": str(record.get("expert_majority_vote", "")).strip(),
        "title": str(record.get("title", "")).strip(),
        "subtitle": str(record.get("sub-title", "")).strip(),
        "author": str(record.get("author", "")).strip(),
        "reference_source": str(record.get("source", "")).strip(),
        "publication_date": str(record.get("issue", "")).strip(),
        "section": str(record.get("section", "")).strip() or "Unspecified",
        "reference_url": str(record.get("link", "")).strip(),
        "article": article,
        "words": words,
        "sha256": digest,
        "signal_score": _signal_score(record),
        "annotations": annotations,
    }


def select_candidates(records: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    candidates = [item for record in records if (item := _candidate(record))]
    if len(candidates) < limit:
        raise ImportError(f"only {len(candidates)} eligible records found; requested {limit}")

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in candidates:
        groups[str(item["model"])].append(item)
    for items in groups.values():
        items.sort(
            key=lambda item: (
                -int(item["signal_score"]),
                abs(int(item["words"]) - 320),
                str(item["section"]).casefold(),
                int(item["record_id"]),
            )
        )

    selected: list[dict[str, Any]] = []
    used_sections: set[str] = set()
    model_names = sorted(groups, key=str.casefold)
    while len(selected) < limit:
        progressed = False
        for model in model_names:
            items = groups[model]
            if not items or len(selected) >= limit:
                continue
            index = next(
                (
                    idx
                    for idx, item in enumerate(items)
                    if str(item["section"]).casefold() not in used_sections
                ),
                0,
            )
            item = items.pop(index)
            selected.append(item)
            used_sections.add(str(item["section"]).casefold())
            progressed = True
        if not progressed:
            break

    if len(selected) != limit:
        raise ImportError(f"selection stopped at {len(selected)} records; requested {limit}")
    return selected


def _provenance(item: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# Provenance: {item['sample_id']}",
            "",
            "This directory contains a machine-generated record released by the Human Detectors "
            "research project. The paired human reference article is not reproduced here.",
            "",
            "## Dataset record",
            "",
            f"- repository: `{SOURCE_REPOSITORY}`",
            f"- pinned commit: `{SOURCE_COMMIT}`",
            f"- dataset file: `{SOURCE_FILE}`",
            f"- record id: `{item['record_id']}`",
            f"- prompt id: `{item['prompt_id']}`",
            f"- generation model: `{item['model']}`",
            f"- ground truth: `{item['ground_truth']}`",
            f"- expert majority vote: `{item['expert_majority_vote']}`",
            f"- reference title: {item['title']}",
            f"- reference source metadata: {item['reference_source']}",
            f"- reference section: {item['section']}",
            f"- reference publication date: {item['publication_date']}",
            f"- reference URL: {item['reference_url']}",
            f"- generated-text SHA-256: `{item['sha256']}`",
            f"- generated-text word count: {item['words']}",
            "- dataset repository license: MIT",
            "",
            "The `author`, `source`, title, and URL fields describe the human reference article "
            "used by the research dataset. They are not an authorship claim for `source.md`.",
            "",
            "Fact Guard checks consistency between a selected source and its HumanizerOS-guided "
            "rewrite. It does not verify the truth of claims in the generated source.",
            "",
        ]
    )


def _annotation_markdown(item: dict[str, Any]) -> str:
    lines = [f"# Human annotations: {item['sample_id']}", ""]
    if not item["annotations"]:
        lines.extend(["No free-form annotator comments were present in the record.", ""])
        return "\n".join(lines)
    for row in item["annotations"]:
        lines.extend(
            [
                f"## Annotator {row['annotator']}",
                "",
                f"- guess: `{row['guess']}`",
                f"- confidence: `{row['confidence']}`",
                "",
                str(row["comment"]),
                "",
            ]
        )
    return "\n".join(lines)


def write_candidates(selected: list[dict[str, Any]], output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    index: list[dict[str, Any]] = []
    for item in selected:
        directory = output / str(item["sample_id"])
        directory.mkdir()
        (directory / "source.md").write_text(str(item["article"]).strip() + "\n", encoding="utf-8")
        (directory / "provenance.md").write_text(_provenance(item), encoding="utf-8")
        (directory / "annotations.md").write_text(_annotation_markdown(item), encoding="utf-8")
        metadata = {key: value for key, value in item.items() if key != "article"}
        (directory / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        index.append(
            {
                "sample_id": item["sample_id"],
                "record_id": item["record_id"],
                "model": item["model"],
                "title": item["title"],
                "section": item["section"],
                "words": item["words"],
                "signal_score": item["signal_score"],
                "source_path": str((directory / "source.md").relative_to(ROOT)),
                "provenance_path": str((directory / "provenance.md").relative_to(ROOT)),
                "annotations_path": str((directory / "annotations.md").relative_to(ROOT)),
            }
        )

    payload = {
        "schema_version": 1,
        "source_repository": SOURCE_REPOSITORY,
        "source_commit": SOURCE_COMMIT,
        "selection": {
            "ground_truth": "machine-generated only",
            "record_id_excluded": 4,
            "word_range": [100, 2000],
            "strategy": "round-robin by generation model with section diversity",
        },
        "candidates": index,
    }
    (output / "index.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import a deterministic Human Detectors candidate batch."
    )
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")

    try:
        payload = _download_json(SOURCE_URL)
        selected = select_candidates(_records(payload), args.limit)
        write_candidates(selected, args.output.resolve())
    except ImportError as exc:
        parser.exit(2, f"import: {exc}\n")

    models = sorted({str(item["model"]) for item in selected}, key=str.casefold)
    sections = sorted({str(item["section"]) for item in selected}, key=str.casefold)
    print(
        f"Imported {len(selected)} candidates across {len(models)} models "
        f"and {len(sections)} sections"
    )
    print("Models: " + ", ".join(models))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
