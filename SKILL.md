---
name: chinese-autobiography-proofreading
description: Batch-proofread Chinese handwritten autobiography scans (PDF) against AI-transcribed Word documents with fully offline OCR, safe formatting, and page-linked reports. Use for 自传/手写/扫描件/OCR/Word 校对/PDF 对照/批量校对/新生自传.
---

# Chinese Autobiography OCR Proofreading

Use this skill when the task is to process one or more students' scanned autobiography PDFs plus AI-transcribed `.docx` files into corrected Word documents with local OCR, page images, and review reports.

This skill wraps the existing `autoproof` project. It does not reimplement OCR or edit Word directly.

## Critical safety rules

Read these before running or changing anything:

1. **Fully offline.** Never call cloud OCR, LLM APIs, web search, or upload PDF/DOCX content. OCR runs through local RapidOCR/ONNX Runtime.
2. **Never modify `input/` source files.** Outputs go to `output/`; reports go to `reports/`.
3. **Do not mix classes/terms.** Keep one class in one input/output/reports set. If new files are added, use a new class folder rather than appending to an old batch.
4. **Never auto-edit student ID or name.** OCR differences for 学号/姓名 are report-only.
5. **Never auto-edit sensitive sentences.** 霸凌、家暴、虐待、自杀、抑郁、轻生 etc. are report-only.
6. **Do not lower OCR thresholds just to make the tool change more text.** The tool deliberately rejects OCR text that is not demonstrably better than Word. `--ocr-conf` below the configured default requires explicit user approval.
7. **Do not bulk-apply report "OCR疑点"/"待人工确认" items.** They are human-decisions.
8. **Do not kill WPS/Word to unlock a file.** If a target docx is open, the tool saves `<name>_已校对.docx` and records it. Close the app only after confirming the document has no unsaved changes.
9. **Do not delete old outputs/reports without asking.** Use a new directory or confirm what should be replaced.

## Locate the project

Set one of:

```powershell
$env:AUTOPROOF_PROJECT = "C:\path\to\autoproof"
```

or pass `-ProjectRoot` to the scripts. The project must contain `main.py`, `config.json`, `autoproof/`, and `requirements.txt`.

Verify dependencies:

```powershell
python -c "import docx, pymupdf, rapidocr_onnxruntime, jieba; print('autoproof dependencies OK')"
```

If missing:

```powershell
python -m pip install -r requirements.txt
```

## Workflow

### 1. Inspect inputs first

Expected naming (not mandatory, but recommended):

- `20250001 姓名.pdf` + `20250001 姓名.docx`
- `20250001+姓名.pdf` + `20250001+姓名.docx`
- only Word, or only PDF, is also supported.

Check that PDF and Word files are paired by ID/name. Do not rename originals unless the user asks.

### 2. Trial run

Run 3 students first when the user has not already validated the batch:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_autoproof.ps1 `
  -ProjectRoot $env:AUTOPROOF_PROJECT `
  -InputDir "$env:AUTOPROOF_PROJECT\input" `
  -OutputDir "$env:AUTOPROOF_PROJECT\output" `
  -ReportsDir "$env:AUTOPROOF_PROJECT\reports" `
  -Limit 3
```

Inspect `reports\pairing_report.txt` and one student report before the full run. Check title/body formatting and whether OCR rewrites are acceptable.

### 3. Full run

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_autoproof.ps1 `
  -ProjectRoot $env:AUTOPROOF_PROJECT `
  -InputDir "$env:AUTOPROOF_PROJECT\input" `
  -OutputDir "$env:AUTOPROOF_PROJECT\output" `
  -ReportsDir "$env:AUTOPROOF_PROJECT\reports"
```

Or invoke directly:

```powershell
python main.py --input ".\input" --output ".\output" --reports ".\reports"
```

First OCR pass can take 10–20 minutes for ~200 pages on CPU. Do not interrupt. Later runs use `ocr_cache`.

For a fast format-only pass:

```powershell
... -NoOcr
```

`-NoOcr` disables only OCR; page rendering and existing punctuation/typo fixes still run.

### 4. Validate the run

```powershell
python .\scripts\check_outputs.py `
  --input "$env:AUTOPROOF_PROJECT\input" `
  --output "$env:AUTOPROOF_PROJECT\output" `
  --reports "$env:AUTOPROOF_PROJECT\reports"
```

The script prints a compact JSON summary and exits non-zero if a generated `.docx` cannot be opened or counts are inconsistent. Do not paste the full report set into chat.

### 5. Optional class audit summary

```powershell
python tools\class_audit.py --reports "$env:AUTOPROOF_PROJECT\reports" --output "$env:AUTOPROOF_PROJECT\reports"
```

This creates `reports/class_audit.md` and `class_audit.csv`. Use it to find students needing attention; do not dump the whole table into chat.

### 6. Report back to the user

Report only bounded, useful facts:

- students found / paired / missing;
- latest Word count;
- OCR successes, OCR pages, OCR rewrites/insertions;
- pending review count and sensitive count;
- any failed or fallback files;
- paths to `pairing_report.txt` and one representative student report.

Do not enumerate every auto-fix or every student unless asked.

## Reading the outputs

- `output\<name>.docx` — final Word for the teacher.
- `reports\pairing_report.txt` — class-level pairing/OCR/identity status.
- `reports\<id>_<name>\<id>_<name>.md` — per-student review report.
- `reports\<id>_<name>\pages\page_01.jpg` — PDF page images.
- `reports\<id>_<name>\ocr\page_01.txt` — page OCR text.
- `reports\<id>_<name>\ocr\page_01.json` — OCR blocks with confidence/bbox.
- `reports\<id>_<name>\ocr\summary.txt` — all OCR text.

See `references/report-reading.md` for what each report section means.

## Hard cases

- **PDF unreadable/encrypted:** report only; do not crash or retry with network OCR.
- **No OCR engine:** tool degrades to page-image mode; report the install hint.
- **Word file open in WPS/Word:** latest output is `*_已校对.docx`; report it. If the user wants the standard filename, only close the document after verifying it is saved.
- **Suspicious OCR rewrite:** do not "fix" it with a language model. Treat as human-review content.
- **Many pending items:** summarize counts and point to the report; do not dump all items.

See `references/safety-and-troubleshooting.md` for details.

## Do not use this skill for

- OCR-free ordinary document formatting unrelated to student autobiographies;
- cloud OCR or model-based rewriting;
- editing original PDFs/DOCX in place;
- deciding sensitive-content handling on the user's behalf.

## References

- `references/report-reading.md` — report sections and how to act on them.
- `references/safety-and-troubleshooting.md` — thresholds, WPS locks, OCR limits, install failures.
- `scripts/run_autoproof.ps1` — safe wrapper with no deletions.
- `scripts/check_outputs.py` — read-only output validator.
