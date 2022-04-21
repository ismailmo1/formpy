from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np

import formpy.utils.img_processing as ip

from .template import Template


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

