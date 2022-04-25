from __future__ import annotations

import cv2
import numpy as np


class ImageAlignmentError(Exception):
    pass


def show_img(img: np.ndarray | list[np.ndarray], time: int = 0) -> None:
    """Utility to display all images in a window with window name = window(i)
    where i = index

    Args:
        img (np.ndarray | list[np.ndarray]): image to display as
        array read into array e.g. via cv2.imread()
        time (int, optional): Delay time in millisec to display window.
        Defaults to 0.
    """

    if type(img) != list:
        cv2.imshow("window", img)
    else:
        for i, im in enumerate(img):
            cv2.imshow("window" + str(i), im)
    cv2.waitKey(time)
    if time == 0:
        cv2.destroyAllWindows()


def thresh_img(
    img: np.ndarray, min_thresh: int = 100, max_thresh: int = 255
) -> np.ndarray:
    """Convert image to binary black and white image using thresholds

    Args:
        img (np.ndarray): image to threshold read into array
        e.g. via cv2.imread()
        min_thresh (int, optional): Pixels below this grayscale value will be
        converted to white pixels . Defaults to 100.
        max_thresh (int, optional): Pixels above this grayscale value will be
        converted to black pixels. Defaults to 255.

    Returns:
        np.ndarray: thresholded image with only black or white pixels
    """
    if len(img.shape) == 3 and img.shape[2] == 3:
        # three channels aka coloured img
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        # img already greyscale
        img_gray = img
    _, img_thresh = cv2.threshold(
        img_gray, min_thresh, max_thresh, cv2.THRESH_BINARY_INV
    )

    return img_thresh


def get_perspective_matrix(ordered_corner_pts: np.ndarray) -> np.ndarray:
    """Calculates a matrix from the corners of the aligment feature

    Args:
        ordered_corner_pts (np.ndarray): Corner points of rectangle alignment
        feature,
        ordered from top-left clockwise

    Returns:
        np.ndarray: perspective matrix to use to align page using
        cv2.getPerspectiveTransform()
    """
    # unpack ordered pts to find widths and heights
    (tl, tr, br, bl) = ordered_corner_pts

    # use euclidean distances (finally a use for pythagoras lol) -
    # taken from pyimagesearch.com
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))

    # find max heights/widths - i.e from top/bottom, left/right
    maxWidth = max(int(widthA), int(widthB))
    maxHeight = max(int(heightA), int(heightB))

    # initialise dst array for transformation -
    # i.e. map corners of img onto this matrix
    dst = np.array(
        [
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1],
        ],
        dtype="float32",
    )

    return dst


def get_outer_box(img: np.ndarray) -> np.ndarray:
    """Finds the rectangle alignment feature in the image

    Args:
        img (np.ndarray): image to detect the outer box from

    Raises:
        ImageAlignmentError: if outer box is not detected

    Returns:
        np.ndarray: returns the 4 coordinates of the corners of the rectangle
        alignment feature,
        ordered from top-left clockwise
    """
    # enhance image to improve contour detection
    if len(img.shape) == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img
    img_bilat = cv2.bilateralFilter(img_gray, 11, 500, 0)
    img_edge = cv2.Canny(img_bilat, 20, 100)

    # find outer rectangle

    conts, _ = cv2.findContours(img_edge, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # find top 10 biggest contours by area
    areas = []
    for c in conts:
        areas.append([c, cv2.contourArea(c), cv2.arcLength(c, True)])

    # sort by arclength and area - (neither work consistently for now :( )
    length_sort = sorted(areas, key=lambda x: x[2], reverse=True)
    area_sort = sorted(areas, key=lambda x: x[1], reverse=True)

    area_conts = [i[0] for i in area_sort]
    length_conts = [i[0] for i in length_sort]

    area_cont_max_x = max(i[0][0] for i in area_conts[0])
    area_cont_max_y = max(i[0][1] for i in area_conts[0])
    length_cont_max_x = max(i[0][0] for i in length_conts[0])
    length_cont_max_y = max(i[0][1] for i in length_conts[0])

    if area_cont_max_x >= length_cont_max_x:
        if area_cont_max_y >= length_cont_max_y:
            # outer contour found with area method
            top_contours = area_sort[:5]
        else:
            raise ImageAlignmentError("Image Alignment Failed: outer box not detected")
    elif area_cont_max_x < length_cont_max_x:
        if area_cont_max_y < length_cont_max_y:
            # outer contour found with length method
            top_contours = length_sort[:5]
        else:
            raise ImageAlignmentError("Image Alignment Failed: outer box not detected")

    # find outer rectangle
    for c in top_contours:
        # approximate curve to check if its rectangularish
        approx = cv2.approxPolyDP(c[0], 0.0015 * c[2], True)
        # check number of corners in apprximated polygon
        if len(approx) >= 4:
            pts = np.zeros((4, 2), dtype="float32")
            # top left
            pts[0] = approx[np.argmin(approx.sum(axis=2))]
            # top right
            pts[2] = approx[np.argmax(approx.sum(axis=2))]

            # smallest difference x-y = top right
            pts[1] = approx[np.argmin(np.diff(approx, axis=2))]
            # largest difference x-y = bottom left
            pts[3] = approx[np.argmax(np.diff(approx, axis=2))]

            break

    return pts


def align_page(img: np.ndarray, corner_pts: np.ndarray | None = None) -> np.ndarray:
    """Applys perspective transform to align the image using a rectangle
    alignment feature on the image

    Args:
        img (np.ndarray): image of form or template read into array
        e.g. via cv2.imread()
        corner_pts (np.ndarray | None, optional): 4 coordinates of the corners
        of the rectangle alignment feature,
        ordered from top-left clockwise. Defaults to None, and the rectangle
        feature will be detected automatically.

    Returns:
        np.ndarray: aligned image
    """

    if corner_pts is not None:
        ordered_pts = corner_pts
    else:
        ordered_pts = get_outer_box(img)

    dst = get_perspective_matrix(ordered_pts)

    width = int(dst[2][0])
    height = int(dst[2][1])

    # transformation matrix
    matrix = cv2.getPerspectiveTransform(ordered_pts, dst)

    # transform image and resize to original size
    # (map spots to correct locations)
    img_warp = cv2.warpPerspective(img, matrix, (width, height))

    # TODO add rotation feature (separate func probably) -
    # TODO add detection mechanism for choosing rotation
    # e.g. top left spot or something

    # if img_warp.shape[0] > img_warp.shape[1]:
    #     img_warp = cv2.rotate(img_warp, cv2.ROTATE_90_CLOCKWISE)

    return img_warp


def process_img(img: np.ndarray) -> np.ndarray:
    """Converts image to binary black & white and aligns the page using the
    rectangle alignment feature

    Args:
        img (np.ndarray): image read into array e.g. via cv2.imread()

    Returns:
        np.ndarray: binary black and white, aligned image
    """

    img_thresh = thresh_img(img)
    img_aligned = align_page(img_thresh)
    return img_aligned
