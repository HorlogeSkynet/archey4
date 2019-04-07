import os


class Shell:
    def __init__(self, not_detected=None):
        self.value = os.getenv(
            'SHELL',
            not_detected
        )
