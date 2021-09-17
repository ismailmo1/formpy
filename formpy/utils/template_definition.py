"""This module contains helper functions to define a new template."""

import cv2
import numpy as np


def find_spots(
    img: np.array, max_radius: int = 35, min_radius: int = 10
) -> list[list[int]]:
    """Find all contours between radius limits and aspect ratio between 0.7 and 1.
    Return sorted list of coordinates - sort by x first, then y.

    Args:
        img (np.array): img to search answers for - this should be a template
        page with all the answers filled in so the coordinates can be detected.
    """
    conts, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    spotCentres = []
    i = 0
    for c in conts:
        i += 1
        # compute enclosing rect to get center points
        x, y, w, h = cv2.boundingRect(c)

        ar = w / h
        # check if bounding rectangle of circle roughly matches criteria:(aspect ratio ==1) and (w,h == 25)
        if (
            min_radius * 2 < w < max_radius * 2
            and min_radius * 2 < h < max_radius * 2
            and 0.9 < ar < 1.1
        ):
            # draw on blank to show correct detection
            # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255))

            xCentre = int(x + (w / 2))
            yCentre = int(y + (h / 2))
            cv2.circle(img, (xCentre, yCentre), 1, 0, -1)
            spotCentres.append([xCentre, yCentre])

    # sort by x, then y
    sortedSpots = sorted(
        spotCentres, key=lambda x: (x[0], x[1]), reverse=False
    )

    return sortedSpots
