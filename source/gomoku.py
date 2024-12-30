from source.AI import *


def ai_move(ai):
    ai.depth = 3
    ai.alphaBetaPruning(ai.depth, ai.boardValue, ai.nextBound, -math.inf, math.inf, True)
    if ai.isValid(ai.currentI, ai.currentJ):
        move_i, move_j = ai.currentI, ai.currentJ
        ai.updateBound(move_i, move_j, ai.nextBound)
    else:
        ai.updateBound(ai.currentI, ai.currentJ, ai.nextBound)
        bound_sorted = sorted(ai.nextBound.items(), key=lambda el: el[1], reverse=True)
        pos = bound_sorted[0][0]
        move_i = pos[0]
        move_j = pos[1]
        ai.currentI, ai.currentJ = move_i, move_j
    return move_i, move_j
