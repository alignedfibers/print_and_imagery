#!/usr/bin/env python3
import sys
from PIL import Image, ImageDraw
from ultralytics import YOLO

def main(input_path, output_path, butterfly_class_id=22):
    # Load image in RGBA mode to support transparency
    image = Image.open(input_path).convert("RGBA")
    width, height = image.size

    # Initialize YOLO model (ensure you have yolov8n.pt downloaded)
    model = YOLO("yolov8n.pt")
    results = model.predict(source=input_path, conf=0.5)

    # Create a blank (black) mask with the same dimensions
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)

    # Iterate over detections and add bounding boxes for butterflies to the mask
    for box in results[0].boxes:
        # Check if detected class matches the butterfly class ID (adjust as needed)
        if int(box.cls) == butterfly_class_id:
            x1, y1, x2, y2 = map(int, box.xyxy.tolist()[0])
            draw.rectangle([x1, y1, x2, y2], fill=255)

    # Create an output image with a transparent background
    output_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    # Paste the original image using the mask as the alpha channel
    output_img.paste(image, mask=mask)
    output_img.save(output_path)
    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python simple_identify_butterflys_in_art_set_otherpixels_transparent.py <input_image> <output_image>")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    main(input_path, output_path)
#!/usr/bin/env python3
import sys
from PIL import Image, ImageDraw
from ultralytics import YOLO

def main(input_path, output_path, butterfly_class_id=22):
    # Load image in RGBA mode to support transparency
    image = Image.open(input_path).convert("RGBA")
    width, height = image.size

    # Initialize YOLO model (ensure you have yolov8n.pt downloaded)
    model = YOLO("yolov8n.pt")
    results = model.predict(source=input_path, conf=0.5)

    # Create a blank (black) mask with the same dimensions
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)

    # Iterate over detections and add bounding boxes for butterflies to the mask
    for box in results[0].boxes:
        # Check if detected class matches the butterfly class ID (adjust as needed)
        if int(box.cls) == butterfly_class_id:
            x1, y1, x2, y2 = map(int, box.xyxy.tolist()[0])
            draw.rectangle([x1, y1, x2, y2], fill=255)

    # Create an output image with a transparent background
    output_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    # Paste the original image using the mask as the alpha channel
    output_img.paste(image, mask=mask)
    output_img.save(output_path)
    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python simple_identify_butterflys_in_art_set_otherpixels_transparent.py <input_image> <output_image>")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    main(input_path, output_path)
