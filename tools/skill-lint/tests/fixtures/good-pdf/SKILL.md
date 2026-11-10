---
name: good-pdf
description: Extract text from PDF files, fill forms, and merge documents. Use when the user asks to process, split, extract, or merge PDFs.
license: Apache-2.0
---

# PDF processing

Follow these steps when handling PDFs.

1. Confirm the input files and the desired output format.
2. Run the bundled helper instead of writing extraction code:
   `python scripts/extract.py input.pdf`
3. Validate the result by checking page count and that extracted text is non-empty.
4. Present the output using the template in [examples](references/examples.md).

## Example

User: Extract text from report.pdf
Agent: run `python scripts/extract.py report.pdf` and return the text.
