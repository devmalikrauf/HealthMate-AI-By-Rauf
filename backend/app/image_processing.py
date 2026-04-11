"""Image preprocessing pipeline for prescription images."""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io


def preprocess_image(image_bytes: bytes) -> Image.Image:
    """Full preprocessing pipeline: denoise, enhance, binarize."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Resize if too large (keep aspect ratio, max 3000px on longest side)
    max_dim = 3000
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # Convert to OpenCV format
    cv_img = np.array(img)
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)

    # Denoise
    cv_img = cv2.fastNlMeansDenoisingColored(cv_img, None, 10, 10, 7, 21)

    # Convert to grayscale
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    # Adaptive thresholding for mixed lighting
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )

    # Slight dilation to connect broken strokes in handwriting
    kernel = np.ones((1, 1), np.uint8)
    binary = cv2.dilate(binary, kernel, iterations=1)

    # Convert back to PIL
    result = Image.fromarray(binary)

    # Sharpen
    result = result.filter(ImageFilter.SHARPEN)

    return result


def auto_rotate(image: Image.Image) -> Image.Image:
    """Auto-rotate based on EXIF orientation tag."""
    try:
        from PIL.ExifTags import Base as ExifBase

        exif = image.getexif()
        orientation = exif.get(ExifBase.Orientation, 1)
        rotations = {3: 180, 6: 270, 8: 90}
        if orientation in rotations:
            image = image.rotate(rotations[orientation], expand=True)
    except Exception:
        pass
    return image


def deskew(image: Image.Image) -> Image.Image:
    """Correct slight rotation/skew in scanned documents."""
    cv_img = np.array(image)
    if len(cv_img.shape) == 3:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
    else:
        gray = cv_img

    # Detect edges and find dominant angle
    edges = cv2.Canny(gray, 50, 200, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

    if lines is None:
        return image

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if abs(angle) < 15:  # Only consider near-horizontal lines
            angles.append(angle)

    if not angles:
        return image

    median_angle = np.median(angles)
    if abs(median_angle) > 0.5:  # Only rotate if skew is significant
        image = image.rotate(median_angle, expand=True, fillcolor=255)

    return image
