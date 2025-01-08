import random
import pathlib


class Dataset:
    """
    Represents a dataset of textual prompts loaded from a file.

    This class provides functionality to load prompts from a file and retrieve
    a random prompt for use in experiments or simulations.

    Attributes:
        _prompts (list of str): A list of prompts loaded from the specified file.
    """

    def __init__(self, file_path: pathlib.Path) -> None:
        """
        Initializes the Dataset instance by loading prompts from the given file.

        Args:
            file_path (pathlib.Path): The path to the file containing prompts.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            IOError: If there is an issue reading the file.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            self._prompts = [line.strip() for line in file if line.strip()]

    def get_random_prompt(self) -> str:
        """
        Retrieves a random prompt from the dataset.

        Returns:
            str: A randomly selected prompt from the dataset.

        Raises:
            IndexError: If the dataset is empty.
        """
        return random.choice(self._prompts)
