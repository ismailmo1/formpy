import cv2
import numpy as np


class Answer:
    """Class to represent answer and fill status."""

    def __init__(
        self,
        x: int,
        y: int,
        value: str,
        circle_radius: int ,
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
                self.circle_radius,
                color,
                circle_thickness,
            )

    def calc_filled_perc(self, form_img) -> float:
        mask = np.zeros(form_img.shape, dtype="uint8")
        cv2.circle(mask, (self.x, self.y), self.circle_radius, 255, -1)
        maskPixels = cv2.countNonZero(mask)
        mask = cv2.bitwise_and(form_img, mask)
        pctFilled = cv2.countNonZero(mask) / maskPixels

        return pctFilled

