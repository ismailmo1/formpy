import cv2
import numpy as np
from formpy.utils.img_processing import (
    align_page,
    get_outer_box,
    process_img,
    thresh_img,
)
from formpy.utils.template_definition import find_spots

from .paths import OEE_TEMPLATE_JPG, OEE_TEMPLATE_SIMPLE_JPG


def test_align_form():
    img = cv2.imread(OEE_TEMPLATE_JPG)
    aligned_img = align_page(img)
    pts = get_outer_box(aligned_img)
    aligned_pts = np.array(
        [[6.0, 5.0], [2152.0, 4.0], [2152.0, 1557.0], [5.0, 1554.0]],
        dtype="float32",
    )
    assert np.array_equal(pts, aligned_pts)


def test_find_spots():
    # load image and align
    simple_img = cv2.imread(OEE_TEMPLATE_SIMPLE_JPG)
    simple_img = process_img(simple_img)

    simple_spots = find_spots(simple_img, max_radius=20, min_radius=10)
    oee_img = cv2.imread(OEE_TEMPLATE_JPG)
    oee_img = process_img(oee_img)

    oee_spots = find_spots(oee_img, max_radius=20, min_radius=10)
    assert len(oee_spots) == 707
    assert len(simple_spots) == 64
