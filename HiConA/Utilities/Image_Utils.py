import numpy as np

def get_xy_axis_from_image(image: np.array) -> int:
    """
    Extracts the 'YX' axis from a given image axes as a int.

    Parameters:
    image_axes (str): A string representing the axes of an image (e.g., 'TCZYX').

    Returns:
    int: The 'YX' as an int.
    """

    x_axis = image.shape[-1]
    y_axis = image.shape[-2]

    return y_axis, x_axis