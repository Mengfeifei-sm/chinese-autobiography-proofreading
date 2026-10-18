# Reading autoproof reports

Use this reference only after a batch has finished. Do not dump all reports into chat.

## 1. Start with `reports/pairing_report.txt`

Check, in order:

1. `PDF 文件数` / `Word 文件数` — did the scanner see all files?
2. `成功配对` / `缺 PDF` / `缺 Word` — any missing partner?
3. `处理失败` — any document-level failure?
4. `OCR 成功` / `OCR 不可用` — was OCR active?
5. Per-student block:
   - `Word 正文` vs `OCR 文本` vs `文件名`;
   - `一致性`;
   - `输出`;
   - `OCR 状态`;
   - `提示`.

If the batch has a fallback file (`*_已校对.docx`), the report's `输出` path points to the real latest file. Do not assume the standard filename is latest.

## 2. Per-student report

Path:

```text
reports/<student_id>_<name>/<student_id>_<name>.md
```

Sections:

| Section | What to do |
| --- | --- |
| 一、处理概况 | Check OCR state, counts, output path, processing time. |
| 二、文件配对与学号姓名核对 | Compare filename / Word / PDF text / OCR. Never auto-change ID/name. |
| 三、自动修正清单 | Safe punctuation/spacing/typo changes. Spot-check a few; all are logged. |
| 四、自动排版说明 | Body/title formatting and line-merge summary. |
| 五、OCR 参考与自动改写 | Review OCR rewrites, OCR insertions, OCR doubts. |
| 六、待人工确认清单 | Actual teacher work list. Prioritize 学号/姓名, 图片, OCR 疑点, sensitive. |
| 七、敏感内容提醒 | Handle according to school policy; source is shown as Word/OCR/PDF text. |
| 八、PDF 处理与页码定位 | Page images and error notes. |

## 3. What OCR auto rewrites mean

- `OCR 自动改写` passed: high similarity, high confidence, no ID/name, no sensitive term, length/change limits, and local dictionary validation.
- `OCR 疑点` means the tool found OCR text but refused to write it. This is not a tool failure; it is a human decision.
- `OCR 补录` means text was added after an image/object (or, if explicitly enabled, an empty paragraph). The original object is preserved.
- `OCR 补录候选不唯一` means the tool refused to guess where to insert text.

## 4. How to verify a suspicious paragraph

1. Use the report `PDF 页码` / OCR page link.
2. Open `reports/<student>/pages/page_XX.jpg`.
3. Compare the Word paragraph with `reports/<student>/ocr/page_XX.txt`.
4. Edit the Word manually only after confirmation.

Do not use a language model or web OCR to "fix" an uncertain OCR paragraph.

## 5. Summarize to the user

Bounded summary template:

```text
已处理 N 名学生：配对成功 X，缺 PDF Y，缺 Word Z，失败 F。
OCR 成功 A 份（B 页），自动改写 C 处，补录 D 处。
待人工确认 E 项，敏感提醒 F 处。
最新 Word 在 output/；先看 reports/pairing_report.txt。
```

Do not list all 49 student paths unless the user asks.
