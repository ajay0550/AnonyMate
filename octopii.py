output_file = "output.json"
notifyURL = ""

import json, textract, sys, urllib, cv2, os, json, shutil, traceback
import subprocess
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from pdf2image import convert_from_path
import image_utils, file_utils, text_utils, webhook

model_file_name = 'models/other_pii_model.h5'
labels_file_name = 'models/other_pii_model.txt'
temp_dir = ".OCTOPII_TEMP/"


def help_screen():
    help = '''Usage: python octopii.py <file, local path or URL>
Note: Only Unix-like filesystems, S3 and open directory URLs are supported.'''
    print(help)

def search_pii(file_path):
    
    contains_faces = 0
    text = ""  # Initialize text variable

    if file_utils.is_image(file_path):
        image = cv2.imread(file_path)
        contains_faces = image_utils.scan_image_for_people(image)

        original, intelligible = image_utils.scan_image_for_text(image)
        text = original  # Extracted text from image
        print("\n📝 Extracted text from image:\n", text)  # Debugging OCR output

    elif file_utils.is_pdf(file_path):
        pdf_pages = convert_from_path(file_path, 400) # Higher DPI reads small text better
        for page in pdf_pages:
            contains_faces = image_utils.scan_image_for_people(page)

            original, intelligible = image_utils.scan_image_for_text(page)
            text = original
            print("\n📝 Extracted text from PDF:\n", text)  # Debugging OCR output

    else:
        text = textract.process(file_path).decode()
        intelligible = text_utils.string_tokenizer(text)
        print("\n📝 Extracted text from document:\n", text)  # Debugging OCR output

    # Detect PII
    addresses = text_utils.regional_pii(text)
    emails = text_utils.email_pii(text, rules)
    phone_numbers = text_utils.phone_pii(text, rules)
    identifiers = text_utils.id_card_numbers_pii(text, rules)

    # Debugging print statements for detected PII
    print("\n🔍 Detected PII:")
    print("Addresses:", addresses)
    print("Emails:", emails)
    print("Phone Numbers:", phone_numbers)
    print("Identifiers:", identifiers)

    keywords_scores = text_utils.keywords_classify_pii(rules, intelligible)
    score = max(keywords_scores.values(), default=0)
    pii_class = list(keywords_scores.keys())[list(keywords_scores.values()).index(score)] if score > 0 else None

    country_of_origin = rules[pii_class]["region"] if pii_class else None

    if len(identifiers) != 0:
        identifiers = identifiers[0]["result"]

    if temp_dir in file_path:
        file_path = file_path.replace(temp_dir, "")
        file_path = urllib.parse.unquote(file_path)

    result = {
        "file_path": file_path,
        "pii_class": pii_class,
        "score": score,
        "country_of_origin": country_of_origin,
        "faces": contains_faces,
        "identifiers": identifiers,
        "emails": emails,
        "phone_numbers": phone_numbers,
        "addresses": addresses
    }

    return result
    

if __name__ == '__main__':
    if len(sys.argv) == 1:
        help_screen()
        exit(-1)
    else:
        location = sys.argv[1]

        # Check for the -notify flag
        notify_index = sys.argv.index('--notify') if '--notify' in sys.argv else -1

        if notify_index != -1 and notify_index + 1 < len(sys.argv): notifyURL = sys.argv[notify_index + 1]
        else: notifyURL = None

    rules = text_utils.get_regexes()

    files = []
    items = []

    temp_exists = False

    print("\n📂 Scanning:", location)

    try:
        shutil.rmtree(temp_dir)
    except:
        pass

    if "http" in location:
        try:
            file_urls = []
            _, extension = os.path.splitext(location)
            if extension != "":
                file_urls.append(location)
            else:
                files = file_utils.list_local_files(location)

            file_urls = file_utils.list_s3_files(location)
            if len(file_urls) != 0:
                temp_exists = True
                os.makedirs(os.path.dirname(temp_dir))
                for url in file_urls:
                    file_name = urllib.parse.quote(url, "UTF-8")
                    urllib.request.urlretrieve(url, temp_dir+file_name)

        except:
            try:
                file_urls = file_utils.list_directory_files(location)

                if len(file_urls) != 0:  # Directory listing (e.g., Apache)
                    temp_exists = True
                    os.makedirs(os.path.dirname(temp_dir))
                    for url in file_urls:
                        try:
                            encoded_url = urllib.parse.quote(url, "UTF-8")
                            urllib.request.urlretrieve(url, temp_dir + encoded_url)
                        except:
                            pass  # Capture 404

                else:  # Curl text from location if available
                    temp_exists = True
                    os.makedirs(os.path.dirname(temp_dir))
                    encoded_url = urllib.parse.quote(location, "UTF-8") + ".txt"
                    urllib.request.urlretrieve(location, temp_dir + encoded_url)

            except:
                traceback.print_exc()
                print("❌ This URL is not a valid S3 or has no directory listing enabled. Try running Octopii on these files locally.")
                sys.exit(-1)

        files = file_utils.list_local_files(temp_dir)

    else:
        _, extension = os.path.splitext(location)
        if extension != "":
            files.append(location)
        else:
            files = file_utils.list_local_files(location)

    if len(files) == 0:
        print("❌ Invalid path provided. Please provide a non-empty directory or a file as an argument.")
        sys.exit(0)

    # Try and truncate files if they're too big
    for file_path in files:
        try:
            file_utils.truncate(file_path)
        except:
            pass

    for file_path in files:
        try:
            results = search_pii(file_path)
            print("\n✅ Final PII Detection Result:\n", json.dumps(results, indent=4))
            file_utils.append_to_output_file(results, output_file)
            if notifyURL is not None:
                webhook.push_data(json.dumps(results), notifyURL)
            print("\n📂 Output saved in:", output_file)

        except textract.exceptions.MissingFileError:
            print("\n❌ Couldn't find file:", file_path, "- Skipping...")

        except textract.exceptions.ShellError:
            print("\n❌ File is empty or corrupt:", file_path, "- Skipping...")

    if temp_exists:
        shutil.rmtree(temp_dir)

    subprocess.run(["python", "redact.py"])

    sys.exit(0)
