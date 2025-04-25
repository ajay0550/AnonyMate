AnonyMate - PII Detection & Redaction Tool
AnonyMate is a Python-based application that detects and redacts Personally Identifiable Information (PII) from documents such as images and PDFs. It uses Optical Character Recognition (OCR) and rule-based techniques to identify and obscure sensitive data such as ID numbers, phone numbers, email addresses, addresses, and faces.

Features
Detects PII in image and PDF files

Redacts (masks) identified PII using OCR

Utilizes regular expressions, keyword matching, and face detection

Generates a structured output file (output.json) containing the detection results

Includes a modern Tkinter-based GUI with preview functionality

Dependencies
Before running the project, install the required Python packages:

bash
Copy
Edit
pip install -r requirements.txt
Additional Installation
Tesseract OCR is required for text extraction.

Windows: Download from Tesseract OCR GitHub

Linux:

bash
Copy
Edit
sudo apt install tesseract-ocr
Ensure Tesseract is properly added to your system PATH and its tessdata directory contains the required language files.

Project Structure
graphql
Copy
Edit
AnonyMate/
│
├── octopii.py           # Main PII detection logic
├── redact.py            # Redacts PII from documents based on detection results
├── octopii_gui.py       # GUI interface for file upload, scan, and preview
├── definitions.json     # Rule definitions for PII classification
├── output.json          # Generated output containing detected PII
├── image_utils.py       # OCR and image handling helpers
├── text_utils.py        # Text processing and regex matching
├── file_utils.py        # File handling utilities
├── requirements.txt     # Required Python packages
How to Use
Step 1: Launch the GUI
bash
Copy
Edit
python octopii_gui.py
Step 2: Upload File
Choose a document (image or PDF) from your system.

Step 3: Scan for PII
Click the "Scan for PII" button to detect sensitive information. Results are stored in output.json and displayed in the interface.

Step 4: Redact PII
Click the "Redact PII" button. The application will generate and display the redacted version of the uploaded file.

Step 5: View Results
Both original and redacted images are previewed in the GUI. Redacted files are saved in the same directory.

Notes
Multiple languages are supported for OCR. Ensure the corresponding .traineddata files are available in your Tesseract installation's tessdata folder.

You can optionally use the webhook feature by providing a URL in the GUI. This allows results to be pushed to an external server.

Contributors
[Your Name]

[Teammate's Name]
