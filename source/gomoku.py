import math
import time

from multiprocessing import Process, Queue


def ai_move_logic(ai, queue):
    ai.depth = 3
    ai.alphaBetaPruning(ai.depth, ai.boardValue, ai.nextBound, -math.inf, math.inf, True)
    if ai.isValid(ai.currentI, ai.currentJ):
        queue.put((ai.currentI, ai.currentJ))
    else:
        ai.updateBound(ai.currentI, ai.currentJ, ai.nextBound)
        bound_sorted = sorted(ai.nextBound.items(), key=lambda el: el[1], reverse=True)
        pos = bound_sorted[0][0]
        queue.put((pos[0], pos[1]))



def ai_move(ai, timeout=10):
    queue = Queue()
    process = Process(target=ai_move_logic, args=(ai, queue))
    process.start()
    process.join(timeout)
    if process.is_alive():
        print("AI move timed out, returning default move.")
        process.terminate()
        return 7, 7
    return queue.get()
