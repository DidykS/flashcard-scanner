# scanner/main.py
# Card detection, text recognition, etc.

from typing import List, Tuple

import cv2
import numpy as np
from imutils import center_crop, rotate_without_cropping

# Type aliases.
Color = Tuple[int, int, int]
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
    max_diff = 0.15 * median_area

    rectangles = []
    for cnt, area in zip(good_contours, areas):
        if abs(median_area - area) < max_diff:
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
