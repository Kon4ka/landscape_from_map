import os
import sys
from PIL import Image, ImageEnhance

AUGS = [
    ("rot90", lambda img: img.rotate(90, expand=True)),
    ("flip", lambda img: img.transpose(Image.FLIP_LEFT_RIGHT)),
    ("bright", lambda img: ImageEnhance.Brightness(img).enhance(1.5)),
]

FOLDERS = ["Original", "MaterialID", "ObjectID", "Normal", "Depth"]


def check_and_get_files(root):
    orig_path = os.path.join(root, "Original")
    if not os.path.isdir(orig_path):
        raise FileNotFoundError(f"No 'Original' folder at {orig_path}")
    files = [f for f in os.listdir(orig_path) if os.path.isfile(os.path.join(orig_path, f))]
    if not files:
        raise FileNotFoundError(f"No files in 'Original' folder at {orig_path}")
    return files


def augment_images(root):
    files = check_and_get_files(root)
    for fname in files:
        imgs = {}
        for folder in FOLDERS:
            fpath = os.path.join(root, folder, fname)
            if os.path.isfile(fpath):
                imgs[folder] = Image.open(fpath)
            else:
                imgs[folder] = None
        for aug_name, aug_fn in AUGS:
            for folder in FOLDERS:
                img = imgs[folder]
                if img is None:
                    continue
                aug_dir = os.path.join(root, folder, "augmented")
                os.makedirs(aug_dir, exist_ok=True)
                out_name = f"{os.path.splitext(fname)[0]}_{aug_name}{os.path.splitext(fname)[1]}"
                out_path = os.path.join(aug_dir, out_name)
                aug_img = aug_fn(img)
                aug_img.save(out_path)


def main():
    if len(sys.argv) != 2:
        print("Usage: python augment_images.py <path_to_dataset_root>")
        sys.exit(1)
    root = sys.argv[1]
    try:
        augment_images(root)
        print("Augmentation complete.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
