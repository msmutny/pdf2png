from app.workers.document_converter import get_normalized_size, ImageSize


def test_get_normalized_size():
    """
    Test method that takes a valid image size (both coordinates greater than zero)
    and fits it into a normalized image size rectangle (1200x1600). Every time the size
    in at least one dimension should equal the normalized image size. Note that since the
    image size is passed to a 'get_normalized_size' as argument from an existing PIL.Image
    object, we can rely on it not being negative or zero, thus we can ignore ZeroDivisionError.
    """
    assert get_normalized_size(ImageSize(1200, 1600)) == ImageSize(1200, 1600)
    assert get_normalized_size(ImageSize(600, 1600)) == ImageSize(600, 1600)
    assert get_normalized_size(ImageSize(600, 800)) == ImageSize(1200, 1600)
    assert get_normalized_size(ImageSize(600, 200)) == ImageSize(1200, 400)
    assert get_normalized_size(ImageSize(1700, 2200)) == ImageSize(1200, 1552)
    assert get_normalized_size(ImageSize(2400, 4800)) == ImageSize(800, 1600)

# TODO - test PDF conversion as well
