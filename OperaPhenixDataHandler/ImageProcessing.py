import numpy as np
import tifffile
import imagej
import scyjava

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
            self.num_channels = len(self.config_file["CHANNEL"])
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

        #In the macro, change where the bf.tiff is stored and where the processed_bf should be saved.
        macro = """
        open("C:/Users/ewestlund/Documents/Python/Opera Phenix/operavenv/bf.tiff"); 
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
        saveAs("Tiff", "C:/Users/ewestlund/Documents/Python/Opera Phenix/operavenv/processed_bf");
        print("saved");
        close("*");
        """

        processed_image = np.empty((self.num_channels, self.image_x_dim, self.image_y_dim))
        bf_channel = BF_ch #Change which channel is the bf_channel, 0-indexed.
        for ch in range(self.num_channels):
            cur_image = self.image_array[:,ch,:,:] # only get one channel
            if ch == bf_channel:
                tifffile.imwrite("C:/Users/ewestlund/Documents/Python/Opera Phenix/operavenv/bf.tiff", cur_image, imagej=True, metadata={'axes':'ZYX'}) #Change where the bf.tiff is saved.

                ij.py.run_macro(macro)

                bf_array = []
                bf_array.append(tifffile.imread("C:/Users/ewestlund/Documents/Python/Opera Phenix/operavenv/processed_bf.tif")) #Change where the processed_bf.tif is saved.
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
    opera_config = OperaExperimentConfigReader("b02fd523-9bf7-4462-8f31.kw.txt")
    opera_config_file = opera_config.load_json_from_txt(remove_first_lines=1, remove_last_lines=2)

    test_images = tifffile.imread("C:\\Users\\rscrimgeour\\Videos\\Test_stack.tif")
    images = ImageProcessor(test_images, opera_config_file).process(max_proj=True, to_8bit=True).get_image()
                                
    
    