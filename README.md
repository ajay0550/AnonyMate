# AnonyMate: PII Detection and Redaction Tool

AnonyMate is a comprehensive tool designed to detect and redact Personally Identifiable Information (PII) from various document formats, including images and PDFs. This repository encompasses two primary scripts:

- **`octopii.py`**: Scans documents to detect PII and generates a report (`output.json`).
- **`redact.py`**: Utilizes the detection report to redact identified PII from the original documents.

## Features

- **PII Detection**: Identifies sensitive information such as:
  - Names
  - Addresses
  - Phone numbers
  - Email addresses
  - Identification numbers

- **PII Redaction**: Obscures detected PII in documents to ensure data privacy.

- **Supported Formats**:
  - Images: JPG, PNG
  - Documents: PDF, DOCX, TXT


