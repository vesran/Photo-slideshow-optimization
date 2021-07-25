from base import *
from utils import *

from tqdm import trange, tqdm
import numpy as np
import random
import math
import copy


class UCBSolution:

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

    def get_candidate_idx_slides(self, sorted_idx_slides, max_candidates=100):
        # Returning the longest
        return sorted_idx_slides[:max_candidates]

    def playout(self,current_idx_slide, idx_slides, all_slides):
        sample = random.sample(idx_slides, k=min(len(idx_slides), 10))
        res = 0
        prev_idx = current_idx_slide
        for idx in sample:
            res += score_slides(all_slides[prev_idx], all_slides[idx])
            prev_idx = idx
        return res

    def UCB(self, current_idx_slide, possible_idx_slides, idx_slides, all_slides, n_sims):
        scores = [[idx, 0, 0, idx, i] for i, idx in enumerate(possible_idx_slides)]  # idx, score, num chosen
        for s in range(1, n_sims+1):
            best_val = 0
            best_idx_slide = None
            best_i = None  # Index for scores
            for i, idx_slide in enumerate(possible_idx_slides):
                val = 100000.0
                if scores[i][2] > 0:
                    # Slide visited
                    val = scores[i][1] / scores[i][2] + 0.7 * math.sqrt(math.log(s) / scores[i][2])
                if val >= best_val:
                    best_val = val
                    best_idx_slide = idx_slide
                    best_i = i
            res = score_slides(all_slides[current_idx_slide], all_slides[best_idx_slide])
            copy_idx_slides = idx_slides[:]
            copy_idx_slides.remove(best_idx_slide)
            res += self.playout(best_idx_slide, copy_idx_slides, all_slides)
            scores[best_i][2] += 1
            scores[best_i][1] += res

        # Take max
        return max(scores,  key=lambda x: x[2])[0]

    @timeit
    def create_slideshow(self, src_slides, max_candidates=100):
        idx_slides = sorted(range(0, len(src_slides)), key=lambda x: -len(src_slides[x].get_tags()))

        seed_idx = 0
        next_idx_slide = seed_idx  # So that the loop is coherent : we need to know idx
        seed = src_slides[seed_idx]
        idx_slides.remove(seed_idx)
        sh = Slideshow()
        sh.add_right(seed)

        num_random = 0
        t = trange(len(src_slides)-1, desc='Create slideshow', leave=True)
        for _ in t:
            sample_idx_slides = self.get_candidate_idx_slides(list(idx_slides), max_candidates=max_candidates)
            if len(sample_idx_slides) > 0:
                next_idx_slide = self.UCB(next_idx_slide, sample_idx_slides, idx_slides, src_slides, n_sims=max_candidates*3)
            else:
                # Choose randomly
                num_random += 1
                next_idx_slide = random.choice(list(idx_slides))
            next_slide = src_slides[next_idx_slide]
            idx_slides.remove(next_idx_slide)
            sh.add_right(next_slide)

        print(f'Num random : {num_random}/{len(src_slides)}')
        assert len(idx_slides) == 0
        return sh

    def run(self, filename, max_candidates=100):
        photos = load_data(filename)
        slides = self.form_slides(photos)
        del photos
        print(f'Num slides : {len(slides)}')
        slideshow = self.create_slideshow(slides, max_candidates=max_candidates)
        score = score_slideshow(slideshow)
        print(f'Score : {score}')
        return slideshow


if __name__ == '__main__':
    filename = "data/c_memorable_moments.txt"
    sol = UCBSolution()
    sol.run(filename, max_candidates=100)
