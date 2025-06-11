import os
from PIL import Image, ImageFilter

def get_image_files(input_dir, extensions=('.png', '.jpg', '.jpeg', '.bmp')):
    """Get list of image file paths in a directory with specified extensions."""
    return [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith(extensions)
    ]

def process_image(input_path, output_path=None, size=(256, 256), grayscale=True, blur=False, out_format=None):
    try:
        with Image.open(input_path) as img:
            if size is not None:
                img = img.resize(size)
            if grayscale:
                img = img.convert('L')
            if blur:
                img = img.filter(ImageFilter.BLUR)
            # If no output format specified, use the input image's format
            if out_format is None:
                out_format = img.format or 'JPEG'
            # If no output path specified, use same name with output format extension
            if output_path is None:
                base, _ = os.path.splitext(input_path)
                output_path = base + '.' + out_format.lower()
            img.save(output_path, out_format)
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False