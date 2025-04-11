import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import json
import os
import threading
import sys
import subprocess
from PIL import Image, ImageTk

class OctoPIIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AnonyMate - PII Detection & Redaction Tool")
        self.root.geometry("900x900")
        self.root.configure(bg="#f0f0f0")

        # Variables
        self.file_path = tk.StringVar()
        self.webhook_url = tk.StringVar()
        self.output_path = tk.StringVar(value="output.json")
        self.scanning = False
        self.original_img_label = None
        self.redacted_img_label = None

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", padx=10, pady=10)
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(header_frame, text="AnonyMate", font=("Arial", 20, "bold"), fg="white", bg="#2c3e50")
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(header_frame, text="PII Detection & Redaction Tool", font=("Arial", 12), fg="white", bg="#2c3e50")
        subtitle_label.pack(side=tk.LEFT, padx=10)

        # Main content
        content_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Source selection
        source_frame = tk.LabelFrame(content_frame, text="Source Selection", bg="#f0f0f0", padx=10, pady=10)
        source_frame.pack(fill=tk.X, pady=10)

        tk.Label(source_frame, text="File/Directory Path:", bg="#f0f0f0").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        path_entry = tk.Entry(source_frame, textvariable=self.file_path, width=50)
        path_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)

        browse_btn = tk.Button(source_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)

        # Options
        options_frame = tk.LabelFrame(content_frame, text="Options", bg="#f0f0f0", padx=10, pady=10)
        options_frame.pack(fill=tk.X, pady=10)

        tk.Label(options_frame, text="Webhook URL (optional):", bg="#f0f0f0").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        webhook_entry = tk.Entry(options_frame, textvariable=self.webhook_url, width=50)
        webhook_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

        tk.Label(options_frame, text="Output File:", bg="#f0f0f0").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        output_entry = tk.Entry(options_frame, textvariable=self.output_path, width=50)
        output_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)

        # Buttons frame
        button_frame = tk.Frame(content_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=10)

        self.scan_btn = tk.Button(button_frame, text="Scan for PII", command=self.start_scan, bg="#3498db", fg="white", padx=10, pady=5, font=("Arial", 11))
        self.scan_btn.pack(side=tk.LEFT, padx=5)

        self.redact_btn = tk.Button(button_frame, text="Redact PII", command=self.start_redaction, bg="#e74c3c", fg="white", padx=10, pady=5, font=("Arial", 11), state=tk.DISABLED)
        self.redact_btn.pack(side=tk.LEFT, padx=5)

        # Image preview
        preview_frame = tk.LabelFrame(content_frame, text="Image Preview", bg="#f0f0f0", padx=10, pady=10)
        preview_frame.pack(fill=tk.X, pady=10)
        self.original_img_label = tk.Label(preview_frame, text="Original Image will appear here", bg="#f0f0f0")
        self.original_img_label.pack(side=tk.LEFT, padx=10)
        self.redacted_img_label = tk.Label(preview_frame, text="Redacted Image will appear here", bg="#f0f0f0")
        self.redacted_img_label.pack(side=tk.RIGHT, padx=10)

        # Console output
        console_frame = tk.LabelFrame(content_frame, text="Console Output", bg="#f0f0f0", padx=10, pady=10)
        console_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, bg="#253342", fg="#ecf0f1", font=("Consolas", 10))
        self.console.pack(fill=tk.BOTH, expand=True)

        # Results frame
        results_frame = tk.LabelFrame(content_frame, text="Detection Results", bg="#f0f0f0", padx=10, pady=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.results_tree = ttk.Treeview(results_frame, columns=("Type", "Value", "Score"), show="headings")
        self.results_tree.heading("Type", text="PII Type")
        self.results_tree.heading("Value", text="Value")
        self.results_tree.heading("Score", text="Score")
        self.results_tree.column("Type", width=150)
        self.results_tree.column("Value", width=350)
        self.results_tree.column("Score", width=100)
        self.results_tree.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Select File", filetypes=[
            ("All Files", "*.*"),
            ("Images", "*.png *.jpg *.jpeg"),
            ("PDF Files", "*.pdf"),
            ("Text Files", "*.txt"),
            ("Documents", "*.doc *.docx")
        ])

        if file_path:
            self.file_path.set(file_path)
            self.display_image_preview(file_path, self.original_img_label)

    def display_image_preview(self, path, label):
        try:
            img = Image.open(path)
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            label.image = photo
        except Exception as e:
            label.config(text=f"Error loading image: {e}")

    def redirect_output(self):
        class ConsoleRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget

            def write(self, string):
                self.text_widget.insert(tk.END, string)
                self.text_widget.see(tk.END)
                self.text_widget.update_idletasks()

            def flush(self):
                pass

        sys.stdout = ConsoleRedirector(self.console)
        sys.stderr = ConsoleRedirector(self.console)

    def start_scan(self):
        if not self.file_path.get():
            self.update_status("No file or directory selected")
            return

        self.scanning = True
        self.scan_btn.config(state=tk.DISABLED)
        self.redact_btn.config(state=tk.DISABLED)
        self.update_status("Scanning...")
        self.console.delete(1.0, tk.END)

        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        threading.Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        try:
            self.redirect_output()
            cmd = ["python", "octopii.py", self.file_path.get()]
            if self.webhook_url.get():
                cmd.extend(["--notify", self.webhook_url.get()])
            result = subprocess.run(cmd, text=True, capture_output=False)
            if result.returncode == 0:
                self.update_status("Scan completed successfully")
                self.load_results()
                self.redact_btn.config(state=tk.NORMAL)
            else:
                self.update_status("Scan failed")
        except Exception as e:
            self.console.insert(tk.END, f"\nError: {str(e)}")
            self.update_status("Error occurred during scan")
        finally:
            self.scanning = False
            self.scan_btn.config(state=tk.NORMAL)

    def load_results(self):
        try:
            with open(self.output_path.get(), "r") as f:
                results = json.load(f)
            for result in results:
                file_path = result["file_path"]
                file_item = self.results_tree.insert("", tk.END, text=file_path, values=("File", file_path, ""))
                if result["pii_class"]:
                    self.results_tree.insert(file_item, tk.END, values=("PII Class", result["pii_class"], result["score"]))
                if result["faces"]:
                    self.results_tree.insert(file_item, tk.END, values=("Faces", "Detected", ""))
                for id_value in result["identifiers"]:
                    self.results_tree.insert(file_item, tk.END, values=("Identifier", id_value, ""))
                for email in result["emails"]:
                    self.results_tree.insert(file_item, tk.END, values=("Email", email, ""))
                for phone in result["phone_numbers"]:
                    self.results_tree.insert(file_item, tk.END, values=("Phone", phone, ""))
                for address in result["addresses"]:
                    self.results_tree.insert(file_item, tk.END, values=("Address", address, ""))
        except Exception as e:
            self.console.insert(tk.END, f"\nError loading results: {str(e)}")

    def start_redaction(self):
        self.redact_btn.config(state=tk.DISABLED)
        self.scan_btn.config(state=tk.DISABLED)
        self.update_status("Redacting PII...")
        threading.Thread(target=self.run_redaction, daemon=True).start()

    def run_redaction(self):
        try:
            self.redirect_output()
            result = subprocess.run(["python", "redact.py"], text=True, capture_output=False)
            if result.returncode == 0:
                self.update_status("Redaction completed successfully")
                redacted_path = self.file_path.get().replace(".", "_redacted.", 1)
                if os.path.exists(redacted_path):
                    self.display_image_preview(redacted_path, self.redacted_img_label)
            else:
                self.update_status("Redaction failed")
        except Exception as e:
            self.console.insert(tk.END, f"\nError: {str(e)}")
            self.update_status("Error occurred during redaction")
        finally:
            self.scan_btn.config(state=tk.NORMAL)
            self.redact_btn.config(state=tk.NORMAL)

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = OctoPIIApp(root)
    root.mainloop()
