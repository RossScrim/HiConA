import numpy as np
import os
import scyjava
from shutil import copy
import json

from HiConA.Utilities.ConfigReader_XML import XMLConfigReader
from HiConA.Backend.ImageJ_singleton import ImageJSingleton

class HiConAStitching:
    def __init__(self, stitching_dir): # stitching_dir to include path to well to process, XML_reader
        self.saved_variables = self._load_variables()
        
        imagej_loc = self.saved_variables["imagej_loc"]
        
        self.ref_ch = self.saved_variables["stitch_ref_ch"]
        self.well_path = stitching_dir["well_output_dir"]
        self.well_name = os.path.basename(os.path.normpath(self.well_path))
        self.xml_reader = stitching_dir["xml_reader"]
        
        self._generate_TileConfiguration(self.xml_reader, self.well_path, self.well_name, self.ref_ch)
        self.ij = ImageJSingleton.get_instance(imagej_loc)

    def _load_variables(self):
        saved_variables_f = os.path.join(os.path.dirname(__file__), '..', 'GUI', "processing_variables.json")
        if os.path.isfile(saved_variables_f):
            with open(saved_variables_f, "r+") as f:
                saved_var = json.load(f)
                return saved_var
        else:
            return None
        
    def _generate_TileConfiguration(self, xml_reader, well_path, well_name, ref_ch):
        output_dir = os.path.join(well_path, f"ch{ref_ch}")

        well_layout = xml_reader.get_well_layout()

        xml_reader.generate_TileConfiguration(well_layout, well_name, output_dir)
    
    def _create_dir(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def _copy_tile_configure_files(self, ref_ch_dir, well_path, ch_directories):
        stitch_configuration_files = [f for f in os.listdir(ref_ch_dir) if f.endswith(".txt")]

        for ch_dir in ch_directories:
            ch_path = os.path.join(well_path, ch_dir)

            for config in stitch_configuration_files:
                copy(os.path.join(ref_ch_dir, config), os.path.join(ch_path, config))

    def _stitch_first_image(self, orgDir, saveDir, wellName, chName, pixelScale):
    #In the macro, change where the bf.tiff is stored and where the processed_bf should be saved.
        macro = """
        //@ String orgDir
        //@ String saveDir
        //@ String wellName
        //@ String chName
        //@ float scale

        run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration] directory=["+orgDir+"] layout_file=TileConfiguration_"+wellName+".txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap computation_parameters=[Save memory (but be slower)] image_output=[Fuse and display]");
        imageID = getImageID();
        run("Set Scale...", "distance=1 known="+scale+" unit=um");
        saveAs("Tiff", saveDir+File.separator+wellName+"_"+chName+".tiff");
        selectImage(imageID);
        """

        args = {
            'orgDir': orgDir,
            'saveDir': saveDir,
            'wellName': wellName,
            'chName': chName,
            'scale': pixelScale
        }

        self.ij.py.run_macro(macro, args)

    def _stitch_remaining_image(self, orgDir, saveDir, wellName, chName, pixelScale):
        #In the macro, change where the bf.tiff is stored and where the processed_bf should be saved.
        macro = """
        //@ String orgDir
        //@ String saveDir
        //@ String wellName
        //@ String chName
        //@ float scale

        run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration] directory=["+orgDir+"] layout_file=TileConfiguration_"+wellName+".registered.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 subpixel_accuracy computation_parameters=[Save memory (but be slower)] image_output=[Fuse and display]");
        run("Set Scale...", "distance=1 known="+scale+" unit=um");
        saveAs("Tiff", saveDir+File.separator+wellName+"_"+chName+".tiff");
        close("*");
        """

        args = {
            'orgDir': orgDir,
            'saveDir': saveDir,
            'wellName': wellName,
            'chName': chName,
            'scale': pixelScale
        }

        self.ij.py.run_macro(macro, args)

    
    def _mergeImages(self, orgDir, wellName, pixelScale):
        macro = """
        //@ String orgDir
        //@ String wellName
        //@ float scale
    
        File.openSequence(orgDir, " open");
        run("Images to Stack", "method=[Scale (smallest)] name="+wellName);

        run("Re-order Hyperstack ...", "channels=[Slices (z)] slices=[Channels (c)] frames=[Frames (t)]");
        imageID = getImageID();
        run("Set Scale...", "distance=1 known="+scale+" unit=um");
        saveAs("Tiff", orgDir+File.separator+wellName+".tiff");
        selectImage(imageID);
        """

        args = {
            'orgDir': orgDir,
            'wellName': wellName,
            'scale': pixelScale
        }

        self.ij.py.run_macro(macro, args)

    def _set_output_image(self):
        WindowManager = scyjava.jimport('ij.WindowManager')
        output_image = WindowManager.getCurrentImage()

        #print(f"Output image type: {type(output_image)}")

        if output_image is not None:
            processed_image = self.ij.py.from_java(output_image)

            if hasattr(processed_image, 'dims'):
                #print(f"Dimension names: {processed_image.dims}")
                desired_order = [d for d in ['T', 'Z', 'C', 'Y', 'X'] if d in processed_image.dims]
                processed_image = processed_image.transpose(*desired_order)
                processed_image = processed_image.values

            #print(f"Array shape: {processed_image.shape}")

            output_image.close()

            necessary_type = np.uint16
            min_value = np.iinfo(necessary_type).min # 0
            max_value = np.iinfo(necessary_type).max # 65535
            array_clipped = np.clip(processed_image, min_value, max_value)
            self.image_array = array_clipped.astype(necessary_type)

    def _stitch_well(self, xml_reader, well_path, well_name, ref_ch):
        stitched_path = os.path.join(well_path, "stitching")
        self._create_dir(stitched_path)

        pixelScale = xml_reader.get_pixel_scale()

        ch_directories = [d for d in os.listdir(well_path) if os.path.isdir(os.path.join(well_path, d)) and d.startswith("ch") and d != "ch"+str(ref_ch)]
        ref_ch_dir = os.path.join(well_path, "ch"+str(ref_ch))

        self._stitch_first_image(ref_ch_dir, stitched_path, well_name, "ch"+str(ref_ch), pixelScale)

        if len(ch_directories) != 0:
            self._copy_tile_configure_files(ref_ch_dir, well_path, ch_directories)

            for ch_dir in ch_directories:
                ch_path = os.path.join(well_path, ch_dir)

                self._stitch_remaining_image(ch_path, stitched_path, well_name, ch_dir, pixelScale)

            self._mergeImages(stitched_path, well_name, pixelScale)

        self._set_output_image()

    def process(self):
        self._stitch_well(self.xml_reader, self.well_path, self.well_name, self.ref_ch)

    def getImage(self):
        return self.image_array


if __name__ == "__main__":
    well_path = r"Z:\Emma\MMC poster\Processed\18112025_LS411N_ATX968_S9.6 - 1\r04c05"
    ref_ch = 2

    xml_reader = XMLConfigReader(r"Z:\Emma\hs\bb41dbf0-41ce-4913-ac11-9a37ce70c088\bb41dbf0-41ce-4913-ac11.xml")

    stitching_dir = {
        "well_path": well_path,
        "xml_reader": xml_reader
    }

    HiConAStitching(stitching_dir)