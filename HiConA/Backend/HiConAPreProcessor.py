import numpy as np
import tifffile
import imagej
import scyjava
import tempfile
import os
import json

from HiConA.Utilities.Image_Utils import get_xy_axis_from_image
from HiConA.Utilities.ConfigReader import ConfigReader
from HiConA.Utilities.IOread import load_images, save_images, create_directory

class HiConAPreProcessor:
    def __init__(self, images, config):
        self.image_array = np.array(images)
        self.saved_variables = self._load_variables()
        # extract experimental information from config file
        self.image_y_dim, self.image_x_dim = get_xy_axis_from_image(images)
        self.num_planes = config["PLANES"]

        if type(config["CHANNEL"]) is list:
            self.num_channels = len(config["CHANNEL"])
        else:
            self.num_channels = 1

    def process(self, projection, to_8bit, EDF_channel):
        if projection == "Maximum":
            self._max_projection()
        elif projection == "Minimum":
            self._min_projection()
        elif projection == "ImageJ EDF":
            self._imagej_EDF(EDF_channel)
        if to_8bit:
            self._convert_to_8bit()

    def _max_projection(self):
        self.image_array = np.max(self.image_array, axis=0)
        return self
    
    def _min_projection(self):
        self.image_array = np.min(self.image_array, axis=0)
        return self

    def _convert_to_8bit(self):
        image_8bit = []
        for image in self.image_array:
            image_8bit.append(np.uint8((image / np.max(image)) * 255))

          # Stack the list back into a single numpy array
        self.image_array = np.array(image_8bit)
        return self

    def _imagej_EDF(self, EDF_channel_num):
        imagej_loc = self.saved_variables["imagej_loc_entry"]
        plugins_dir = os.path.join(imagej_loc, "plugins")
        scyjava.config.add_option(f'-Dplugins.dir={plugins_dir}')
        ij = imagej.init(imagej_loc, mode="interactive")
        ij.ui().showUI()

        # Generate tempfile
        temp_dir = tempfile.TemporaryDirectory()
        self.edf_temp = os.path.join(temp_dir.name, "ref_ch.tiff")
        self.proc_temp = os.path.join(temp_dir.name, "proc.tif")

        # EDF macro
        macro, arg = self._get_edf_macro()

        #TODO Continue from here finishing the EDF part
        processed_image = np.empty((self.num_channels, self.image_x_dim, self.image_y_dim))
        edf_channel = EDF_channel_num #Change which channel is the bf_channel, 0-indexed.
        for ch in range(self.num_channels):
            cur_image = self.image_array[:,ch,:,:] # only get one channel
            if ch == edf_channel:
                tifffile.imwrite(self.edf_temp, cur_image, imagej=True, metadata={'axes':'ZYX'}) #Change where the bf.tiff is saved.

                ij.py.run_macro(macro, arg)

                edf_array = []
                edf_array.append(tifffile.imread(self.proc_temp)) #Change where the processed_bf.tif is saved.
                edf_array = np.array(edf_array)

                processed_image[ch] = edf_array
            else:
                #tifffile.imwrite("fluo.tiff", cur_image, imagej=True, metadata={'axes':'ZYX'}) #Change where the bf.tiff is saved.
                processed_image[ch] = np.max(cur_image, axis=0)
        
        necessary_type = np.uint16
        min_value = np.iinfo(necessary_type).min # 0
        max_value = np.iinfo(necessary_type).max # 65535
        array_clipped = np.clip(processed_image, min_value, max_value)
        self.image_array = array_clipped.astype(necessary_type)

        ij.dispose()
        temp_dir.cleanup()
        return self

    def _get_edf_macro(self):
    # EDF macro
        macro = """
        @ String edfImagePath
        @ String procImagePath

        open(edfImagePath); 
        //print("image opened");
        run("EDF Easy mode", "quality='2' topology='0' show-topology='off' show-view='off'");
        //print("EDF run");
        while(!isOpen("Output")){
        //print("in while-loop");
		wait(5000);}
		selectImage("Output");
        //run("Duplicate...", "Output-1");
        //selectImage("Output-1");
        //run("Gaussian Blur...", "sigma=100");
        //imageCalculator("Divide create 32-bit", "Output","Output-1");
        //selectImage("Result of Output");
        run("16-bit");
        run("Enhance Contrast", "saturated=0.35");
        saveAs("Tiff", procImagePath);
        //print("saved");
        close("*");
        """

        arg = {
            "edfImagePath": self.edf_temp,
            "procImagePath": self.proc_temp
        }
        return macro, arg

    def _load_variables(self):
        saved_variables_f = os.path.join(os.path.dirname(__file__), '..', 'GUI', "saved_variables.json")
        if os.path.isfile(saved_variables_f):
            with open(saved_variables_f, "r+") as f:
                saved_var = json.load(f)
                return saved_var
        else:
            return None

    def get_image(self):
        return self.image_array

if __name__ == "__main__":
    pass


