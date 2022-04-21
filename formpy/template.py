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
    """A class to represent a template that a form is built from.

    Class Methods:
        from_image_template:
            initialise template from an image and configuration dictionaries
        from_json:
            initialise template from a json file
        from_dict:
            initialise template from a dictionary object

    Methods:
        to_dict:
            convert template to a dictionary object representation
        to_json:
            convert template to a json string representation

    """

    def __init__(
        self, img: np.ndarray, questions: list[Question], circle_radius: int
    ):
        self.questions = questions
        self.img = ip.process_img(img)
        self.circle_radius = circle_radius

    @classmethod
    def from_img_template(
        cls,
        img_path: str,
        circle_radius: int,
        question_assignment: dict,
        question_config: dict = None,
    ) -> Template:
        """Initialise template from img

        Args:
            img_path (str): path to load image of template from
            circle_radius (int): size of the answer circles
            question_assignment (dict): map of question id to list of answer ids.
            question_config (dict, optional): map of question id to true/false flag for multiple answers. Defaults to None.

        Returns:
            Template: _description_
        """

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

            if question_assignment == None:
                assigned_answers_idx = input(
                    f"enter answer id (shown in red) to add to question{question_id}"
                )
                assigned_answers_idx = [
                    int(i.strip()) for i in assigned_answers_idx.split(",")
                ]
            else:
                assigned_answers_idx = question_assignment[question_id]

            # print(f"{question_id}:{assigned_answers_idx}")
            for idx in assigned_answers_idx:
                answer_coords = all_spots[idx]
                unassigned_answers.remove(answer_coords)
                answer = Answer(
                    x=answer_coords[0],
                    y=answer_coords[1],
                    value=f"val_{idx}",
                    circle_radius=circle_radius,
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
            see from_dict() for format of JSON.
            img_path (str): Path to image of template.

        Returns:
            Form: Return form instantiated from JSON config and image.
        """

        with open(json_path, "r") as fp:
            template = json.load(fp)

        return cls.from_dict(template, img_path)

    @classmethod
    def from_dict(cls, template: dict, img_path: str) -> Template:
        """Create template from dictionary of template config.

        Args:
            template (dict): template config in form:
            {config:
                {radius:<CIRCLE_RADIUS>},
            questions:
                {question_id:
                    [
                        {answer_val:<ANSWER_VAL>,
                        answer_coords: [<X_COORD>, <Y_COORD>]}
                    ]
                }
            }
            img_path (str): path to image of form

        Returns:
            Template
        """
        img = cv2.imread(img_path)

        question_objs = []
        questions = template["questions"]
        question_ids = questions.keys()
        circle_radius = template["config"]["radius"]
        for question_id in question_ids:
            answers = []

            for answer in questions[question_id]:
                x, y = answer["answer_coords"]
                answer_val = answer["answer_val"]
                answers.append(Answer(x, y, answer_val, circle_radius))

            question = Question(
                question_id=int(question_id), answers=answers, multiple=None
            )
            question_objs.append(question)

        return Template(img, question_objs, circle_radius)

    def to_dict(self) -> dict:
        """Convert template obj to dictionary in form of
        {config:
                {radius:<CIRCLE_RADIUS>},
            questions:
                {question_id:
                    [
                        {answer_val:<ANSWER_VAL>,
                        answer_coords: [<X_COORD>, <Y_COORD>]}
                    ]
                }
            }
        Return:
            dict : python dictionary object with format described above
        """
        # TODO add circle radius metadata

        question_dict = {}

        for question in self.questions:
            question_dict[question.question_id] = []

            for answer in question.answers:
                question_dict[question.question_id].append(
                    {
                        "answer_val": answer.value,
                        "answer_coords": (answer.x, answer.y),
                    }
                )
        template_dict = {}
        template_dict["config"]["radius"] = self.circle_radius
        template_dict["questions"] = question_dict
        return template_dict

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @property
    def perspective_matrix(self) -> np.ndarray:
        """return perspective matrix from outer box detected in image
        used for alignment of template

        Returns:
            np.ndarray: perspective matrix
        """
        ordered_pts = ip.get_outer_box(self.img)
        matrix = ip.get_perspective_matrix(ordered_pts)
        return matrix
