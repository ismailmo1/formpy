from __future__ import annotations

import cv2
import numpy as np


def find_spots(
    img: np.array, max_radius: int = 35, min_radius: int = 10
) -> list[list[int]]:
    """Use contour detection to find all circles that may correspond to
    answers on a template.
    Min and max radius and the aspect ratio of between 0.9 - 1.1 are used to
    determine if
    the detected contour is an answer

    Args:
        img (np.array): image of template read into array e.g. via cv2.imread()
        This should be a template page with all the answers filled in so the
        coordinates can be detected
        max_radius (int, optional): max threshold used to determine if the
        contour is a answer circle. Defaults to 35.
        min_radius (int, optional): min threshold used to determine if the
        contour is a answer circle. Defaults to 10.

    Returns:
        list[list[int]]: sorted list of [x,y] coordinates representing the
        centre of the answer circle. Sorted by x first, then y
    """
    conts, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    spotCentres = []
    for c in conts:
        # compute enclosing rect to get center points
        x, y, width, height = cv2.boundingRect(c)

        aspect_ratio = width / height
        # check if bounding rectangle of circle roughly matches criteria:
        # (aspect ratio ==1) and (w,h == 25)
        if (
            min_radius * 2 < width < max_radius * 2
            and min_radius * 2 < height < max_radius * 2
            and 0.9 < aspect_ratio < 1.1
        ):
            xCentre = int(x + (width / 2))
            yCentre = int(y + (height / 2))
            cv2.circle(img, (xCentre, yCentre), 1, 0, -1)
            spotCentres.append([xCentre, yCentre])

    # sort by x, then y
    sortedSpots = sorted(spotCentres, key=lambda x: (x[0], x[1]), reverse=False)

    return sortedSpots
