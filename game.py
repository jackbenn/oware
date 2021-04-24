import numpy as np

class Board:
    def __init__(self, size=6):
        self.size = size
        self.initial = 4
        self.houses = np.full((2, size),
                               fill_value=4,
                               dtype=int)

    def __str__(self):
        s = '\n'
        s += '  ' + ' '.join(f'{x:2}' for x in self.houses[1, ::-1])
        s += '\n'
        s += '  ' + ' '.join(f'{x:2}' for x in self.houses[0, :])
        s += '\n'
        return s

if __name__ == '__main__':
    b = Board()
    print(b)
