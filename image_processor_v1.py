import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import time
from image_utils import get_image_files, process_image
import tkinter.font as tkfont

class BatchImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Image Processor v1 (Sequential)")

        # Input/Output
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.format_var = tk.StringVar(value='JPEG')

        # Processing options
        self.resize_var = tk.BooleanVar(value=True)
        self.grayscale_var = tk.BooleanVar()
        self.blur_var = tk.BooleanVar()
        self.enhanced_var = tk.BooleanVar()

        # GUI Layout
        self._build_gui()

    def _build_gui(self):
        # Styles
        self.root.configure(bg="#d9d9d9")
        Background_C=('#d9d9d9')
        button_style = {
            "fg": "white",
            "bg": "#092467",
            "activeforeground": "white",
            "activebackground": "#2D4171",
            "relief": tk.RAISED,
            "bd": 2
        }
        O_paddings={
            "padx": "10",
            "pady": "5"
        }
        default_font=tkfont.Font(family="Verdana",size=12)
        # Input/Output
        tk.Label(self.root,bg=Background_C, text="Input Folder:",font=default_font).grid(row=0, column=0, sticky="e",padx=10,pady=10)
        tk.Entry(self.root, textvariable=self.input_var, width=30,font=default_font,highlightcolor="black",highlightthickness=2).grid(row=0, column=1,ipady=3)
        tk.Button(self.root,text="Browse",command=self.select_input_folder,font=default_font,**button_style).grid(row=0, column=2,padx=5)

        tk.Label(self.root,bg=Background_C, text="Output Folder:",font=default_font).grid(row=1, column=0, sticky="e",padx=10,pady=10)
        tk.Entry(self.root, textvariable=self.output_var, width=30,font=default_font,highlightcolor="black",highlightthickness=2).grid(row=1, column=1,ipady=3)
        tk.Button(self.root,text="Browse", command=self.select_output_folder,font=default_font, **button_style).grid(row=1, column=2,padx=5)

        # Format
        tk.Label(self.root,bg=Background_C,font=default_font, text="Output Format:").grid(row=2, column=0, sticky="e")
        self.Option=tk.OptionMenu(self.root, self.format_var, 'JPEG', 'PNG', 'BMP', 'GIF')
        self.Option.grid(row=2, column=1, sticky="w")
        self.Option.config(bg='#092467', fg="white",font=default_font, activebackground="#2D4171", activeforeground="white", highlightthickness=0)
        self.Option["menu"].config(bg='#092467', fg="white", activebackground="#2D4171", activeforeground="white")


        # Options
        row = 3
        tk.Checkbutton(self.root,font=default_font,bg=Background_C, text="Resize to 256 x 256", variable=self.resize_var).grid(row=row, column=0, sticky="w",**O_paddings)
        tk.Checkbutton(self.root,font=default_font,bg=Background_C, text="Greyscale", variable=self.grayscale_var).grid(row=row, column=1, sticky="w",**O_paddings)
        row += 1
        tk.Checkbutton(self.root,font=default_font,bg=Background_C, text="Blur", variable=self.blur_var).grid(row=row, column=0, sticky="w",**O_paddings)
        tk.Checkbutton(self.root,font=default_font,bg=Background_C, text="Enhanced Image", variable=self.enhanced_var).grid(row=row, column=1, sticky="w",**O_paddings)

        # Info for size
        row += 1
        tk.Label(self.root,bg=Background_C,font=default_font, text="If not resizing, original image size is kept.").grid(row=row, column=0, columnspan=3,**O_paddings)

        # Buttons and status
        row += 1
        self.process_btn = tk.Button(self.root, text="Process Images", command=self.process_images,font=default_font,**button_style)
        self.process_btn.grid(row=row, column=0, columnspan=2)
        self.open_output_btn = tk.Button(self.root, text="Open Output Folder", command=self.open_output_folder, state="disabled",font=default_font,**button_style)
        self.open_output_btn.grid(row=row, column=2, columnspan=2,padx=10)
        row += 1
        self.status_label = tk.Label(self.root, text="",font=default_font,bg=Background_C)
        self.status_label.grid(row=row, column=0, columnspan=4,**O_paddings)

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
        resize = self.resize_var.get()
        size = (256, 256)
        grayscale = self.grayscale_var.get()
        blur = self.blur_var.get()
        enhanced = self.enhanced_var.get()

        if not input_dir or not output_dir:
            messagebox.showerror("Error", "Please select input and output folders.")
            return

        self.process_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Processing...")
        self.open_output_btn.config(state="disabled")

        def run():
            try:
                files = get_image_files(input_dir)
                if not files:
                    self.status_label.config(text="No images found!")
                    self.process_btn.config(state=tk.NORMAL)
                    return
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                processed = 0
                start_time = time.time()
                for img_path in files:
                    fname = os.path.splitext(os.path.basename(img_path))[0]
                    ext = output_format.lower()
                    out_file = os.path.join(output_dir, f"{fname}.{ext}")
                    process_image(
                        img_path,
                        out_file,
                        resize=resize,
                        size=size,
                        grayscale=grayscale,
                        blur=blur,
                        enhanced=enhanced,
                        out_format=output_format
                    )
                    processed += 1
                    self.status_label.config(text=f"Processing... ({processed}/{len(files)})")
                elapsed = time.time() - start_time
                self.status_label.config(text=f"Done! Processed {processed} images in {elapsed:.2f} seconds.")
                self.open_output_btn.config(state="normal")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.status_label.config(text="Error occurred!")
            finally:
                self.process_btn.config(state=tk.NORMAL)
        threading.Thread(target=run).start()

    def open_output_folder(self):
        import webbrowser
        output_dir = self.output_var.get()
        if output_dir and os.path.exists(output_dir):
            webbrowser.open(output_dir)

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchImageProcessorApp(root)
    root.mainloop()