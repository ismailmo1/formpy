import cv2
import pytest
from formpy.questions import Form, Template
from formpy.utils import img_processing as ip

from tests.test_template import template_from_json

OEE_FILLED_FORM = "tests/oee_forms/test_filled_form.jpg"


@pytest.fixture()
def form(template_from_json):
    form_img_path = (OEE_FILLED_FORM,)
    template = template_from_json
    form = Form(cv2.imread(form_img_path), template)
    # ip.showImg(form.img)
    return form


def test_form_answer(form):
    img = cv2.cvtColor(form.img, cv2.COLOR_GRAY2BGR)
    for question in form.questions:
        for ans in question.answers:
            if ans.is_filled(form.img):
                color = (0, 0, 255)
                cv2.putText(
                    img,
                    str(question.question_id) + ans.value,
                    (ans.x, ans.y),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.4,
                    color,
                )
            else:
                color = (0, 255, 0)

            ans.mark_answer(img, color=color, circle_thickness=2)

    ip.show_img(img)
