from typing import Tuple

import cv2
import numpy as np


class Answer:
    """A class to represent a single answer circle"""

    def __init__(
        self,
        x: int,
        y: int,
        value: str,
        circle_radius: int,
        filled_threshold: float = 0.8,
    ):
        """Initialise an answer: individual spot corresponding to one possible answer.

        Args:
            x (int): x coordinate of answer
            y (int):  y coordinate of answer
            value (str):  value that the answer represents.
            circle_radius (int): radius of answer spot
            filled_threshold (float, optional): Value from 0.0 - 1.0 used as
            threshold to determine what fill percentage counts as a filled in
            answer circle. Defaults to 0.8.
        """

        self.x = x
        self.y = y
        self.circle_radius = circle_radius
        self.value = value
        self.filled_threshold = filled_threshold

    def is_filled(self, form_img: np.ndarray) -> bool:
        return self.calc_filled_perc(form_img) >= self.filled_threshold

    def mark_answer(
        self,
        form_img: np.ndarray,
        circle_thickness: int = -1,
        colour: Tuple[int] = (0, 0, 255),
    ) -> None:
        """Marks answer on image in place

        Args:
            form_img (np.ndarray): image of form read into array
            e.g. via cv2.imread()
            circle_thickness (int, optional): thickness of circle if a hollow
            circle is required.
            Defaults to -1 (filled circle).
            colour (Tuple[int], optional): colour of circle in BGR.
            Defaults to (0, 0, 255).

        Returns:
            None: marks answer in place so original image is modified
        """
        if len(form_img.shape) != 3:
            form_img = cv2.cvtColor(form_img, cv2.COLOR_GRAY2BGR)

        form_img = cv2.circle(
            form_img,
            (self.x, self.y),
            self.circle_radius,
            colour,
            circle_thickness,
        )

    def calc_filled_perc(self, form_img: np.ndarray) -> float:
        """Returns percentage of circle that is filled in

        Args:
            form_img (np.ndarray): _description_

        Returns:
            float: range from 0.0 - 1.0 representing percentage of circle
            filled in
        """
        # create full black mask with same size as image
        mask = np.zeros(form_img.shape, dtype="uint8")
        # draw white circle on mask to expose the answer circle
        cv2.circle(mask, (self.x, self.y), self.circle_radius, 255, -1)
        mask_pixels = cv2.countNonZero(mask)
        # white pixels on answer == filled in parts of answer
        # (img colour is inverted)
        # bitwise AND == how many white pixels are on the answer
        mask = cv2.bitwise_and(form_img, mask)
        # proportion of white pixels on answer to total white pixels available
        # in answer circle
        pct_filled = cv2.countNonZero(mask) / mask_pixels

        return pct_filled
