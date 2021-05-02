import numpy as np


class Game:
    def __init__(self, size=6):
        self.size = size
        self.initial = 4
        self.to_win = self.size * self.initial + 1
        self.houses = np.full((2, size),
                              fill_value=4,
                              dtype=int)
        self.score = np.zeros(2, dtype=int)
        self.player = 0
        self.done = False
        self.winner = 0.5

    def __str__(self):
        s = '\n'
        s += f' {self.score[1]:2}  '
        s += ''.join(f'({x:2} )' for x in self.houses[1, ::-1])
        s += '\n'
        s += '     ' + ' --- ' * self.size + '\n'
        s += '     '
        s += ''.join(f'({x:2} )' for x in self.houses[0, :])
        s += f'  {self.score[0]:2}'
        s += '\n'
        return s

    def get_state(self, player):
        if self.player == 0:
            return np.concatenate((self.houses[0],
                                   self.houses[1, ::-1]))
        else:
            return np.concatenate((self.houses[1, ::-1],
                                   self.houses[0]))

    def check_done(self):
        if self.score[0] >= self.to_win:
            self.done = True
            self.winner = 0
        elif self.score[1] >= self.to_win:
            self.done = True
            self.winner = 1
        elif self.score[0] == self.score[1] == self.to_win - 1:
            self.done = True
            self.winner = 0.5
        elif self.houses[0].max() == 0:
            self.done = True
            self.winner = 0
        elif self.houses[1].max() == 0:
            self.done = True
            self.winner = 1
        return self.done

    def move(self, house):
        '''
        Have current player (self.player) move
        Parameters:
            house : (int) house to sow, starting with the left-most as 0
        Returns: (int) number of captures
        '''
        save = self.houses.copy()
        seeds = self.houses[self.player, house]
        self.houses[self.player, house] = 0
        current_house = house + 1
        current_side = self.player
        while seeds > 0:
            if current_house == self.size:
                current_house = 0
                current_side = 1 - current_side
            # if we aren't back at the starting point
            if current_house != house or current_side != self.player:
                self.houses[current_side, current_house] += 1
                seeds -= 1
            current_house += 1

        captures = self.capture(current_side, current_house-1)

        self.player = 1 - self.player
        self.check_done()
        return captures

    def capture(self, side, house):
        '''
        Capture stones (if play in current side)
        Parameters:
            house: house
        '''
        captures = 0

        if side == self.player:
            return captures

        # check for grand slam
        if (house == self.size and
            np.all((self.houses[side] == 2) |
                   (self.houses[side] == 3))):
            return captures

        current_house = house
        while (self.houses[side, current_house] in (2, 3) and
               current_house >= 0):
            captures += self.houses[side, house]
            self.houses[side, house] = 0
            current_house -= 1
        self.score[1-side] += captures
        return captures


if __name__ == '__main__':
    b = Game()
    print(b)
    b.move(2)
    print(b)

    b.move(5)
    print(b)

    b.move(1)
    print(b)

    b.move(4)
    print(b)
