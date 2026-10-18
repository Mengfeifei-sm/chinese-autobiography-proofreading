# chinese-autobiography-proofreading

A reusable Agent Skill for offline OCR and Word proofreading of Chinese handwritten autobiography scans.

This repository contains **only the skill** — no student PDFs, DOCX files, OCR text, page images, or reports.

The skill wraps an existing local project (the `autoproof` tool) that contains:

```text
main.py
config.json
autoproof/
requirements.txt
```

## What it does

- Runs a fully local OCR + Word proofreading batch.
- Pairs scanned PDFs with AI-transcribed `.docx` files by student ID and name.
- Uses RapidOCR/ONNX Runtime locally; no cloud OCR, no API, no upload.
- Keeps student IDs, names, sensitive content, and low-confidence OCR report-only.
- Produces corrected Word files, per-student review reports, page images, and OCR text.
- Provides a safe PowerShell runner and a read-only output validator.
- Prevents an agent from dumping every report or force-applying uncertain changes.

## Install

### Codex

Copy or clone this repository into the Codex skills directory:

```powershell
git clone https://github.com/<your-account>/chinese-autobiography-proofreading.git `
  "$env:USERPROFILE\.codex\skills\chinese-autobiography-proofreading"
```

Or copy the folder manually to:

```text
%USERPROFILE%\.codex\skills\chinese-autobiography-proofreading\
```

Other agent runtimes: place this folder in their documented skills directory. The entry file is `SKILL.md`.

## Configure the autoproof project

```powershell
$env:AUTOPROOF_PROJECT = "C:\path\to\autoproof"
```

The project must be installed with its own dependencies:

```powershell
python -m pip install -r "$env:AUTOPROOF_PROJECT\requirements.txt"
```

## Use

Trial run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_autoproof.ps1 `
  -ProjectRoot $env:AUTOPROOF_PROJECT `
  -InputDir "$env:AUTOPROOF_PROJECT\input" `
  -OutputDir "$env:AUTOPROOF_PROJECT\output" `
  -ReportsDir "$env:AUTOPROOF_PROJECT\reports" `
  -Limit 3
```

Full run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_autoproof.ps1 `
  -ProjectRoot $env:AUTOPROOF_PROJECT
```

Format-only, no OCR:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_autoproof.ps1 `
  -ProjectRoot $env:AUTOPROOF_PROJECT -NoOcr
```

Validate outputs:

```powershell
python .\scripts\check_outputs.py `
  --input "$env:AUTOPROOF_PROJECT\input" `
  --output "$env:AUTOPROOF_PROJECT\output" `
  --reports "$env:AUTOPROOF_PROJECT\reports"
```

Class audit (provided by the project):

```powershell
python "$env:AUTOPROOF_PROJECT\tools\class_audit.py" `
  --reports "$env:AUTOPROOF_PROJECT\reports" `
  --output "$env:AUTOPROOF_PROJECT\reports"
```

## Safety rules

- Fully offline; never use cloud OCR or LLM APIs.
- Never modify `input/` source files.
- Never auto-edit student ID, name, or sensitive sentences.
- Do not bulk-apply "待人工确认" items.
- Do not lower OCR thresholds just to force more rewrites.
- Do not kill WPS/Word to unlock a file.
- Do not delete old outputs/reports without confirmation.
- Use a new folder per class/term.

See `references/safety-and-troubleshooting.md` for details.

## Contents

```text
SKILL.md
scripts/run_autoproof.ps1
scripts/check_outputs.py
references/report-reading.md
references/safety-and-troubleshooting.md
requirements.txt
```

## Requirements

The skill assumes Python 3.10+ and the autoproof project dependencies:

- python-docx
- PyMuPDF
- rapidocr-onnxruntime
- jieba

`requirements.txt` is provided for convenience; install it into the environment used by the autoproof project.

## License

No license is granted by default. Add a license if you intend to distribute this skill beyond your organization.
