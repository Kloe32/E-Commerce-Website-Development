from PIL import Image, ImageFilter, ImageEnhance
import os

def get_image_files(input_dir):
    """Return all image files in a directory."""
    exts = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
    return [os.path.join(input_dir, f) for f in os.listdir(input_dir)
            if f.lower().endswith(exts) and os.path.isfile(os.path.join(input_dir, f))]

def process_image(
    img_path,
    output_path,
    resize=False,   
    size=(256, 256),
    grayscale=False,
    blur=False,
    enhanced=False,
    out_format='JPEG'
):
    """Process the image as requested."""
    try:
        img = Image.open(img_path).convert("RGBA")

        # Resize to 256x256 only if selected by user
        if resize:
            img = img.resize((size), Image.LANCZOS)

        # Greyscale
        if grayscale:
            img = img.convert("L").convert("RGBA")

        # Blur
        if blur:
            img = img.filter(ImageFilter.GaussianBlur(radius=2))

        # Enhanced (CPU-intensive filters)
        if enhanced:
            img = ImageEnhance.Brightness(img).enhance(1.2)   # Simulated Exposure
            img = ImageEnhance.Contrast(img).enhance(2.0)      # Strong contrast
            img = ImageEnhance.Color(img).enhance(2.0)         # Vibrance/Saturation
            img = ImageEnhance.Sharpness(img).enhance(2.0)     # Sharpness

        # Convert RGBA/LA to RGB for JPEG output (no alpha for JPEG)
        save_img = img
        if out_format.upper() == 'JPEG':
            if img.mode in ('RGBA', 'LA'):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                save_img = background
            else:
                save_img = img.convert('RGB')
        else:
            save_img = img

        save_img.save(output_path, out_format)
        return True
    except Exception as e:
        print(f"Error processing {img_path}: {e}")
        return False