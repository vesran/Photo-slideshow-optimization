from base import *
from utils import *

import random


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


def create_random_slideshow(slides):
    random.shuffle(slides)
    slideshow = Slideshow()
    for slide in slides:
        slideshow.add_right(slide)
    return slideshow


@timeit
def create_slideshow(slides, num_iters=10):
    best_slideshow = None
    best_score = -1
    all_scores = []
    for _ in range(num_iters):
        slideshow = create_random_slideshow(slides)
        score = score_slideshow(slideshow)
        if score > best_score:
            best_score = score
            best_slideshow = slideshow
        all_scores.append(score)
    print("All scores :", all_scores)
    return best_slideshow


if __name__ == '__main__':
    filename = "data/d_pet_pictures.txt"
    photos = load_data(filename)

    slides = form_slides(photos)
    slideshow = create_slideshow(slides, num_iters=10)
    score = score_slideshow(slideshow)

    print(f'Score : {score}')
