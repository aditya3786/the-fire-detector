import os
import xml.etree.ElementTree as ET

# Paths
annotations_dir = "annotations/Annotations"
output_dir = "data/labels"

os.makedirs(output_dir, exist_ok=True)

# Define class mapping
class_mapping = {
    "fire": 0,
    "smoke": 1
}

def convert_annotation(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    image_name = os.path.splitext(os.path.basename(xml_file))[0]
    txt_file = os.path.join(output_dir, image_name + ".txt")

    with open(txt_file, "w") as f:
        for obj in root.iter("object"):
            cls = obj.find("name").text
            if cls not in class_mapping:
                continue

            cls_id = class_mapping[cls]
            xmlbox = obj.find("bndbox")
            xmin = float(xmlbox.find("xmin").text)
            ymin = float(xmlbox.find("ymin").text)
            xmax = float(xmlbox.find("xmax").text)
            ymax = float(xmlbox.find("ymax").text)

            # YOLO format: x_center, y_center, width, height (normalized)
            size = root.find("size")
            img_w = float(size.find("width").text)
            img_h = float(size.find("height").text)

            x_center = ((xmin + xmax) / 2) / img_w
            y_center = ((ymin + ymax) / 2) / img_h
            width = (xmax - xmin) / img_w
            height = (ymax - ymin) / img_h

            f.write(f"{cls_id} {x_center} {y_center} {width} {height}\n")

# Convert all XML files
for xml_file in os.listdir(annotations_dir):
    if xml_file.endswith(".xml"):
        convert_annotation(os.path.join(annotations_dir, xml_file))

print("✅ Conversion completed! YOLO label files are saved in 'data/labels'.")
