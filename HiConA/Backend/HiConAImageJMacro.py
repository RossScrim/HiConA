import numpy as np
import tifffile
import imagej
import scyjava
import tempfile
import re
import os
from tkinter.filedialog import askdirectory
import json

class ImageJProcessor:
    def __init__(self, images):
        self.image_array = np.array(images)
        # Get this some other way?
        dimensions = np.shape(self.image_array)

        self.num_channels = dimensions[0]
        self.image_x_dim = dimensions[1]
        self.image_y_dim = dimensions[2]

        self.config_var = self._load_imagej_config()

        self.macro, self.arg, self.temp_dir = self._generate_macro(macro_file = self.config_var["macro_file"], args_file = self.config_var["args_file"])
        

    def _load_imagej_config(self):
        imagej_config_f = os.path.join(os.path.dirname(__file__), '..', 'GUI', "imagej_macro_config.json")
        if os.path.isfile(imagej_config_f):
            with open(imagej_config_f, "r+") as f:
                imagej_config = json.load(f)
                return imagej_config
        else:
            return None

    def _imagej_run_macro(self):
        self._init_imagej()
        pre_macro_temp = os.path.join(self.temp_dir.name, "pre.tiff")
        post_macro_temp = os.path.join(self.temp_dir.name, "post.tif")

        processed_image = np.empty((self.num_channels, self.image_x_dim, self.image_y_dim))
        
        for ch in range(self.num_channels):
            cur_image = self.image_array[ch, :, :]
            tifffile.imwrite(pre_macro_temp, cur_image, imagej=True, metadata={'axes':'YX'})

            self.ij.py.run_macro(self.macro, self.arg)

            temp_im_array = []
            temp_im_array.append(tifffile.imread(post_macro_temp))
            temp_im_array = np.array(temp_im_array)

            processed_image[ch] = temp_im_array
            
        necessary_type = np.uint16
        min_value = np.iinfo(necessary_type).min # 0
        max_value = np.iinfo(necessary_type).max # 65535
        array_clipped = np.clip(processed_image, min_value, max_value)
        self.image_array = array_clipped.astype(necessary_type)

        self.ij.dispose()
        self.temp_dir.cleanup()
        return self
    
    def _init_imagej(self):
        imagej_loc = self.config_var["imagej_loc"]

        plugins_dir = os.path.join(imagej_loc, "plugins")
        scyjava.config.add_option(f'-Dplugins.dir={plugins_dir}')
        if self.config_var["interactive"] == 1:
            self.ij = imagej.init(imagej_loc, mode="interactive")
        else:
            self.ij = imagej.init(imagej_loc)
        
        if self.config_var["show_UI"] == 1:
                self.ij.ui().showUI()

    
    def _generate_macro(self, macro_file, args_file, cleanup_temp = 0):
        with open(macro_file, "r") as f:
            macro = f.read()

        with open(args_file, "r") as f:
            arg = json.load(f)

        # Generate tempfile
        temp_dir = tempfile.TemporaryDirectory()
        pre_macro_temp = os.path.join(temp_dir.name, "pre.tiff")
        post_macro_temp = os.path.join(temp_dir.name, "post.tif")

        arg["preImagePath"] = pre_macro_temp
        arg["postImagePath"] = post_macro_temp

        arg_text = ""
        for key in arg.keys():
            arg_type = type(arg[key])

            if arg_type == str:
                arg_text += "#@ String " + str(key) +"\n" 
            elif arg_type == int:
                arg_text += "#@ int " + str(key) +"\n"
            elif arg_type == float:
                arg_text += "#@ float " + str(key) +"\n"
        
        macro = arg_text + """open(preImagePath);\n""" + macro + """\nsaveAs("Tiff", postImagePath);"""

        if cleanup_temp:
            temp_dir.cleanup()

        return macro, arg, temp_dir

    def process(self):
        """Processes the image based on flags for specific operations."""
        self._imagej_run_macro()
        return self  # Return self to allow method chaining
    
    def get_image(self):
        return self.image_array
    

if __name__ == "__main__":
    image_path = r"Z:\Emma\MMC poster\Processed\18112025_LS411N_ATX968_S9.6 - 1\r04c05\Stitched\r04c05.tif"
    im_arr = np.array([tifffile.imread(image_path)])

    imagejprocessor = ImageJProcessor(im_arr[0])

    imagejprocessor.process()

    processed_image = imagejprocessor.get_image()

    tifffile.imwrite(os.path.join(r"C:\Users\ewestlund\Documents\GitHub Projects\HiConA\HiConA\Test Data", "test_image.tif"), 
                     processed_image,
                     imagej=True, 
                     metadata={'axes': 'CYX'})