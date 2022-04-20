import cv2
import pytest
from formpy.questions import Form, Template

OEE_FILLED_FORM = "tests/oee_forms/test_filled_form.jpg"
OEE_TEMPLATE_JSON = "tests/oee_forms/test_template.json"
OEE_TEMPLATE_JPG = "tests/oee_forms/test_template.jpg"

@pytest.fixture
def template_from_json():
    """returns template object from oee template json and image"""
    template = Template.from_json(
        OEE_TEMPLATE_JSON,
        OEE_TEMPLATE_JPG,
    )
    return template


@pytest.fixture
def form(template_from_json):
    """returns Form object from oee filled form with oee template"""
    template = template_from_json
    form_img_path = OEE_FILLED_FORM
    form = Form(cv2.imread(form_img_path), template)
    return form

