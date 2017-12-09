import random


class BoringGame:

    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height

    def random_location(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)

        return (x, y)
