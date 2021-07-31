from base import *
from utils import *

from tqdm import trange
from tqdm import tqdm
import numpy as np
import random
from math import exp
import copy


class NRPASolutionTimed:

    def __init__(self, filename, max_slides=200, max_candidates=3, N=50, P=10):
        photos = load_data(filename)
        self.slides = self.form_slides(photos)
        print(f'Num slides : {len(self.slides)}')
        self.slides_ids = sorted(range(len(self.slides[:max_slides])), key=lambda x: -len(self.slides[x].get_tags()))
        self.max_candidates = max_candidates
        self.N = N 
        self.P = P

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
        return state[1][:]

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

    # def playout(self, state, policy="Uniform"):
    #     while len(state[1]) > 0:
    #         moves = self.legal_moves(state)
    #         move = random.choice(moves)
    #         state = self.play(state, move)
    #     return state

    def code(self, move):
        return move # move is already coded as an index on the slides so the function is idempotent

    def playout_nrpa(self, state, policy):
        sequence = []
        while len(state[1]) > 0:
            z=0.0
            moves = self.legal_moves(state)
            for m in moves:
                z=z+exp(policy[self.code(m)])
            move = random.choices(moves, weights=[exp(policy[self.code(m)])/z for m in moves])[0]
            state = self.play(state, move)
            sequence.append(move)
        ss = Slideshow()
        [ss.add_right(self.slides[s]) for s in state[0]]
        return score_slideshow(ss), sequence

    def nrpa(self, n, policy, monitor_time=False, delay=1000):
        if monitor_time:
            ts = time.time()
        if n == 0:
            root = ([], self.slides_ids[:], 0) 
            return self.playout_nrpa(root, policy)
        else:
            bestScore = float('-inf')
            bestSeq = []
            for _ in range(self.N): # Iterations
                score, seq = self.nrpa(n-1, policy)
                if score > bestScore:
                    bestScore = score
                    bestSeq = seq
                policy = self.adapt(policy, bestSeq)
                if monitor_time:
                    te = time.time()
                    if te-ts>delay:
                        print(te-ts)
                        return (bestScore, bestSeq)
            return (bestScore, bestSeq)

    def stabilizedNrpa(self, n, policy, monitor_time=False, delay=1000):
        if monitor_time:
            ts = time.time()
        if n == 0:
            root = ([], self.slides_ids[:], 0) 
            return self.playout_nrpa(root, policy)
        elif n==1:
            bestScore = float('-inf')
            bestSeq = []
            for _ in range(self.P):
                score, seq = self.stabilizedNrpa(n-1, policy)
                if score > bestScore:
                    bestScore = score
                    bestSeq = seq
                if monitor_time:
                    te = time.time()
                    if te-ts>delay:
                        return (bestScore, bestSeq)
            return (bestScore, bestSeq)
        else:
            bestScore = float('-inf')
            bestSeq = []
            for _ in range(self.N): # Iterations
                score, seq = self.stabilizedNrpa(n-1, policy)
                if score > bestScore:
                    bestScore = score
                    bestSeq = seq
                policy = self.adapt(policy, bestSeq)
                if monitor_time:
                    te = time.time()
                    if te-ts>delay:
                        return (bestScore, bestSeq)
            return (bestScore, bestSeq)

    def adapt(self, policy, sequence, alpha=1.0):
        root = ([], self.slides_ids[:], 0) 
        newPolicy = policy
        state = root
        for move in sequence:
            newPolicy[self.code(move)]+=alpha
            z=0.0
            for m in self.legal_moves(state):
                z+=exp(policy[self.code(m)])
            for m in self.legal_moves(state):
                newPolicy[self.code(m)]=newPolicy[self.code(m)]-alpha*(exp(policy[self.code(m)])/z)
            state = self.play(state, move)
        return newPolicy

    def create_slideshow(self, n, stabilized=False, monitor_time=False, delay=1000):
        policy = [random.randint(0,100)/100 for _ in range(len(self.slides_ids))]
        if stabilized:
            if monitor_time:
                bestScore, bestSeq = self.stabilizedNrpa(n, policy, monitor_time=True, delay=delay)
            else:
                bestScore, bestSeq = self.stabilizedNrpa(n, policy)
        else:
            if monitor_time:
                bestScore, bestSeq = self.nrpa(n, policy, monitor_time=True, delay=delay)
            else:
                bestScore, bestSeq = self.nrpa(n, policy)
        ss = Slideshow()
        [ss.add_right(self.slides[s]) for s in bestSeq]
        return ss

    def run(self, n, verbose=1, stabilized=False, monitor_time=False, delay=1000):
        if stabilized:
            if monitor_time:
                slideshow = self.create_slideshow(n, stabilized=True, monitor_time=True, delay=delay)
            else:
                slideshow = self.create_slideshow(n, stabilized=True)
        else:
            if monitor_time:
                slideshow = self.create_slideshow(n, stabilized=True, monitor_time=True, delay=delay)
            else:
                slideshow = self.create_slideshow(n)
        score = score_slideshow(slideshow)
        print(f'Score : {score}') if verbose > 0 else 0
        return slideshow

if __name__ == '__main__':
    filename = "data/c_memorable_moments.txt"
    sol = NRPASolution(filename, max_slides=20, max_candidates=3)
    slideshow = sol.run(2)
