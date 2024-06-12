import cv2
import os


def crop(filename, output_dir):
    image = cv2.imread(filename, cv2.IMREAD_COLOR)

    # Check if image is loaded successfully
    if image is None:
        # print(f"Failed to load image: {filename}")
        return

    # Extract class name and file name from the original path
    class_name = filename.split(os.sep)[-2]
    file_name = filename.split(os.sep)[-1]

    # Create the directory in the processed folder if it doesn't exist
    class_dir = os.path.join(output_dir, class_name)
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)

    # Save the processed image in the corresponding class folder
    output_path = os.path.join(class_dir, file_name)

    height, width = image.shape[0], image.shape[1]

    if height == width:
        cv2.imwrite(output_path, image)
        return None

    dimension = height if height < width else width
    top = (height // 2) - (dimension // 2)
    bottom = (height // 2) + (dimension // 2)
    left = (width // 2) - (dimension // 2)
    right = (width // 2) + (dimension // 2)

    crop_img = image[top:bottom, left:right]
    cv2.imwrite(output_path, crop_img)


def crop_and_resize(filename, output_dir, target_size_kb=300):
    global encoded_img
    image = cv2.imread(filename, cv2.IMREAD_COLOR)

    if image is None:
        return

    # Convert to BGR if image is in RGBA (PNG with transparency)
    if image.shape[2] == 4:  # Check if it has an alpha channel
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

    class_name = filename.split(os.sep)[-2]
    file_name_without_ext = os.path.splitext(filename.split(os.sep)[-1])[0]  # Get filename without extension

    class_dir = os.path.join(output_dir, class_name)
    os.makedirs(class_dir, exist_ok=True)

    output_path = os.path.join(class_dir, f"{file_name_without_ext}.jpg")  # Force .jpg extension

    height, width = image.shape[0], image.shape[1]

    if height != width:
        dimension = min(height, width)
        top = (height // 2) - (dimension // 2)
        bottom = (height // 2) + (dimension // 2)
        left = (width // 2) - (dimension // 2)
        right = (width // 2) + (dimension // 2)
        image = image[top:bottom, left:right]

    # Resize image
    scale_percent = 100
    while scale_percent >= 10:
        result, encoded_img = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), scale_percent])
        if result and len(encoded_img) <= target_size_kb * 1024:
            break
        scale_percent -= 5

    try:
        with open(output_path, "wb") as f:
            f.write(encoded_img)
    except Exception as e:
        print(f"Error saving image {output_path}: {e}")