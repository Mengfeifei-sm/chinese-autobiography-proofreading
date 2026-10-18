# Safety, thresholds, and troubleshooting

## 1. Never do these

- Do not call cloud OCR, LLM APIs, web search, or upload student content.
- Do not edit `input/` files in place.
- Do not auto-edit student ID, name, or sensitive sentences.
- Do not apply all `待人工确认` items in bulk.
- Do not lower OCR thresholds just to force more rewrites.
- Do not kill WPS/Word to unlock a file unless the user explicitly asks and unsaved work is ruled out.
- Do not delete old output/reports without confirmation.

## 2. OCR thresholds

Config: `config.json → ocr`

| Key | Default | Meaning |
| --- | --- | --- |
| `min_confidence` | 0.85 | OCR line confidence; below is report-only |
| `match_threshold` | 0.80 | Word/OCR similarity |
| `max_auto_rewrite_chars` | 160 | longer paragraphs are report-only |
| `max_auto_change_chars` | 6 | maximum character changes for a rewrite |
| `require_lexical_improvement` | true | requires local `jieba` dictionary to prove OCR is better |
| `insert_ocr_for_image_paragraphs` | true | insert after image/object paragraph |
| `insert_ocr_for_empty_paragraphs` | false | do not fill form blank paragraphs by default |

Lowering `min_confidence` or `match_threshold` can inject OCR errors such as:

- 军训 → 军到
- 大概 → 大相既
- 做事 → 微事

Only change thresholds after explicit user request, and rerun tests.

## 3. WPS/Word file lock

If `output\<name>.docx` is open, the tool saves:

```text
output\<name>_已校对.docx
```

The student report records this fallback in `待人工确认`. To restore the standard name:

1. Close the document only if it is saved / no unsaved edits.
2. Copy or rename `_已校对.docx` to the standard name.
3. Update report paths if the tool is not rerun.

Do not force-delete a locked file.

## 4. OCR engine missing

Check:

```powershell
python -c "import rapidocr_onnxruntime; print('OCR OK')"
```

Install:

```powershell
python -m pip install -r requirements.txt
```

Without OCR, the tool does not crash; it renders pages and reports that OCR is unavailable.

## 5. First run is slow

RapidOCR CPU inference is roughly 2–5 seconds/page. ~200 pages can take 10–20 minutes.

- Keep the window open.
- Later runs use `ocr_cache` (keyed by PDF path, page, engine, DPI, language, file stamp).
- `--no-ocr` is the fast format-only mode.
- `--no-render` skips page images and therefore also skips OCR.

## 6. Preserve the batch boundary

Use one folder per class/term:

```text
D:\自传\2566班\input
D:\自传\2566班\output
D:\自传\2566班\reports
```

Do not append a new class to an old `input` folder; old students will be processed again and reports will be overwritten.

## 7. When output looks wrong

1. Open the pairing report and the student report.
2. Check OCR status and page images.
3. If the issue is formatting, inspect title/body classification.
4. If the issue is content, use `待人工确认` / OCR text; do not ask the tool to "guess".
5. If the tool itself needs changing, edit source modules and run `python test/run_tests.py`.

## 8. Validation commands

```powershell
python test/run_tests.py
```

```powershell
python skills\chinese-autobiography-proofreading\scripts\check_outputs.py `
  --input .\input `
  --output .\output `
  --reports .\reports
```

`check_outputs.py` is read-only. It does not modify Word/report files.
