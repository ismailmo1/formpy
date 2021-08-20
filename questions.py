"""
This module contains the Question, Answer and Form classes.

A Form class will represent one page of a completed form that contains a
list of questions. Each question contains a list of possible answers
which are defined by their x,y coordinates, radius and threshold which
is used to check the filled in status and find answer(s) to question.
"""


class Answer:
    """Class to represent answer and fill status."""

    def __init__(
        self, x: int, y: int, circle_radius: int, fill_threshold: float
    ):
        """Init answer class.

        Args:
            x (int): x coordinate of answer
            y (int): y coordinate of answer
            circle_radius (int): size of circle to overlay on spot from
            fill_threshold (float): fraction of circle should be filled in
            to register in check_fill
        """
        pass

    def check_fill(self) -> bool:
        """Return true if answer is filled in above the fill_threshold.

        Returns:
            bool: true if filled in
        """
        pass


class Question:
    """Class to represent a question."""

    def __init__(self, answers: list[Answer], multiple: bool):
        pass

    def find_answers(self):
        pass


class Form:
    """Class to represent a single paged form."""

    def __init__(self, x_size: int, y_size: int, questions: list(Question)):
        """Init Form Class from list of questions."""
        pass

    @classmethod
    def from_template(cls):
        """Init Form from template of form."""
        # TODO convert template to img i.e. from word, excel or pdf
        # TODO add logic to detect questions from img
        # TODO construct form class from list of detected questions
        pass
