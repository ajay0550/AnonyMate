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
 
    
Usage
Installing dependencies
Install all dependencies via pip install -r requirements.txt.
Install the Tesseract helper locally via sudo apt install tesseract-ocr -y on Ubuntu or sudo pacman -Syu tesseract on Arch Linux.
Install Spacy language definitions locally via python -m spacy download en_core_web_sm.
Once you've installed the above, you're all set.

Running
To run Octopii, type

python3 octopii.py <location to scan>
where <location to scan> is a file or a directory.

Octopii currently supports local scanning via filesystem path, S3 URLs and Apache open directory listings. You can also provide individual image URLs or files as an argument.

Example
We've provided a dummy-pii/ folder containing sample PII for you to test Octopii with. Pass it as an argument and you'll get the following output

owais@artemis ~ $ python3 octopii.py dummy-pii/

Searching for PII in dummy-pii/dummy-drivers-license-nebraska-us.jpg
{
    "file_path": "dummy-pii/dummy-drivers-license-nebraska-us.jpg",
    "pii_class": "Nebraska Driver's License",
    "country_of_origin": "United States",
    "faces": 1,
    "identifiers": [],
    "emails": [],
    "phone_numbers": [
        "4000002170"
    ],
    "addresses": [
        "Nebraska"
    ]
}

Searching for PII in dummy-pii/dummy-PAN-India.jpg
{
    "file_path": "dummy-pii/dummy-PAN-India.jpg",
    "pii_class": "Permanent Account Number",
    "country_of_origin": "India",
    "faces": 0,
    "identifiers": [],
    "emails": [],
    "phone_numbers": [],
    "addresses": [
        "INDIA"
    ]
}

...
A file named output.txt is created, containing output from the tool. This file is appended to sequentially in real-time.

Working
Octopii uses Tesseract for Optical Character Recognition (OCR) and NLTK for Natural Language Processing (NLP) to detect for strings of personal identifiable information. This is done via the following steps:

1. Input and importing
Octopii scans for images (jpg and png) and documents (pdf, doc, txt etc). It supports 3 sources:

Amazon Simple Storage Service (S3): traverses the XML from S3 container URLs
Open directory listing: traverses Apache open directory listings and scans for files
Local filesystem: can access files and folders within UNIX-like filesystems (macOS and Linux-based operating systems)
Images are detected via Python Imaging Library (PIL) and are opened with OpenCV. PDFs are converted into a list of images and are scanned via OCR. Text-based file types are read into strings and are scanned without OCR.

2. Face detection
A binary classification image detection technique - known as a "Haar cascade" - is used to detect faces within images. A pre-trained cascade model is supplied in this repo, which contains cascade data for OpenCV to use. Multiple faces can be detected within the same PII image, and the number of faces detected is returned.

3. Cleaning image and reading text
Images are then "cleaned" for text extraction with the following image transformation steps:

Auto-rotation
Grayscaling
Monochrome
Mean threshold
Gaussian threshold
3x Deskewing
Image filtering illustration

Since these steps strip away image data (including colors in photographs), this image cleaning process occurs after attempting face detection.

4. Optical Character Recognition (OCR)
Tesseract is used to grab all text strings from an image/file. It is then tokenized into a list of strings, split by newline characters ('\n') and spaces (' '). Garbled text, such as null strings and single characters are discarded from this list, resulting in an 'intelligible' list of potential words.

This list of words is then fed into a similarity checker function. This function uses Gestalt pattern matching to compare each word extracted from the PII document with a list of keywords, present in definitions.json. This check happens once per cleaning. The number of times a word occurs from the keywords list is counted and this is used to derive a confidence score. When a particular definition's keywords appear repeatedly in these scans, that definition gets the highest score and is picked as the predicted PII class.

Octopii also checks for sensitive PII substrings such as emails, phone numbers and common government ID unique identifiers using regular expressions. It can also extract geolocation data such as addresses and countries using Natural Language Processing.

5. Output
The output consists of the following:

redacted images of the input.

