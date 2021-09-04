import cv2
import pytest
from omr.questions import Form, Template


@pytest.fixture()
def form():
    temp_img = cv2.imread("tests/test_template.jpg")
    template = Template.from_json("tests/test_template.json", temp_img)
    form = Form(temp_img, template)
    return form


def test_form_answer():
    pass
