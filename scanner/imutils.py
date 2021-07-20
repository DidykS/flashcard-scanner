import cv2


def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    if width is None and height is None:
        return image

    h, w = image.shape[:2]

    dim = None
    if width is None:
        r = height / h
        dim = (int(w * r), height)
    else:
        r = width / w
        dim = (width, int(h * r))

    resized = cv2.resize(image, dim, interpolation=inter)

    return resized
