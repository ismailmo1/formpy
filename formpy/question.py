from __future__ import annotations

import numpy as np

from .answer import Answer


class Question:
    """A class to represent a Question on a form or template."""

    def __init__(self, question_id: int, answers: list[Answer], multiple: bool):
        """Return Question instance to represent group of answers belonging to
        a question.

        Args:
            question_id (int): Unique ID to keep track of question number.
            form_img (np.ndarray): image of form.
            answers (list[Answer]): All spots that reference a possible answer.
            multiple (bool): Set to true if question has multiple possible
            answers.
        """
        self.answers = answers
        self.multiple = multiple
        self.question_id = question_id

    @property
    def question_img(self, form_img: np.ndarray) -> np.ndarray:
        """return cropped form image of the question

        Args:
            form_img (np.ndarray): form image read into array
            e.g. via cv2.imread()

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
            list[Answer]: answers that have been marked i.e. return true for
            answer.check_fill()
            if question.multiple == False then the first marked answer will be
            returned and length
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
