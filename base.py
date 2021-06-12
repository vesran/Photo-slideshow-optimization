

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


class Slideshow:
    """
    Represents an ordered sequence of photos. The order will give the final score.
    Can make the slideshow grow by adding one photo to the left or to the right at a time.
    Can also see the current photo at the left/right. 
    """

    def __init__(self):
        self.photos = []

    def add_left(self, photo):
        self.photos.insert(0, photo)

    def add_right(self, photo):
        self.photos.append(photo)

    def get_photos(self):
        return self.photos

    def get_first(self):
        return self.photos[0]

    def get_last(self):
        return self.photos[-1]

    def __repr__(self):
        return repr(self.photos)

    def __len__(self):
        return len(self.photos)


###########################################
# Metrics
###########################################

def compute_score(photo1, photo2):
    """ Calculates score of transition between photo1 to photo2.
    :param photo1: First photo (left).
    :param photo2: Second photo (right).
    :return:
    """
    common_tags = photo1.get_tags().intersection(photo2.get_tags())
    return min(len(common_tags),
               len(photo1.get_tags()-common_tags),
               len(photo2.get_tags()-common_tags))


def compute_score_slideshow(slideshow):
    """ Calculates the total score given the slideshow.
    :param slide: Slideshow
    :return: Int score.
    """
    assert len(slideshow) > 0
    s = 0
    photos = slideshow.get_photos()
    if len(photos) > 1:
        assert photos[0].is_vertical() == photos[1].is_vertical(), f"V/H rule broken at position [0, 1] in slide"
        assert photos[-1].is_vertical() == photos[-2].is_vertical(), f"V/H rule broken at the 2 last positions in slide"
    for i in range(1, len(slideshow)):
        s += compute_score(photos[i-1], photos[i])

        # Check if a vertical image is next to another vertical image
        if (i-2 >= 0) and (not photos[i-2].is_vertical()) and \
                (photos[i-1].is_vertical()) and (not photos[i].is_vertical()):
            raise Exception(f"V/H rule broken at position {[i-2, i-1, i]} in slide")
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
