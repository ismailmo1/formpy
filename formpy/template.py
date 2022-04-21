
from __future__ import annotations

import json
from typing import TYPE_CHECKING

import cv2
import numpy as np

import formpy.utils.img_processing as ip
from formpy.answer import Answer
from formpy.question import Question
from formpy.utils.template_definition import find_spots

if TYPE_CHECKING:
    from formpy.form import Form

class Template:
    def __init__(self, img: np.ndarray, questions: list[Question], circle_radius:int):
        self.questions = questions
        self.img = ip.process_img(img)
        self.circle_radius = circle_radius

    @classmethod
    def from_img_template(
        cls,
        img_path: str,
        circle_radius: int, 
        question_assigment: dict = None,
        question_config: dict = None
    ) -> Template:
        """Init template of form from img - ask for user input to assign question to
        answers-question config and to assign multi answer true/false"""

        # load image and align
        raw_img = cv2.imread(img_path)
        img = ip.process_img(raw_img)

        # find all spots - sorted by x then y
        all_spots = find_spots(
            img, max_radius=circle_radius + 5, min_radius=circle_radius - 5
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

        template = Template(raw_img, questions, circle_radius)

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
        #TODO add circle radius metadata
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
        #TODO add circle radius metadata

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
        #TODO add circle radius metadata

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
