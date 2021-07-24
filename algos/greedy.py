from base import *
from utils import *

from sklearn.feature_extraction.text import CountVectorizer

from tqdm import trange
from tqdm import tqdm
import numpy as np
import random
import copy


@timeit
def form_slides(photos):
    # Naive algorithm where
    # vertical photos are paired sequentially as they are read.
    slides = []
    remaining_vertical = None
    slide = None
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


def _get_next_best_idx_slide(current_slide, sample_idx_slides, all_slides):
    return max(sample_idx_slides, key=lambda x: score_slides(current_slide, all_slides[x]))


def get_tag_to_idx_slides(slides):
    tag2idx_slides = {}
    for idx_slide, slide in enumerate(slides):
        for tag in slide.get_tags():
            if tag not in tag2idx_slides:
                tag2idx_slides[tag] = set()
            tag2idx_slides[tag].add(idx_slide)
    return tag2idx_slides


def get_candidate_idx_slides_old2(idx_slides, current_slide, tag2idx_slides):
    # Returns slides indices which share at least one common tag with the current slide
    candidates = set()
    for tag in current_slide.get_tags():
        candidates = candidates.union(tag2idx_slides[tag])
        if len(candidates) > 1_000:
            # Break early, otherwise it's too long
            break
    inter = candidates.intersection(idx_slides)
    return inter if len(inter) > 0 else idx_slides


def get_candidate_idx_slides_old(table, tag2idx, current_slide, idx_slides):
    tags_idx = [tag2idx[tag] for tag in current_slide.get_tags()]
    sums = table[idx_slides][:, tags_idx].sum(axis=1).flatten()
    max_common = sums.max()
    n_min = 1  #0. * max_common
    #n_max = 1.5 * max_common
    # candidates = np.where((n_min <= sums) & (sums <= n_max))[1]
    candidates = np.where(n_min <= sums)[1]
    return idx_slides[candidates][:1000]


def get_candidate_idx_slides(sorted_idx_slides):
    # Returning the longest
    return sorted_idx_slides[:1000]



@timeit
def create_slideshow(src_slides):
    # idx_slides = set(range(0, len(src_slides)))
    idx_slides = sorted(range(0, len(src_slides)), key=lambda x: -len(src_slides[x].get_tags()))
    # tmp = np.array(list(idx_slides))

    seed_idx = 0
    seed = src_slides[seed_idx]
    idx_slides.remove(seed_idx)

    print("Get table")
    # tag2idx_slides = get_tag_to_idx_slides(src_slides)

    # vectorizer = CountVectorizer()
    # corpus = [' '.join(list(slide.get_tags())) for slide in slides]
    # table = vectorizer.fit_transform(corpus)
    # tag2idx = {tag: i for i, tag in enumerate(vectorizer.get_feature_names())}

    sh = Slideshow()
    sh.add_right(seed)

    print('Start looping')
    num_random = 0
    t = trange(len(src_slides)-1, desc='Bar desc', leave=True)
    for _ in t:
        # sample_idx_slides = random.sample(idx_slides, min(1000, len(idx_slides)))  # legalMoves
        # sample_idx_slides = get_candidate_idx_slides_old2(idx_slides, sh.get_last(), tag2idx_slides)
        # sample_idx_slides = get_candidate_idx_slides_old(table, tag2idx, sh.get_last(), tmp[list(idx_slides)])
        sample_idx_slides = get_candidate_idx_slides(list(idx_slides))
        if len(sample_idx_slides) > 0:
            next_idx_slide = _get_next_best_idx_slide(sh.get_last(), sample_idx_slides, src_slides)
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
