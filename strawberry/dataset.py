import random
import pathlib


class Dataset:
    def __init__(self, file_path: pathlib.Path) -> None:
        with open(file_path, 'r', encoding='utf-8') as file:
            self._prompts = [line.strip() for line in file if line.strip()]

    def get_random_prompt(self) -> str:
        return random.choice(self._prompts)
