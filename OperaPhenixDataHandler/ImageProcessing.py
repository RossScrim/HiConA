import numpy as np
import tifffile
import imagej
import scyjava
import tempfile
import re
import os
from tkinter.filedialog import askdirectory

from ConfigReader import OperaExperimentConfigReader


# TODO Add this class if needed?
class ImageFOVHandler:
    def __init__(self):
        pass
    def recombine_FOV():
        pass

class ImageProcessor:
    def __init__(self, images, config):
        self.image_array = np.array(images)
        dimensions = np.shape(self.image_array)
        #print(dimensions)
        self.image_x_dim = dimensions[2]
        self.image_y_dim = dimensions[3]

        self.num_planes = config["PLANES"]

        if type(config["CHANNEL"]) is list:
            self.num_channels = len(config["CHANNEL"])
        else:
            self.num_channels = 1
        self.timepoints = config["TIMEPOINTS"]
        #print(self.num_planes, self.num_channels, self.timepoints)

    def max_projection(self):
        self.image_array = np.max(self.image_array, axis=0)
        return self

    def min_projection(self):
        self.image_array = np.min(self.image_array, axis=0)
        return self
    
    def EDF_projection(self, BF_ch):
        plugins_dir = "C:/Users/ewestlund/Fiji.app/plugins" #Add path to Fiji Plugins
        scyjava.config.add_option(f'-Dplugins.dir={plugins_dir}')
        ij = imagej.init("C:/Users/ewestlund/Fiji.app", mode="interactive") #Add path to Fiji.app folder
        ij.ui().showUI()

        # Generate tempfile
        temp_dir = tempfile.TemporaryDirectory()
        bf_temp = os.path.join(temp_dir.name, "bf.tiff")
        proc_temp = os.path.join(temp_dir.name, "proc.tif")
        print(bf_temp, proc_temp)

        #In the macro, change where the bf.tiff is stored and where the processed_bf should be saved.
        macro = """
        @ String BFImagePath
        @ String procImagePath

        open(BFImagePath); 
        print("image opened");
        run("EDF Easy mode", "quality='2' topology='0' show-topology='off' show-view='off'");
        print("EDF run");
        while(!isOpen("Output")){
        print("in while-loop");
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
        print("saved");
        close("*");
        """

        arg = {
            "BFImagePath": bf_temp,
            "procImagePath": proc_temp
        }

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

    def convert_to_8bit(self):
        image_8bit = []
        for image in self.image_array:
            image_8bit.append(np.uint8((image / np.max(image)) * 255))

          # Stack the list back into a single numpy array
        self.image_array = np.array(image_8bit)
        return self
    

    def process(self, max_proj=False, min_proj=False, edf_proj=False, edf_BFch=-1, to_8bit=False):
        """Processes the image based on flags for specific operations."""
        if max_proj:
            self.max_projection()
        if min_proj:
            self.min_projection()
        if edf_proj:
            self.EDF_projection(edf_BFch)
        if to_8bit:
            self.convert_to_8bit()
        return self  # Return self to allow method chaining
    
    def get_image(self):
        return self.image_array


if __name__ == "__main__":
    measurement_path = askdirectory(title='Choose measurement directory')
    saving_path = askdirectory(title='Choose saving directory')

    in_measurement_path = [f for f in os.listdir(measurement_path) if not os.path.isdir(f)]
    kw_file = next(x for x in in_measurement_path if x.endswith(".kw.txt"))

    opera_config = OperaExperimentConfigReader(os.path.join(measurement_path, kw_file))
    opera_config_file = opera_config.load_json_from_txt(remove_first_lines=1, remove_last_lines=2)

    planes = opera_config_file["PLANES"]
    channels = len(opera_config_file["CHANNEL"])
    fields = opera_config_file["FIELDS"]

    image_path = os.path.join(measurement_path, "images")
    wells = [w for w in os.listdir(image_path) if os.path.isdir(os.path.join(image_path, w))]

    # Choose which well to test
    well_num = 0
    test_image_path = os.path.join(image_path, wells[well_num])
    
    for i in range(1, fields+1):
        cur_FOV = i
        pattern = fr"r\d+c\d+f0?{cur_FOV}p\d+-ch\d+t\d+.tiff"

        matched_string = [match.group() for file_name in sorted(os.listdir(test_image_path)) if
                                 (match := re.search(pattern, file_name))]

        im_arr_names = [os.path.join(test_image_path, matched_string[i]) for i in range(len(matched_string))]
        im_arr = []
        
        for filepath in im_arr_names:
            im_arr.append(tifffile.imread(filepath))
            if len(im_arr) == 1:
                xdim = len(im_arr[0][1])
                ydim = len(im_arr[0][0])
        im_arr = np.array(im_arr)

        images = np.reshape(im_arr, [planes, channels, xdim, ydim])
        
        processor = ImageProcessor(images, opera_config_file)

        processor.process(edf_proj=1, edf_BFch=2)
        images = processor.get_image()

        tifffile.imwrite(saving_path + f"/{wells[well_num]}_{i}.tif",
                                         processor.get_image(), imagej=True, metadata={'axes': 'CYX'})
                                
    
    