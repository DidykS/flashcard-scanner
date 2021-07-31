# scanner/main.py
# Card detection, text recognition, etc.

from typing import Dict, List, Tuple

import cv2
import numpy as np
from google.cloud import vision
from imutils import center_crop, rotate_without_cropping

# Type aliases.
Color = Tuple[np.uint8, np.uint8, np.uint8]
RotatedRect = Tuple[Tuple[float, float], Tuple[float, float], float]


def detect_cards(
    image: np.ndarray, hsv_ranges: Tuple[Color, Color]
) -> List[RotatedRect]:
    """Detect the cards inside the image.

    Args:
        image (np.ndarray): The input image.
        hsv_ranges (Tuple[Color, Color]): Low and high HSV color ranges to remove the background.

    Returns:
        The list of RotatedRect.
    """
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv_low, hsv_high = hsv_ranges
    thresh = cv2.inRange(image_hsv, hsv_low, hsv_high)
    # Invert the binary image.
    thresh = 255 - thresh
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel=None)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    good_contours = []
    areas = []
    for cnt in contours:
        # Approximate the contour.
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, closed=True)

        if len(approx) == 4:
            area = cv2.contourArea(cnt)
            # Skip the contour if its area is very small.
            if area < 1000:
                continue
            good_contours.append(cnt)
            areas.append(area)

    median_area = np.median(areas)
    # The area of the contour must be +-15% of the median area.
    max_delta_area = 0.15 * median_area

    rectangles = []
    for cnt, area in zip(good_contours, areas):
        if abs(median_area - area) < max_delta_area:
            rectangles.append(cv2.minAreaRect(cnt))

    return rectangles


def is_upside(card: np.ndarray) -> bool:
    """Check if the card is upside down.

    Args:
        card (np.ndarray): A grayscale image of the card.

    Returns:
        True if the card is upside down. Otherwise, False.
    """
    h = card.shape[0]
    # Take 10% of the height of the card.
    dh = int(h * 0.1)

    top = card[:dh]
    bottom = card[-dh:]

    # Check the average colors of the top and bottom of the image.
    return top.mean() > bottom.mean()


def crop_cards(
    image: np.ndarray, rectangles: List[RotatedRect]
) -> List[np.ndarray]:
    """Crop out the cards from the image.

    Args:
        image (np.ndarray): The input image.
        rectangles (List[RotatedRect]): The list of RotatedRect describes the cards inside the image.

    Returns:
        The list of cards.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    cards = []
    for rect in rectangles:
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        # Calculate the minimal up-right bounding rectangle for each RotatedRect.
        x, y, w, h = cv2.boundingRect(box)
        # Replace negative coordinates with zeros.
        x = max(0, x)
        y = max(0, y)

        card = gray[y : y + h, x : x + w]

        _, (rect_w, rect_h), angle = rect
        card = rotate_without_cropping(card, angle)

        # Make sure that the card is in a horizontal position.
        card_h, card_w = card.shape[:2]
        if card_h > card_w:
            card = cv2.rotate(card, cv2.ROTATE_90_CLOCKWISE)

        if rect_h > rect_w:
            rect_h, rect_w = rect_w, rect_h

        card = center_crop(card, (int(rect_w), int(rect_h)))

        if is_upside(card):
            card = cv2.rotate(card, cv2.ROTATE_180)

        cards.append(card)

    return cards


def detect_text(image: np.ndarray, heights: List[int]) -> List[List[Dict]]:
    """Detect text in the image.

    Args:
        image (np.ndarray): The input image.
        heights (List[int]): A list with the height of each card in the input image.

    Returns:
        A nested list with text annotations for each card.
    """
    client = vision.ImageAnnotatorClient()

    _, encoded_image = cv2.imencode(".jpg", image)
    content = encoded_image.tobytes()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)

    cards_data = []
    card_data = []
    total_height = heights.pop(0)
    for annotation in response.text_annotations[1:]:
        coords = [(v.x, v.y) for v in annotation.bounding_poly.vertices]
        tl, tr, br, bl = coords
        y = max(br[1], bl[1])

        new_annotation = dict()
        new_annotation["text"] = annotation.description
        # Calculate the center coordinates of the text.
        new_annotation["center"] = (
            (tl[0] + tr[0] + br[0] + bl[0]) // 4,
            (tl[1] + tr[1] + br[1] + bl[1]) // 4,
        )

        if y < total_height:
            card_data.append(new_annotation)
        else:
            cards_data.append(card_data)
            card_data = [new_annotation]
            total_height += heights.pop(0)

    if card_data:
        cards_data.append(card_data)

    return cards_data


def get_text_rows(
    annotations: List[Dict], max_delta_y: int = 10
) -> List[List[str]]:
    """Combine the annotations into the text rows.

    Args:
        annotations (List[Dict]): A list with text annotations.
        max_delta_y (int, optional): The maximum difference between the y-axis coordinates. Defaults to 10 (pixels).

    Returns:
        A nested list with text strings.
    """
    rows = []
    row = [annotations[0]["text"]]
    prev_y = annotations[0]["center"][1]

    for annotation in annotations[1:]:
        y = annotation["center"][1]
        if abs(prev_y - y) <= max_delta_y:
            row.append(annotation["text"])
        else:
            rows.append(row)
            row = [annotation["text"]]
        prev_y = y

    if row:
        rows.append(row)

    return rows
