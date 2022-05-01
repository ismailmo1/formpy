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
    """A class to represent a template that a form is built from."""

    def __init__(self, img: np.ndarray, questions: list[Question], circle_radius: int):
        """initialise template

        Args:
            img (np.ndarray): image of template read in using e.g. cv2.imread()
            questions (list[Question]): list of questions on template
            circle_radius (int): size of answer circles
        """
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
            question_assignment (dict): map of question id to list of answer
            id.
            question_config (dict, optional): map of question id to true/false
            flag for multiple answers. Defaults to None.

        Returns:
            Template
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

            if question_assignment is None:
                assigned_answers_idx = input(
                    f"enter answer id (shown in red) to add to question: \
                        {question_id}"
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
            img_path (str): Path to image of template.
            json_path (str): Path to JSON containing configuration for form
            template, see format below.

        .. code-block:: json

            {"config":
                    {"radius":"<CIRCLE_RADIUS>"},
                "questions":
                    {"question_id":
                        {
                            "multiple":<BOOL>,
                            "answers":
                            [
                                {"answer_val":"<ANSWER_VAL>",
                                "answer_coords": ["<X_COORD>", "<Y_COORD>"]}
                            ]
                        }
                    }
                }


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
            template (dict): template config as shown below.

        .. code-block:: python

            {"config":
                    {"radius":"<CIRCLE_RADIUS>"},
                "questions":
                    {"question_id":
                        {
                            "multiple":<BOOL>,
                            "answers":
                            [
                                {"answer_val":"<ANSWER_VAL>",
                                "answer_coords": ["<X_COORD>", "<Y_COORD>"]}
                            ]
                        }
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
            multiple = questions[question_id]["multiple"]
            for answer in questions[question_id]["answers"]:
                x, y = answer["answer_coords"]
                answer_val = answer["answer_val"]
                answers.append(Answer(x, y, answer_val, circle_radius))

            question = Question(
                question_id=int(question_id),
                answers=answers,
                multiple=multiple,
            )
            question_objs.append(question)

        return Template(img, question_objs, circle_radius)

    def to_dict(self) -> dict:
        """Convert template obj to dictionary. See docs for dictionary structure.

        Return:
            dict : dictionary representation of template as below.

        .. code-block:: python

            {"config":
                    {"radius":"<CIRCLE_RADIUS>"},
                "questions":
                    {"question_id":
                        {
                            "multiple":<BOOL>,
                            "answers":
                            [
                                {"answer_val":"<ANSWER_VAL>",
                                "answer_coords": ["<X_COORD>", "<Y_COORD>"]}
                            ]
                        }
                    }
                }

        """

        question_dict = {}

        for question in self.questions:
            question_dict[question.question_id] = []
            question_dict[question.question_id]["multiple"] = question.multiple
            question_dict[question.question_id]["answers"] = []

            for answer in question.answers:
                question_dict[question.question_id]["answers"].append(
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
        """Convert template into json string representation.

        Returns:
            str: json string in format below.

        .. code-block:: json

            {"config":
                    {"radius":"<CIRCLE_RADIUS>"},
                "questions":
                    {"question_id":
                        {
                            "multiple":<BOOL>,
                            "answers":
                            [
                                {"answer_val":"<ANSWER_VAL>",
                                "answer_coords": ["<X_COORD>", "<Y_COORD>"]}
                            ]
                        }
                    }
                }

        """
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
