from base import *
from utils import *

from tqdm import trange
from tqdm import tqdm
import numpy as np
import random
import copy


class NestedMCSolution:

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
        if len(state[0]) > 0:
            s = score_slides(self.slides[state[0][-1]], self.slides[move]) + state[2]
        else:
            s = 0
        state[0].append(move)
        state[1].remove(move)
        return state[0], state[1], s

    def playout(self, state):
        while len(state[1]) > 0:
            moves = self.legal_moves(state)
            move = random.choice(moves)
            state = self.play(state, move)
        return state

    def nested(self, state, n):
        if n == 0:
            return self.playout(state)
        best_ending_state = (None, None, -1)
        while not self.terminal(state[0]):
            moves = self.legal_moves(state)
            for m in moves:
                s1 = copy.deepcopy(state)
                s1 = self.play(s1, m)
                s1 = self.nested(s1, n - 1)
                if s1[-1] > best_ending_state[-1]:
                    best_ending_state = s1
            state = self.play(state, best_ending_state[0][len(state[0])])
        return state

    def create_slideshow(self, n):
        state = ([], self.slides_ids[:], 0)
        final_state = self.nested(state, n)
        ss = Slideshow()
        [ss.add_right(self.slides[s]) for s in final_state[0]]
        return ss

    def run(self, n, verbose=1):
        slideshow = self.create_slideshow(n)
        score = score_slideshow(slideshow)
        print(f'Score : {score}') if verbose > 0 else 0
        return slideshow


if __name__ == '__main__':
    filename = "data/c_memorable_moments.txt"
    sol = NestedMCSolution(filename, max_slides=20, max_candidates=3)
    slideshow = sol.run(2)
