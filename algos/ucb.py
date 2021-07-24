from base import *
from utils import *

from tqdm import trange, tqdm
import numpy as np
import random
import math
import copy


@timeit
def form_slides(photos):
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


def get_candidate_idx_slides(sorted_idx_slides):
    # Returning the longest
    return sorted_idx_slides[:200]


def playout(current_idx_slide, idx_slides, all_slides):
    sample = random.sample(idx_slides, k=min(len(idx_slides), 10))
    res = 0
    prev_idx = current_idx_slide
    for idx in sample:
        res += score_slides(all_slides[prev_idx], all_slides[idx])
        prev_idx = idx
    return res


def UCB(current_idx_slide, possible_idx_slides, idx_slides, all_slides, n_sims):
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
        res += playout(best_idx_slide, copy_idx_slides, all_slides)
        scores[best_i][2] += 1
        scores[best_i][1] += res

    # Take max
    return max(scores,  key=lambda x: x[2])[0]


@timeit
def create_slideshow(src_slides):
    idx_slides = sorted(range(0, len(src_slides)), key=lambda x: -len(src_slides[x].get_tags()))

    seed_idx = 0
    next_idx_slide = seed_idx  # So that the loop is coherent : we need to know idx
    seed = src_slides[seed_idx]
    idx_slides.remove(seed_idx)
    sh = Slideshow()
    sh.add_right(seed)

    print('Start looping')
    num_random = 0
    t = trange(len(src_slides)-1, desc='Bar desc', leave=True)
    for _ in t:
        sample_idx_slides = get_candidate_idx_slides(list(idx_slides))
        if len(sample_idx_slides) > 0:
            next_idx_slide = UCB(next_idx_slide, sample_idx_slides, idx_slides, src_slides, n_sims=200*2)
        else:
            # Choose randomly
            num_random += 1
            next_idx_slide = random.choice(list(idx_slides))
        next_slide = src_slides[next_idx_slide]
        idx_slides.remove(next_idx_slide)
        sh.add_right(next_slide)

        if len(sh) % 10000 == 0:
            print(len(sh), 'incorporated in slideshow')
    print(f'Num random : {num_random}/{len(src_slides)}')
    assert len(idx_slides) == 0
    return sh


if __name__ == '__main__':
    filename = "data/d_pet_pictures.txt"
    photos = load_data(filename)

    slides = form_slides(photos)
    del photos
    print(f'Num slides : {len(slides)}')
    slideshow = create_slideshow(slides)
    score = score_slideshow(slideshow)

    print(f'Score : {score}')
