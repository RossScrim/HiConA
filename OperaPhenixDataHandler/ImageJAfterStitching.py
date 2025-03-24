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
        dimensions = np.shape(self.image_array)

        self.num_channels = dimensions[0]
        self.image_x_dim = dimensions[1]
        self.image_y_dim = dimensions[2]

    def imagej_run_macro(self):
        self.init_imagej()

        processed_image = np.empty((self.num_channels, self.image_x_dim, self.image_y_dim))
        
        for ch in range(self.num_channels):
            cur_image = self.image_array[ch, :, :]
            tifffile.imwrite(self.pre_macro_temp, cur_image, imagej=True, metadata={'axes':'YX'})

            self.ij.py.run_macro(self.macro, self.arg)

            temp_im_array = []
            temp_im_array.append(tifffile.imread(self.post_macro_temp))
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
        

    def init_imagej(self):
        self.cur_py_dir = os.path.dirname(__file__)
        self.imagej_config = os.path.join(self.cur_py_dir, "imagej_config.json")
        with open(self.imagej_config, "r") as f:
            self.config_var = json.load(f)
        
        imagej_loc = self.config_var["fiji_loc"]

        plugins_dir = os.path.join(imagej_loc, "plugins")
        scyjava.config.add_option(f'-Dplugins.dir={plugins_dir}')
        if self.config_var["interactive"] == 1:
            self.ij = imagej.init(imagej_loc, mode="interactive")
            self.ij.ui().showUI()
        else:
            self.ij = imagej.init(imagej_loc)
        
        # Generate tempfile
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pre_macro_temp = os.path.join(self.temp_dir.name, "pre.tiff")
        self.post_macro_temp = os.path.join(self.temp_dir.name, "post.tif")

        macro_file = self.config_var["macro_file"]
        args_file = self.config_var["args_file"]

        with open(macro_file, "r") as f:
            self.macro = f.read()

        with open(args_file, "r") as f:
            self.arg = json.load(f)

        self.arg["preImagePath"] = self.pre_macro_temp
        self.arg["postImagePath"] = self.post_macro_temp

        arg_text = ""
        for key in self.arg.keys():
            arg_type = type(self.arg[key])

            if arg_type == str:
                arg_text += "#@ String " + str(key) +"\n" 
            elif arg_type == int:
                arg_text += "#@ int " + str(key) +"\n"
            elif arg_type == float:
                arg_text += "#@ float " + str(key) +"\n"
        
        self.macro = arg_text + """open(preImagePath);\n""" + self.macro + """\nsaveAs("Tiff", postImagePath);"""


    def process(self):
        """Processes the image based on flags for specific operations."""
        self.imagej_run_macro()
        return self  # Return self to allow method chaining
    
    def get_image(self):
        return self.image_array