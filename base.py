

class Photo:
    """
    Represents a photo. Photo has
    - an orientation which can be 'V' or 'H',
    - a set of tags.
    """

    def __init__(self, orientation, tags):
        assert orientation in ('V', 'H')
        self.orientation = orientation  # V or H
        self.tags = tags  # Set

    def __repr__(self):
        return self.orientation + repr(self.tags)

    def get_tags(self):
        return self.tags

    def is_vertical(self):
        return self.orientation == 'V'


class Slide:
    """
    Represents a slide containing :
    - one horizontal photo
    or
    - two vertical photos.
    """

    def __init__(self, photo1, photo2=None):
        if photo2:
            # Check if we have 2 vertical photos
            assert photo1.is_vertical() and photo2.is_vertical(), "At least one photo is not vertical."
        else:
            # Check if we are trying to insert 1 single vertical photo.
            assert not photo1.is_vertical(), "Not allowed to create a slide with a single vertical photo."
        self.content = [photo1] if photo2 is None else [photo1, photo2]
        self.tags = photo1.get_tags().union(photo2.get_tags()) if photo2 else photo1.get_tags()

    def has_vertical(self):
        # Does the slide contains 2 vertical photos or not.
        return len(self.content) == 2

    def get_tags(self):
        return self.tags

    def get_content(self):
        return self.content

    def __repr__(self):
        return repr(self.content)


class Slideshow:
    """
    Represents an ordered sequence of slides.
    Can make the slideshow grow by adding one slide to the left or to the right at a time.
    Can also see the current slide at the left/right.
    """

    def __init__(self):
        self.slides = []

    def add_left(self, slide):
        self.slides.insert(0, slide)

    def add_right(self, slide):
        self.slides.append(slide)

    def get_slides(self):
        return self.slides

    def get_first(self):
        return self.slides[0]

    def get_last(self):
        return self.slides[-1]

    def __repr__(self):
        return repr(self.slides)

    def __len__(self):
        return len(self.slides)


###########################################
# Metrics
###########################################

def score_slides(slide1, slide2):
    """ Calculates transition score between slide1 to slide2.
    :param slide1: First slide (left).
    :param slide2: Second slide (right).
    :return: Int score
    """
    common_tags = slide1.get_tags().intersection(slide2.get_tags())
    return min(len(common_tags),
               len(slide1.get_tags()-common_tags),
               len(slide2.get_tags()-common_tags))


def score_slideshow(slideshow):
    """ Calculates the total score of the given slideshow.
    :param slideshow: Slideshow
    :return: Int score.
    """
    assert len(slideshow) > 0
    slides = slideshow.get_slides()
    # Handle first slide which can be composed of 2 vertical photos - score photos
    s = 0
    for i in range(1, len(slideshow)):
        # Between 2 slides
        s += score_slides(slides[i-1], slides[i])

    return s


###########################################
# Load data
###########################################

def load_data(filename, verbose=1):
    """ Reads data.
    :param filename: File containing data about photos.
    :param verbose: Verbose purposes. Set it to 0 in order to silent everything.
    :return: list of Photo described in the specified file.
    """
    # Get lines
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Parse data line to Photo
    photos = []
    true_num_photos = int(lines[0])
    for i, line in enumerate(lines[1:], start=1):
        # Extract info from line
        array = line.strip().split(' ')
        orientation = array[0]
        num_tags = int(array[1])
        tags = array[2:]
        assert len(tags) == num_tags, f'The number of tags is not what is expected at line {i}.'
        # Add photo
        photos.append(Photo(orientation, tags))

    assert true_num_photos == len(photos), 'The number of photos is not what is expected.'
    print(len(photos), 'photos caught.') if verbose >= 1 else 0
    return photos


if __name__ == '__main__':
    filename = "data/e_shiny_selfies.txt"
    photos = load_data(filename)
