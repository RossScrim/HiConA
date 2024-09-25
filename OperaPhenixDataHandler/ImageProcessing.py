import numpy as np


class ImageProcessor:
    def __init__(self, images, config):
        self.image_array = np.array(images)
        self.image_x_dim = len(self.image_array[-1])
        self.image_y_dim = len(self.image_array[0])

        self.num_planes = config["planes"]
        self.num_channels = config["channels"]
        self.num_fov = config["fields"]

    def max_projection(self):
        projected_images = np.max(self.image_array, axis=1)
        return projected_images

    def min_projection(self):
        projected_images = np.min(self.image_array, axis=1)
        return projected_images

    def image_stitcher(self):
        pass

    def convert_to_8bit(self):
        image_8bit = []
        for image in self.image_array:
            image_8bit.append(np.uint8((image / np.max(image)) * 255))
        return np.array(image_8bit)

