import random

import numpy as np

from schemas.commo.ttypes import Location

PROXIMITY_THRESHOLD = 25


class BoringGame:

    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height

    def random_location(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)

        return Location(x=x, y=y)

    def within_proximity(self, loc1, loc2):
        l2_dist = np.linalg.norm(np.array([loc1.x, loc1.y]) - np.array([loc2.x, loc2.y]))

        return l2_dist <= PROXIMITY_THRESHOLD
