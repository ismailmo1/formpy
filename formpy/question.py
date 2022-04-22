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

import numpy as np

from .answer import Answer


class Question:
    """A class to represent a Question on a form or template.

    Methods:
        find_answers: find the marked answer(s) for the questions

    Properties:
        question_img: return a cropped image of the question

    """

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
    def question_img(self, form_img: np.ndarray) -> np.ndarray:
        """return cropped form image of the question

        Args:
            form_img (np.ndarray): form image read into an array e.g. through cv2.imread()

        Returns:
            np.ndarray: cropped form image
        """
        return form_img[
            self.__search_area_y0 : self.__search_area_y1,
            self.__search_area_x0 : self.__search_area_x1,
        ]

    @property
    def __search_area_x0(self):
        return min([ans.x for ans in self.answers])

    @property
    def __search_area_x1(self):
        return max([ans.x for ans in self.answers])

    @property
    def __search_area_y0(self):
        return min([ans.y for ans in self.answers])

    @property
    def __search_area_y1(self):
        return max([ans.y for ans in self.answers])

    def find_answers(self, img: np.ndarray) -> list[Answer]:
        """Find marked answer(s) for question

        Args:
            img (np.ndarray): image of the form

        Returns:
            list[Answer]: answers that have been marked i.e. return true for answer.check_fill()
            if question.multiple == False then the first marked answer will be returned and length
            of this list will be 1.
        """

        answers = []
        for ans in self.answers:
            if ans.is_filled(img):
                if self.multiple:
                    answers.append(ans)
                else:
                    return [ans]
        return answers
