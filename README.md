# AnonyMate - PII Detection & Redaction Tool

**AnonyMate** is a Python-based application that detects and redacts Personally Identifiable Information (PII) from documents such as images and PDFs. It uses Optical Character Recognition (OCR) and rule-based techniques to identify and obscure sensitive data such as ID numbers, phone numbers, email addresses, addresses, and faces.

## Features

- Detects PII in image and PDF files  
- Redacts (masks) identified PII using OCR  
- Utilizes regular expressions, keyword matching, and face detection  
- Generates a structured output file (`output.json`) containing the detection results  
- Includes a modern Tkinter-based GUI with preview functionality  

## Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

# Additional Installation
Tesseract OCR is required.

Windows: Download and install from Tesseract OCR GitHub

Linux:
```
sudo apt install tesseract-ocr
```
Ensure Tesseract is added to your system PATH and the tessdata folder contains necessary languages.


## Project Structure

AnonyMate/
├── octopii.py           # PII detection script
├── redact.py            # Redacts detected PII
├── octopii_gui.py       # User-friendly GUI interface
├── definitions.json     # Keyword definitions for classification
├── output.json          # Output file with detection results
├── image_utils.py       # OCR and image processing
├── text_utils.py        # Regex and text-based scanning
├── file_utils.py        # File handling helpers
├── requirements.txt     # Dependency list

## How to Use
1. Launch the GUI

```
python octopii_gui.py

```

2. Upload a File
Upload an image or PDF file using the GUI.

3. Scan for PII
Click Scan for PII. Detected data will be shown in the GUI and saved to output.json.

4. Redact PII
Click Redact PII. A new image will be generated with sensitive data blacked out.

5. View Results
Preview both original and redacted images in the GUI.

## Notes

Multiple languages are supported via Tesseract (e.g. English, Hindi, Tamil, etc.). Ensure the corresponding .traineddata files exist in your Tesseract installation's tessdata folder.

Webhook support: Provide a webhook URL to receive the output as JSON remotely.

