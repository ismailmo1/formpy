from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np

import formpy.utils.img_processing as ip

from .template import Template


class Form:
    """A class to represent a form."""

    def __init__(self, img: np.ndarray, template: Template) -> Form:
        """Initialise form with an associated template that it was built from

        Args:
            img (np.ndarray): a form image read into array
            e.g. via cv2.imread()
            template (Template): template that the form was built from

        Returns:
            Form
        """
        self.template = template
        self.img = self.__resize_img(img)
        self.questions = template.questions

    def __repr__(self) -> str:
        return (
            f"Form with {len(self.questions)} questions and"
            f"{sum([len(i.answers) for i in self.questions])}"
        )

    def __resize_img(self, img: np.ndarray) -> np.ndarray:
        """resize image to be of same size as template

        Args:
            img (np.ndarray): form image read into array e.g. via cv2.imread()
        """
        processed_img = ip.process_img(img)
        resized_img = cv2.resize(
            processed_img,
            (self.template.img.shape[1], self.template.img.shape[0]),
            interpolation=cv2.INTER_LINEAR,
        )
        return resized_img

    def mark_all_answers(self, colour: Tuple[int] = (0, 0, 255)) -> np.ndarray:
        """mark all answers on the form image with the question id and answer value

        Args:
            colour (Tuple[int], optional): color of text and circles to mark
            answers in BGR. Defaults to (0, 0, 255).

        Returns:
            np.ndarray: form image with marked answers, answer values and
            question ids
        """
        colour_img = cv2.cvtColor(cv2.bitwise_not(self.img), cv2.COLOR_GRAY2BGR)

        for qn in self.template.questions:
            answers = qn.answers
            for ans in answers:

                cv2.putText(
                    colour_img,
                    str(qn.question_id) + ans.value,
                    (ans.x, ans.y),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.4,
                    colour,
                )

                ans.mark_answer(colour_img, colour=colour, circle_thickness=-1)

        return colour_img
