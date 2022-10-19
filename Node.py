import numpy as np
class Node:
    def __init__(self, pos):
        self.pos = pos
        self.entering_roads = []
        self.exiting_roads = []