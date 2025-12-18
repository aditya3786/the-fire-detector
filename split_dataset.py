import os, random, shutil

# Paths
images_path = "data/images"
labels_path = "data/labels"

# Create train and val folders
os.makedirs("data/images/train", exist_ok=True)
os.makedirs("data/images/val", exist_ok=True)
os.makedirs("data/labels/train", exist_ok=True)
os.makedirs("data/labels/val", exist_ok=True)

# Get all image files
images = [f for f in os.listdir(images_path) if f.endswith(".jpg") or f.endswith(".png")]
random.shuffle(images)

# Split (80% train, 20% val)
split_index = int(0.8 * len(images))
train_images = images[:split_index]
val_images = images[split_index:]

def copy_files(image_list, subset):
    for img in image_list:
        img_src = os.path.join(images_path, img)
        lbl_src = os.path.join(labels_path, os.path.splitext(img)[0] + ".txt")
        
        img_dst = f"data/images/{subset}/{img}"
        lbl_dst = f"data/labels/{subset}/{os.path.splitext(img)[0]}.txt"
        
        if os.path.exists(img_src):
            shutil.copy(img_src, img_dst)
        if os.path.exists(lbl_src):
            shutil.copy(lbl_src, lbl_dst)

copy_files(train_images, "train")
copy_files(val_images, "val")

print(f"✅ Dataset split completed! Train: {len(train_images)} | Val: {len(val_images)}")
