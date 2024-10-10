import math
import sys
import source.utils as utils

sys.setrecursionlimit(1500)
N = 15  # board size 15x15


class GomokuAI():
    def __init__(self, depth=3):
        self.depth = depth  # default depth set to 3
        self.boardMap = [[0 for j in range(N)] for i in range(N)]
        self.currentI = -1
        self.currentJ = -1
        self.nextBound = {}  # to store possible moves to be checked (i,j)
        self.boardValue = 0
        self.turn = 0
        self.lastPlayed = 0
        self.emptyCells = N * N
        self.patternDict = utils.create_pattern_dict()  # dictionary containing all patterns with corresponding score
        self.zobristTable = utils.init_zobrist()
        self.rollingHash = 0
        self.TTable = {}

    def drawBoard(self):
        for i in range(N):
            for j in range(N):
                if self.boardMap[i][j] == 1:
                    state = 'x'
                if self.boardMap[i][j] == -1:
                    state = 'o'
                if self.boardMap[i][j] == 0:
                    state = '.'
                print('{}|'.format(state), end=" ")
            print()
        print()

    def isValid(self, i, j, state=True):
        if i < 0 or i >= N or j < 0 or j >= N:
            return False
        if state:
            if self.boardMap[i][j] != 0:
                return False
            else:
                return True
        else:
            return True

    def setState(self, i, j, state):
        assert state in (-1, 0, 1), 'The state inserted is not -1, 0 or 1'
        self.boardMap[i][j] = state
        self.lastPlayed = state

    def countDirection(self, i, j, xdir, ydir, state):
        count = 0
        for step in range(1, 5):
            if xdir != 0 and (j + xdir * step < 0 or j + xdir * step >= N):
                break
            if ydir != 0 and (i + ydir * step < 0 or i + ydir * step >= N):
                break
            if self.boardMap[i + ydir * step][j + xdir * step] == state:
                count += 1
            else:
                break
        return count

    def isFive(self, i, j, state):
        directions = [[(-1, 0), (1, 0)], [(0, -1), (0, 1)], [(-1, 1), (1, -1)], [(-1, -1), (1, 1)]]
        for axis in directions:
            axis_count = 1
            for (xdir, ydir) in axis:
                axis_count += self.countDirection(i, j, xdir, ydir, state)
                if axis_count >= 5:
                    return True
        return False

    def childNodes(self, bound):
        for pos in sorted(bound.items(), key=lambda el: el[1], reverse=True):
            yield pos[0]

    def updateBound(self, new_i, new_j, bound):
        played = (new_i, new_j)
        if played in bound:
            bound.pop(played)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1), (-1, -1), (1, 1)]
        for dir in directions:
            new_col = new_j + dir[0]
            new_row = new_i + dir[1]
            if self.isValid(new_row, new_col) and (new_row, new_col) not in bound:
                bound[(new_row, new_col)] = 0

    def countPattern(self, i_0, j_0, pattern, score, bound, flag):
        directions = [(1, 0), (1, 1), (0, 1), (-1, 1)]
        length = len(pattern)
        count = 0
        for dir in directions:
            steps_back = min(5, j_0, i_0) if dir[0] == 1 else min(5, N - 1 - j_0, i_0)
            i_start = i_0 - steps_back * dir[1]
            j_start = j_0 - steps_back * dir[0]
            z = 0
            while z <= steps_back:
                i_new = i_start + z * dir[1]
                j_new = j_start + z * dir[0]
                index = 0
                remember = []
                while index < length and self.isValid(i_new, j_new, state=False) and self.boardMap[i_new][j_new] == \
                        pattern[index]:
                    if self.isValid(i_new, j_new):
                        remember.append((i_new, j_new))
                    i_new = i_new + dir[1]
                    j_new = j_new + dir[0]
                    index += 1
                if index == length:
                    count += 1
                    for pos in remember:
                        if pos not in bound:
                            bound[pos] = 0
                        bound[pos] += flag * score
                    z += index
                else:
                    z += 1
        return count

    def evaluate(self, new_i, new_j, board_value, turn, bound):
        value_before = 0
        value_after = 0
        for pattern in self.patternDict:
            score = self.patternDict[pattern]
            value_before += self.countPattern(new_i, new_j, pattern, abs(score), bound, -1) * score
            self.boardMap[new_i][new_j] = turn
            value_after += self.countPattern(new_i, new_j, pattern, abs(score), bound, 1) * score
            self.boardMap[new_i][new_j] = 0
        return board_value + value_after - value_before

    def alphaBetaPruning(self, depth, board_value, bound, alpha, beta, maximizingPlayer):
        if depth <= 0 or (self.checkResult() != None):
            return board_value

        if self.rollingHash in self.TTable and self.TTable[self.rollingHash][1] >= depth:
            return self.TTable[self.rollingHash][0]

        if maximizingPlayer:
            max_val = -math.inf
            for child in self.childNodes(bound):
                i, j = child[0], child[1]
                new_bound = dict(bound)
                new_val = self.evaluate(i, j, board_value, 1, new_bound)
                self.boardMap[i][j] = 1
                self.rollingHash ^= self.zobristTable[i][j][0]
                self.updateBound(i, j, new_bound)
                eval = self.alphaBetaPruning(depth - 1, new_val, new_bound, alpha, beta, False)
                if eval > max_val:
                    max_val = eval
                    if depth == self.depth:
                        self.currentI = i
                        self.currentJ = j
                        self.boardValue = eval
                        self.nextBound = new_bound
                alpha = max(alpha, eval)
                self.boardMap[i][j] = 0
                self.rollingHash ^= self.zobristTable[i][j][0]
                del new_bound
                if beta <= alpha:
                    break
            utils.update_TTable(self.TTable, self.rollingHash, max_val, depth)
            return max_val
        else:
            min_val = math.inf
            for child in self.childNodes(bound):
                i, j = child[0], child[1]
                new_bound = dict(bound)
                new_val = self.evaluate(i, j, board_value, -1, new_bound)
                self.boardMap[i][j] = -1
                self.rollingHash ^= self.zobristTable[i][j][1]
                self.updateBound(i, j, new_bound)
                eval = self.alphaBetaPruning(depth - 1, new_val, new_bound, alpha, beta, True)
                if eval < min_val:
                    min_val = eval
                    if depth == self.depth:
                        self.currentI = i
                        self.currentJ = j
                        self.boardValue = eval
                        self.nextBound = new_bound
                beta = min(beta, eval)
                self.boardMap[i][j] = 0
                self.rollingHash ^= self.zobristTable[i][j][1]
                del new_bound
                if beta <= alpha:
                    break
            utils.update_TTable(self.TTable, self.rollingHash, min_val, depth)
            return min_val

    def firstMove(self):
        self.currentI, self.currentJ = 7, 7
        self.setState(self.currentI, self.currentJ, 1)

    def checkResult(self):
        if self.isFive(self.currentI, self.currentJ, self.lastPlayed) and self.lastPlayed in (-1, 1):
            return self.lastPlayed
        elif self.emptyCells <= 0:
            return 0
        else:
            return None

    def getWinner(self):
        if self.checkResult() == 1:
            return 'Gomoku AI wins!'
        if self.checkResult() == -1:
            return 'Human wins!'
        else:
            return 'No winner yet'
