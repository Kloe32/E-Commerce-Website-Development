import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import webbrowser
import time
import concurrent.futures
from image_utils import get_image_files, process_image

class BatchImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Image Processor (Parallel)")

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.resize_var = tk.BooleanVar(value=True)
        self.gray_var = tk.BooleanVar(value=True)
        self.blur_var = tk.BooleanVar(value=False)
        self.format_var = tk.StringVar(value="JPEG")  # Default output format

        # Folder selection
        tk.Label(root, text="Input Folder:").grid(row=0, column=0, sticky="e")
        tk.Entry(root, textvariable=self.input_var, width=40, state='readonly').grid(row=0, column=1)
        tk.Button(root, text="Browse", command=self.select_input_folder).grid(row=0, column=2)

        tk.Label(root, text="Output Folder:").grid(row=1, column=0, sticky="e")
        tk.Entry(root, textvariable=self.output_var, width=40, state='readonly').grid(row=1, column=1)
        tk.Button(root, text="Browse", command=self.select_output_folder).grid(row=1, column=2)

        # Processing options
        tk.Label(root, text="Options:").grid(row=2, column=0, sticky="e")
        opt_frame = tk.Frame(root)
        opt_frame.grid(row=2, column=1, columnspan=2, sticky="w")
        tk.Checkbutton(opt_frame, text="Resize to 256x256", variable=self.resize_var).pack(side="left")
        tk.Checkbutton(opt_frame, text="Grayscale", variable=self.gray_var).pack(side="left")
        tk.Checkbutton(opt_frame, text="Blur", variable=self.blur_var).pack(side="left")

        # Output format option
        tk.Label(root, text="Save as:").grid(row=3, column=0, sticky="e")
        format_options = ["BMP", "JPEG", "PNG", "Original"]
        tk.OptionMenu(root, self.format_var, *format_options).grid(row=3, column=1, sticky="w")

        # Process button
        self.process_btn = tk.Button(root, text="Process", command=self.process_images)
        self.process_btn.grid(row=4, column=0, columnspan=3, pady=10)

        # Status and Open Output
        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.grid(row=5, column=0, columnspan=3)
        self.open_output_btn = tk.Button(root, text="Open Output Folder", command=self.open_output_folder, state="disabled")
        self.open_output_btn.grid(row=6, column=0, columnspan=3, pady=5)

    def select_input_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_var.set(folder)

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_var.set(folder)

    def process_images(self):
        input_dir = self.input_var.get()
        output_dir = self.output_var.get()
        output_format = self.format_var.get()
        if not input_dir or not output_dir:
            messagebox.showerror("Error", "Please select both input and output folders.")
            return

        self.process_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Processing (parallel)...")
        self.open_output_btn.config(state="disabled")

        def run():
            try:
                files = get_image_files(input_dir)
                if not files:
                    self.status_label.config(text="No images found in the input folder.")
                    self.process_btn.config(state=tk.NORMAL)
                    return
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                total = len(files)
                start_time = time.time()

                def process_one(img_path):
                    filename = os.path.basename(img_path)
                    name, ext = os.path.splitext(filename)
                    # Decide output extension and format
                    if output_format == "Original":
                        out_ext = ext
                        if ext.lower() in ['.jpg', '.jpeg']:
                            out_fmt = 'JPEG'
                        elif ext.lower() == '.png':
                            out_fmt = 'PNG'
                        elif ext.lower() == '.bmp':
                            out_fmt = 'BMP'
                        else:
                            out_fmt = 'JPEG'
                            out_ext = '.jpg'
                    else:
                        out_fmt = output_format
                        if output_format == 'JPEG':
                            out_ext = '.jpg'
                        elif output_format == 'PNG':
                            out_ext = '.png'
                        else:
                            out_ext = '.bmp'
                    output_path = os.path.join(output_dir, name + out_ext)
                    return process_image(
                        img_path,
                        output_path,
                        size=(256, 256) if self.resize_var.get() else None,
                        grayscale=self.gray_var.get(),
                        blur=self.blur_var.get(),
                        out_format=out_fmt
                    )

                processed = 0
                # You may want to limit max_workers, e.g. max_workers=8
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(process_one, img_path) for img_path in files]
                    for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                        future.result()  # propagate exceptions
                        self.status_label.config(text=f"Processing (parallel)... ({i}/{total})")

                end_time = time.time()
                elapsed = end_time - start_time
                self.status_label.config(
                    text=f"Done! Processed {total} images in {elapsed:.2f} seconds (Parallelized)."
                )
                self.open_output_btn.config(state="normal")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.status_label.config(text="Error occurred!")
            finally:
                self.process_btn.config(state=tk.NORMAL)
        threading.Thread(target=run).start()

    def open_output_folder(self):
        output_dir = self.output_var.get()
        if os.path.isdir(output_dir):
            webbrowser.open(f'file://{os.path.abspath(output_dir)}')

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchImageProcessorApp(root)
    root.mainloop()