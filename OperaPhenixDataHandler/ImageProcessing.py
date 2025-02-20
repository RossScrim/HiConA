import numpy as np
import tifffile
from ConfigReader import OperaExperimentConfigReader


# TODO Add this class if needed?
class ImageFOVHandler:
    def __init__(self):
        pass
    def recombine_FOV():
        pass

class ImageProcessor:
    def __init__(self, images):
        self.image_array = np.array(images)
        self.image_dim = np.ndim(self.image_array)

    def max_projection(self):
        self.image_array = np.max(self.image_array, axis=0)
        return self

    def min_projection(self):
        self.image_array = np.min(self.image_array, axis=0)
        return self
    
    def convert_to_8bit(self):
        if self.image_dim == 2:
            self.image_array = self._convert_image_to_8bit(self.image_array)

        elif self.image_dim == 3:
            self.image_array = np.array([self._convert_image_to_8bit(image) for image in self.image_array])

        elif self.image_dim == 4:
            self.image_array = np.array([[self._convert_image_to_8bit(image)
                                          for image in image_array] for image_array in self.image_array])
        return self

    def _convert_image_to_8bit(self, image):
        image_temp = (image - np.min(image)) / np.array(image)
        image_temp = image_temp * 255
        return image_temp.astype(np.uint8)

    def process(self, max_proj=False, min_proj=False, to_8bit=False):
        """Processes the image based on flags for specific operations."""
        if max_proj:
            self.max_projection()
        if min_proj:
            self.min_projection()
        if to_8bit:
            self.convert_to_8bit()
        return self  # Return self to allow method chaining

    def get_image(self):
        return self.image_array

if __name__ == "__main__":
    opera_config = OperaExperimentConfigReader("88651da0-9ab0-4728-816f.kw.txt")
    opera_config_file = opera_config.load_json_from_txt(remove_first_lines=1, remove_last_lines=2)

    test_images = tifffile.imread("C:\\Users\\rscrimgeour\\Videos\\Test_stack.tif")
    images = ImageProcessor(test_images, opera_config_file).process(max_proj=True, to_8bit=True).get_image()
                                
    
    