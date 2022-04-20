import cv2
import numpy as np
from formpy.questions import Template
from formpy.utils.img_processing import align_page, get_outer_box

OEE_TEMPLATE_JSON = "tests/oee_forms/test_template.json"
OEE_TEMPLATE_JPG = "tests/oee_forms/test_template.jpg"

OEE_TEMPLATE_SIMPLE_JSON = "tests/oee_forms/test_template_simple.json"
OEE_TEMPLATE_SIMPLE_JPG = "tests/oee_forms/test_template_simple.jpg"


def test_questions(template_from_json):
    template = template_from_json
    assert len(template.questions) == 2


def test_answers(template_from_json):
    template = template_from_json
    assert len(template.questions[1].answers) == 307


def test_answer_value(template_from_json):
    template = template_from_json
    assert template.questions[0].answers[350].value == "val_350"


def test_answer_x(template_from_json):
    template = template_from_json
    assert template.questions[1].answers[30].x == 1534


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
    assert round(filled_perc, 3) == 1.0


def test_align_form():
    img = cv2.imread(OEE_TEMPLATE_JPG)
    aligned_img = align_page(img)
    pts = get_outer_box(aligned_img)
    aligned_pts = np.array(
        [[6.0, 5.0], [2152.0, 4.0], [2152.0, 1557.0], [5.0, 1554.0]],
        dtype="float32",
    )
    assert np.array_equal(pts, aligned_pts)


def test_template_from_img():
    question_ans = {
        0: [i for i in range(0, 400)],
        1: [i for i in range(400, 707)],
    }
    template = Template.from_img_template(OEE_TEMPLATE_JPG, question_ans)

    # uncomment below to show answers on img
    img = cv2.cvtColor(template.img, cv2.COLOR_GRAY2BGR)
    for question in template.questions:
        for ans in question.answers:
            ans.mark_answer(img, -1)

    cv2.imwrite("test.jpeg",img)
    # template.to_json(OEE_TEMPLATE_JSON)
    assert template.questions[0].answers[22].x == 123


def test_simple_template_from_img():
    question_ans = {
        0: [i for i in range(0, 8)],
        1: [i for i in range(8, 16)],
        2: [i for i in range(16, 24)],
        3: [i for i in range(24, 32)],
        4: [i for i in range(32, 40)],
        5: [i for i in range(40, 48)],
        6: [i for i in range(48, 56)],
        7: [i for i in range(56, 64)],
    }
    template = Template.from_img_template(
        OEE_TEMPLATE_SIMPLE_JPG, question_ans
    )

    # uncomment below to show answers on img
    # img = cv2.cvtColor(template.img, cv2.COLOR_GRAY2BGR)
    # for question in template.questions:
    #     for ans in question.answers:
    #         ans.mark_answer(img, -1)

    # show_img(img)
    # template.to_json(OEE_TEMPLATE_SIMPLE_JSON)
    assert template.questions[5].answers[4].x == 1619
    assert template.questions[2].answers[1].y == 465
