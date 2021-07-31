from base import *
from utils import *

import math
import random
import copy


class UCT:

    def __init__(self, filename, max_slides=200, max_candidates=3):
        photos = load_data(filename)
        self.slides = self.form_slides(photos)
        print(f'Num slides : {len(self.slides)}')
        self.slides_ids = sorted(range(len(self.slides[:max_slides])), key=lambda x: -len(self.slides[x].get_tags()))
        self.max_candidates = max_candidates

    @timeit
    def form_slides(self, photos):
        # Naive algorithm where
        # vertical photos are paired sequentially as they are read.
        slides = []
        remaining_vertical = None
        for photo in photos:
            if photo.is_vertical() and remaining_vertical is not None:
                slide = Slide(remaining_vertical, photo)
                slides.append(slide)
                remaining_vertical = None
            elif photo.is_vertical() and remaining_vertical is None:
                remaining_vertical = photo
            else:
                # Photo is horizontal
                slide = Slide(photo)
                slides.append(slide)
        assert remaining_vertical is None, f"One vertical photo remains... Kinda strange."
        return slides

    def legal_moves(self, state):
        return state[1][:self.max_candidates]

    def terminal(self, slideshow):
        return len(slideshow) == len(self.slides_ids)

    def play(self, state, move):
        assert move in state[1]
        state = copy.deepcopy(state)
        if len(state[0]) > 0:
            s = score_slides(self.slides[state[0][-1]], self.slides[move]) + state[2]
        else:
            s = 0
        state[0].append(move)
        state[1].remove(move)
        h = state[-1] ^ move
        return state[0], state[1], s, h

    def playout(self, state):
        while len(state[1]) > 0:
            moves = self.legal_moves(state)
            move = random.choice(moves)
            state = self.play(state, move)
        return state[2]

    def uct(self, state, table, c):
        if self.terminal(state[0]):
            return state[2]
        t = table.get(state[-1], None)  # [num playout, [num chosen for each move], [sum score for each move]]
        if t is not None:
            best_value = -1
            best = 0
            moves = self.legal_moves(state)
            for i, m in enumerate(moves):
                val = 100_000
                if t[1][i] > 0:
                    Q = t[2][i] / t[1][i]  # Mean score
                    val = Q + c * math.sqrt(math.log(t[0]) / t[1][i])
                if val > best_value:
                    best_value = val
                    best = i
            state = self.play(state, moves[best])
            res = self.uct(state, table, c)
            t[0] += 1
            t[1][best] += 1
            t[2][best] += res
            return res
        else:
            num_playouts = [0. for _ in range(self.max_candidates)]
            scores = [0. for _ in range(self.max_candidates)]
            table[state[-1]] = [0, num_playouts, scores]
            return self.playout(state)

    def best_move(self, state, n, c):
        table = {}
        for _ in range(n):
            s1 = copy.deepcopy(state)
            _ = self.uct(state, table, c)
        moves = self.legal_moves(state)
        best_move_idx = max(range(self.max_candidates), key=lambda x: table.get(state[-1], 0)[1][x])
        best_move = moves[best_move_idx]
        mean_score = table.get(state[-1], 0)[2][best_move_idx] / table.get(state[-1], 0)[1][best_move_idx]
        return best_move, mean_score

    def create_slideshow(self, n, c):
        state = ([], self.slides_ids[:], 0, hash('begin'))
        ss = Slideshow()
        while not self.terminal(state[0]):
            best_move, ms = self.best_move(state, n, c)
            state = self.play(state, best_move)
        [ss.add_right(self.slides[s]) for s in state[0]]
        return ss

    def run(self, n, c, verbose=1):
        slideshow = self.create_slideshow(n, c)
        score = score_slideshow(slideshow)
        print(f'Score : {score}') if verbose > 0 else 0
        return slideshow


if __name__ == '__main__':
    filename = "data/c_memorable_moments.txt"
    sol = UCT(filename, max_slides=50, max_candidates=3)
    slideshow = sol.run(30, 0.01)
