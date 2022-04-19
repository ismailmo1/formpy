"""
This module contains the Question, Answer and Form classes.

A Form class will represent one page of a completed form that contains a
list of questions. Each question contains a list of possible answers
which are defined by their x,y coordinates, radius and threshold which
is used to check the filled in status and find answer(s) to question.
"""
# TODO remove class inheritance from form and class - no overlapping methods etc
# TODO make template a property of the form to access question/answer instances
# TODO i.e. form.template.question.answers[0].filled -> True
# TODO or make question/answer directly accessible from form object after it has been instantiated with a template
# TODO i.e. for form.__init__(): self.questions = self.template.questions
from __future__ import annotations

import json
from typing import Tuple

import cv2
import numpy as np

import formpy.utils.img_processing as ip
from formpy.utils.template_definition import find_spots

CIRCLE_RADIUS = 30


class Answer:
    """Class to represent answer and fill status."""

    def __init__(
        self,
        x: int,
        y: int,
        value: str,
        circle_radius: int = CIRCLE_RADIUS,
        filled_threshold: float = 0.8,
    ):
        """Individual spot corresponding to one possible answer.

        Args:
            x (int): x coordinate of answer
            y (int): y coordinate of answer
            circle_radius (int): radius of answer spot
            form_img (np.ndarray): image of form.
            value (str): value that the answer represents.
        """
        self.x = x
        self.y = y
        self.circle_radius = circle_radius
        self.value = value
        self.filled_threshold = filled_threshold

    def is_filled(self, form_img) -> bool:
        return self.calc_filled_perc(form_img) >= self.filled_threshold

    def mark_answer(self, form_img, circle_thickness=-1, color=(0, 0, 255)):
        if len(form_img.shape) != 3:
            raise Exception("img must be in BGR form")
        else:
            cv2.circle(
                form_img,
                (self.x, self.y),
                CIRCLE_RADIUS,
                color,
                circle_thickness,
            )

    def calc_filled_perc(self, form_img) -> float:
        mask = np.zeros(form_img.shape, dtype="uint8")
        cv2.circle(mask, (self.x, self.y), CIRCLE_RADIUS, 255, -1)
        maskPixels = cv2.countNonZero(mask)
        mask = cv2.bitwise_and(form_img, mask)
        pctFilled = cv2.countNonZero(mask) / maskPixels

        return pctFilled


class Question:
    """Class to represent a question containing multiple possible answers."""

    def __init__(
        self, question_id: int, answers: list[Answer], multiple: bool
    ):
        """Return Question instance to represent group of answers belonging to a question.

        Args:
            question_id (int): Unique ID to keep track of question number.
            form_img (np.ndarray): image of form.
            answers (list[Answer]): All spots that reference a possible answer.
            multiple (bool): Set to true if question has multiple possible answers.
        """
        self.answers = answers
        self.multiple = multiple
        self.question_id = question_id

    @property
    def question_img(self, form_img):
        return form_img[
            self.search_area_y0 : self.search_area_y1,
            self.search_area_x0 : self.search_area_x1,
        ]

    @property
    def search_area_x0(self):
        return min([ans.x for ans in self.answers])

    @property
    def search_area_x1(self):
        return max([ans.x for ans in self.answers])

    @property
    def search_area_y0(self):
        return min([ans.y for ans in self.answers])

    @property
    def search_area_y1(self):
        return max([ans.y for ans in self.answers])

    def find_answers(self, img):
        # loop through each answer coordinate and check_fill() -
        # stop when found if multiple = false
        answers = []
        for ans in self.answers:
            if ans.is_filled(img):
                print(ans)
                if self.multiple:
                    answers.append(ans)
                else:
                    return [ans]
        return answers


class Form:
    """Class to represent a single paged form containing questions."""

    def __init__(self, img: np.ndarray, template: Template) -> Form:
        """Form Class with associated template.

        Args:
            width (int): width of image, i.e. np.ndarray.size[0]
            height (int): height of image, i.e. np.ndarray.size[1]
            questions (list): list of Question instances
        """
        self.template = template
        # resize processed image to same as template
        self.img = cv2.resize(
            ip.process_img(img),
            (template.img.shape[1], template.img.shape[0]),
            interpolation=cv2.INTER_LINEAR,
        )
        self.questions = template.questions

    def __repr__(self) -> str:
        return f"Form with {len(self.questions)} questions and {sum([len(i.answers) for i in self.questions])}"

    def mark_all_answers(
        self, found_answers: list, color: Tuple[int] = (0, 0, 255)
    ) -> np.ndarray:
        color_img = cv2.cvtColor(cv2.bitwise_not(self.img), cv2.COLOR_GRAY2BGR)
        for qn in found_answers:
            answers = found_answers[qn]
            for ans in answers:

                cv2.putText(
                    color_img,
                    str(qn.question_id) + ans.value,
                    (ans.x, ans.y),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.4,
                    color,
                )

                ans.mark_answer(color_img, color=color, circle_thickness=-1)

        return color_img


class Template:
    def __init__(self, img: np.ndarray, questions: list[Question]):
        self.questions = questions
        self.img = ip.process_img(img)

    @classmethod
    def from_img_template(
        cls,
        img_path: str,
        question_assigment: dict = None,
        question_config: dict = None,
    ) -> Template:
        """Init template of form from img - ask for user input to assign question to
        answers-question config and to assign multi answer true/false"""

        # load image and align
        raw_img = cv2.imread(img_path)
        img = ip.process_img(raw_img)

        # find all spots - sorted by x then y
        all_spots = find_spots(
            img, max_radius=CIRCLE_RADIUS + 5, min_radius=CIRCLE_RADIUS - 5
        )
        unassigned_answers = all_spots.copy()

        # create colour image to highlight answers in red
        colour_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        # initialise question_id
        question_id = 0
        # list to hold assigned questions
        questions = []
        # keep looping until all found spots are assigned to a questions
        while len(unassigned_answers) > 0:
            # list to hold assigned answers
            assigned_answers = []
            for i, spot in enumerate(all_spots):
                # color unassigned qns in red and assigned in green
                if spot in unassigned_answers:
                    color = (0, 0, 255)
                else:
                    color = (0, 255, 0)
                cv2.putText(
                    colour_img,
                    str(i),
                    (spot[0], spot[1]),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.5,
                    color,
                    1,
                )

            if question_assigment == None:
                assigned_answers_idx = input(
                    f"enter answer id (shown in red) to add to question{question_id}"
                )
                assigned_answers_idx = [
                    int(i.strip()) for i in assigned_answers_idx.split(",")
                ]
            else:
                assigned_answers_idx = question_assigment[question_id]

            # print(f"{question_id}:{assigned_answers_idx}")
            for idx in assigned_answers_idx:
                answer_coords = all_spots[idx]
                unassigned_answers.remove(answer_coords)
                answer = Answer(
                    answer_coords[0], answer_coords[1], f"val_{idx}"
                )
                assigned_answers.append(answer)

            question_id += 1
            if question_config:
                question = Question(
                    question_id=question_id,
                    answers=assigned_answers,
                    multiple=question_config[question_id],
                )

            else:
                question = Question(question_id, assigned_answers, True)

            questions.append(question)

        template = Template(raw_img, questions)

        return template

    @classmethod
    def from_json(cls, json_path: str, img_path: str) -> Form:
        """Return Form instance from pre-configured JSON.

        Args:
            json_path (str): Path to JSON containing configuration for form template.
            img_path (str): Path to image of template.

        Returns:
            Form: Return form instantiated from JSON config and image.
        """

        img = cv2.imread(img_path)

        with open(json_path, "r") as fp:
            template = json.load(fp)

        questions = []

        for question_id in template.keys():
            answers = []

            for answer in template[question_id]:
                x, y = answer["answer_coords"]
                answer_val = answer["answer_val"]
                answers.append(Answer(x, y, answer_val))

            question = Question(
                question_id=int(question_id), answers=answers, multiple=None
            )
            questions.append(question)

        return Template(img, questions)

    @classmethod
    def from_dict(
        cls, img: str | np.ndarray, question_config: dict
    ) -> Template:
        """question_config in form {question_id:{multiple:bool, answers:list[answer]}, question_id2}
        if img is str, assume path and img into array, else assume image is already np array
        """
        img = cv2.imread(img) if type(img) == str else img

        questions = []

        for question_id in question_config.keys():
            answers = []
            multiple = question_config[question_id].get("multiple", False)
            for answer in question_config[question_id]["answers"].values():
                x, y = [
                    int(coord) for coord in answer["answer_coords"].split(",")
                ]
                answer_val = answer["answer_val"]
                answers.append(Answer(x, y, answer_val))

            question = Question(
                question_id=question_id, answers=answers, multiple=multiple
            )
            questions.append(question)

        return Template(img, questions)

    def to_dict(self) -> str:
        """Convert template obj to dict in form of
        {question_id:[
            {answer_val:'val', answer_coords:(x,y)},
            {answer_val:'val', answer_coords:(x,y)}
            ]}"""

        template_dict = {}

        for question in self.questions:
            template_dict[question.question_id] = []

            for answer in question.answers:
                template_dict[question.question_id].append(
                    {
                        "answer_val": answer.value,
                        "answer_coords": (answer.x, answer.y),
                    }
                )
        return template_dict

    @property
    def perspective_matrix(self):
        ordered_pts = ip.get_outer_box(self.img)
        matrix = ip.get_perspective_matrix(ordered_pts)
        return matrix


if __name__ == "__main__":
    template = Template.from_json(
        "tests/test_template.json", "tests/test_template.jpg"
    )

    ip.show_img(template.img)
    ip.show_img(template.processed_img)
