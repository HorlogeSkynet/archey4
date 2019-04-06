import os


class User:
    def __init__(self, not_detected=None):
        self.value = os.getenv(
            'USER',
            not_detected
        )

