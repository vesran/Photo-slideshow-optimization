from base import *
from utils import *

from tqdm import trange
from tqdm import tqdm
import numpy as np
import random
import copy


class GreedySolution:

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

    def get_next_best_idx_slide(self, current_slide, sample_idx_slides, all_slides):
        return max(sample_idx_slides, key=lambda x: score_slides(current_slide, all_slides[x]))

    def get_tag_to_idx_slides(self, slides):
        tag2idx_slides = {}
        for idx_slide, slide in enumerate(slides):
            for tag in slide.get_tags():
                if tag not in tag2idx_slides:
                    tag2idx_slides[tag] = set()
                tag2idx_slides[tag].add(idx_slide)
        return tag2idx_slides

    def get_candidate_idx_slides(self, sorted_idx_slides, max_candidates=1000):
        # Returning the longest
        return sorted_idx_slides[:max_candidates]

    @timeit
    def create_slideshow(self, src_slides, max_candidates=1000):
        idx_slides = sorted(range(0, len(src_slides)), key=lambda x: -len(src_slides[x].get_tags()))

        seed_idx = 0
        seed = src_slides[seed_idx]
        idx_slides.remove(seed_idx)

        sh = Slideshow()
        sh.add_right(seed)

        num_random = 0
        t = trange(len(src_slides) - 1, desc='Bar desc', leave=True)
        for _ in t:
            sample_idx_slides = self.get_candidate_idx_slides(list(idx_slides), max_candidates=max_candidates)
            if len(sample_idx_slides) > 0:
                next_idx_slide = self.get_next_best_idx_slide(sh.get_last(), sample_idx_slides, src_slides)
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
    filename = "data/d_pet_pictures.txt"
    sol = GreedySolution()
    sol.run(filename, 100)
