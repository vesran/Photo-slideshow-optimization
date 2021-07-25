from base import *
from utils import *

from tqdm import tqdm
import random


class RandomSolution:

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

    def create_random_slideshow(self, slides):
        random.shuffle(slides)
        slideshow = Slideshow()
        for slide in slides:
            slideshow.add_right(slide)
        return slideshow

    @timeit
    def create_slideshow(self, slides, num_iters=10):
        best_slideshow = None
        best_score = -1
        all_scores = []
        for _ in tqdm(range(num_iters)):
            slideshow = self.create_random_slideshow(slides)
            score = score_slideshow(slideshow)
            if score > best_score:
                best_score = score
                best_slideshow = slideshow
            all_scores.append(score)
        print("All scores :", all_scores)
        return best_slideshow

    def run(self, filename, num_iters):
        photos = load_data(filename)

        slides = self.form_slides(photos)
        slideshow = self.create_slideshow(slides, num_iters=num_iters)
        score = score_slideshow(slideshow)

        print(f'Score : {score}')
        return slideshow


if __name__ == '__main__':
    filename = "data/d_pet_pictures.txt"
    sol = RandomSolution()
    s = sol.run(filename, num_iters=10)
