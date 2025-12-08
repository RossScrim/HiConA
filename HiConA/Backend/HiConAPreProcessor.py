import numpy as np
import tifffile
import imagej
import scyjava
import tempfile
import re
import os
from tkinter.filedialog import askdirectory
import json

from HiConA.Utilities.ConfigReader import ConfigReader
from HiConA.Utilities.IOread import load_images, save_images, create_directory

class PreProcessor:
    def __init__(self, images, config, xml_reader):
        self.image_array = np.array(images)

        self.saved_variables = self._load_variables()


    def process(self, projection, to_8bit):
        if projection == "Maximum":
            self._max_projection()
        elif projection == "Minimum":
            self._min_projection()
        elif projection == "ImageJ EDF":
            self._imagej_EDF()

        if to_8bit:
            self._convert_to_8bit()


    def _max_projection(self):
        self.image_array = np.max(self.image_array, axis=0)
        return self
    
    def _min_projection(self):
        self.image_array = np.min(self.image_array, axis=0)
        return self
    

    def _imagej_EDF(self):
        imagej_loc = self.saved_variables["imagej_loc_entry"]

        plugins_dir = os.path.join(imagej_loc, "plugins")
        scyjava.config.add_option(f'-Dplugins.dir={plugins_dir}')
        ij = imagej.init(imagej_loc, mode="interactive")
        ij.ui().showUI()

        # Generate tempfile
        temp_dir = tempfile.TemporaryDirectory()
        bf_temp = os.path.join(temp_dir.name, "ref_ch.tiff")
        proc_temp = os.path.join(temp_dir.name, "proc.tif")

        # EDF macro
        macro, arg = self._get_edf_macro()

        #TODO Continue from here finishing the EDF part
        processed_image = np.empty((self.num_channels, self.image_x_dim, self.image_y_dim))
        bf_channel = BF_ch #Change which channel is the bf_channel, 0-indexed.
        for ch in range(self.num_channels):
            cur_image = self.image_array[:,ch,:,:] # only get one channel
            if ch == bf_channel:
                tifffile.imwrite(bf_temp, cur_image, imagej=True, metadata={'axes':'ZYX'}) #Change where the bf.tiff is saved.

                ij.py.run_macro(macro, arg)

                bf_array = []
                bf_array.append(tifffile.imread(proc_temp)) #Change where the processed_bf.tif is saved.
                bf_array = np.array(bf_array)

                processed_image[ch] = bf_array
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
        @ String BFImagePath
        @ String procImagePath

        open(BFImagePath); 
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
            "BFImagePath": bf_temp,
            "procImagePath": proc_temp
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
    



if __name__ == "__main__":
    pass


