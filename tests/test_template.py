import cv2
import pytest
from omr.questions import Template
from omr.utils.img_processing import alignForm, showImg


@pytest.fixture()
def template_from_json():
    template = Template.from_json(
        "tests/test_template.json", "tests/test_template.jpg"
    )
    return template


def test_questions(template_from_json):
    template = template_from_json
    assert len(template.questions) == 2


def test_answers(template_from_json):
    template = template_from_json
    assert len(template.questions[1].answers) == 47


def test_answer_value(template_from_json):
    template = template_from_json
    assert template.questions[0].answers[600].value == "val_600"


def test_answer_x(template_from_json):
    template = template_from_json
    assert template.questions[1].answers[30].x == 2087


def test_question_id(template_from_json):
    template = template_from_json
    assert template.questions[0].question_id == 1


def test_answer_check_fill(template_from_json):
    template = template_from_json
    temp_img = template.img

    assert template.questions[1].answers[42].is_filled(temp_img) == True


def test_answer_check_fill_perc(template_from_json):
    template = template_from_json
    temp_img = template.img
    ans = template.questions[0].answers[100]
    filled_perc = ans.calc_filled_perc(temp_img)
    assert round(filled_perc, 3) == 0.983


def test_align_form():
    img = cv2.imread("tests/test_template.jpg")
    aligned_img = alignForm(img, None)
    showImg(aligned_img)


def test_template_from_img():
    question_ans = {
        0: [i for i in range(0, 700)],
        1: [i for i in range(700, 747)],
    }
    template = Template.from_img_template(
        "tests/test_template.jpg", question_ans
    )
    template.to_json("tests/test_template.json")
    assert template.questions[0].answers[22].x == 124
