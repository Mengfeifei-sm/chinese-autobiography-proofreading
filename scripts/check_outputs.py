#!/usr/bin/env python3
"""Read-only validation for an autoproof batch output.

Usage:
    python check_outputs.py --input PATH --output PATH --reports PATH
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from docx import Document
except Exception:  # pragma: no cover
    Document = None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def count(report: str, label: str) -> int | None:
    match = re.search(rf"{re.escape(label)}\s*:\s*(\d+)", report)
    return int(match.group(1)) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate autoproof outputs without modifying them.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--reports", required=True)
    parser.add_argument("--json", action="store_true", help="Print JSON (default). Kept for compatibility.")
    args = parser.parse_args()

    input_dir = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()
    reports_dir = Path(args.reports).expanduser().resolve()
    pairing_path = reports_dir / "pairing_report.txt"

    result: dict[str, object] = {
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "reports_dir": str(reports_dir),
        "input_pdfs": len(list(input_dir.rglob("*.pdf"))) if input_dir.exists() else 0,
        "input_docx": len(list(input_dir.rglob("*.docx"))) if input_dir.exists() else 0,
        "output_docx": 0,
        "fallback_docx": [],
        "student_reports": 0,
        "ocr_page_txt": 0,
        "ocr_page_json": 0,
        "ocr_summary": 0,
        "page_images": 0,
        "unreadable_docx": [],
        "missing_outputs": [],
        "missing_reports": [],
        "pairing": {},
        "errors": [],
        "ok": False,
    }

    if not pairing_path.exists():
        result["errors"].append(f"缺少配对报告：{pairing_path}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    report_text = read_text(pairing_path)
    for label, key in (
        ("PDF 文件数", "pdf_files"),
        ("Word 文件数", "docx_files"),
        ("成功配对", "paired"),
        ("缺 PDF", "missing_pdf"),
        ("缺 Word", "missing_word"),
        ("已生成校对稿", "generated"),
        ("处理失败", "failed"),
        ("OCR 成功", "ocr_success"),
        ("OCR 不可用", "ocr_unavailable"),
    ):
        value = count(report_text, label)
        if value is not None:
            result["pairing"][key] = value

    docx_files = sorted(output_dir.glob("*.docx")) if output_dir.exists() else []
    result["output_docx"] = len(docx_files)
    result["fallback_docx"] = sorted(path.name for path in docx_files if "_已校对" in path.stem)

    if Document is not None:
        for path in docx_files:
            try:
                Document(str(path))
            except Exception as exc:
                result["unreadable_docx"].append({"path": str(path), "error": str(exc)})

    report_files = sorted(reports_dir.glob("*/*.md")) if reports_dir.exists() else []
    result["student_reports"] = len(report_files)
    if reports_dir.exists():
        result["ocr_page_txt"] = len(list(reports_dir.rglob("ocr/page_*.txt")))
        result["ocr_page_json"] = len(list(reports_dir.rglob("ocr/page_*.json")))
        result["ocr_summary"] = len(list(reports_dir.rglob("ocr/summary.txt")))
        result["page_images"] = len(list(reports_dir.rglob("pages/page_*.jpg")))

    for match in re.finditer(r"^\s*输出\s*:\s*(.+)$", report_text, re.MULTILINE):
        output_path = Path(match.group(1).strip())
        if not output_path.exists():
            result["missing_outputs"].append(str(output_path))
    for match in re.finditer(r"^\s*报告\s*:\s*(.+)$", report_text, re.MULTILINE):
        report_path = Path(match.group(1).strip())
        if not report_path.exists():
            result["missing_reports"].append(str(report_path))

    pairing = result["pairing"]
    expected_outputs = pairing.get("generated")
    if expected_outputs is not None and len(docx_files) < int(expected_outputs):
        result["errors"].append(f"配对报告称生成 {expected_outputs} 份，但 output 只有 {len(docx_files)} 份 docx")
    if result["missing_outputs"]:
        result["errors"].append(f"{len(result['missing_outputs'])} 个报告中的输出路径不存在")
    if result["missing_reports"]:
        result["errors"].append(f"{len(result['missing_reports'])} 个报告路径不存在")
    if result["unreadable_docx"]:
        result["errors"].append(f"{len(result['unreadable_docx'])} 个 docx 无法打开")
    if len(report_files) < len(docx_files) and pairing.get("docx_files"):
        result["errors"].append("学生报告数量少于 Word 数量")

    result["ok"] = not result["errors"]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
