import numpy as np
import os
import scyjava
from shutil import copy
import json
import math
import tifffile
import re
import imagej
import scyjava

from HiConA.Utilities.ConfigReader_XML import XMLConfigReader
from HiConA.Utilities.Image_Utils import get_xy_axis_from_image
from HiConA.Backend.ImageJ_singleton import ImageJSingleton
from HiConA.Utilities.IOread import save_images

class HiConA3DStitching:
    def __init__(self, well_dir, xml_file, save_dir, ref_ch, imagej_loc):
        self.well_dir = well_dir
        self.well_name = os.path.basename(well_dir)
        self.xml_reader = XMLConfigReader(xml_file)

        self.num_planes = self.xml_reader.get_num_planes()
        self.num_channels = len(self.xml_reader.get_channel_order())
        self.num_FOVs = 4
        self.ref_ch = ref_ch

        self.save_dir = save_dir

        print(imagej_loc)

        plugins_dir = os.path.join(imagej_loc, "plugins") # Path to Fiji Plugins
        scyjava.config.add_option(f'-Dplugins.dir={plugins_dir}')
        self.ij = imagej.init(imagej_loc, mode='interactive')

    def process_3D_stitching(self):
        
        for plane in range(1, self.num_planes+1):
            image_stack = []
            for fov in range(1, self.num_FOVs+1):
                image = self._get_images(plane, fov)
                image_stack.append(image)
            
            y_axis, x_axis = get_xy_axis_from_image(image)

            images = np.reshape(image_stack, [self.num_FOVs, self.num_channels, y_axis, x_axis])

            self._split_save_images(images, plane, fov)
        
        self._generate_TileConfiguration_middle_plane(self.well_name, math.ceil(self.num_planes/2))
        #self._copy_TileConfiguration_files()
        
        self._stitch_images()
        
        self._stack_images()

    def _get_images(self, cur_plane, cur_fov):
        image_pattern = rf"{self.well_name}f0?{cur_fov}p0?{cur_plane}-ch\d+t\d+.tiff"
        images = np.array([tifffile.imread(os.path.join(self.well_dir, fp)) for fp in os.listdir(self.well_dir) if re.match(image_pattern, fp)])
        return images

    def _split_save_images(self, images, cur_plane, cur_fov):
        cur_save_dir = os.path.join(self.save_dir, str(cur_plane))
        os.makedirs(cur_save_dir, exist_ok=True)
        
        split_image = np.split(images, images.shape[-3], axis=-3)
        for ch in range(self.num_channels):
            cur_save_dir_ch = os.path.join(cur_save_dir, f"ch{ch+1}")
            os.makedirs(cur_save_dir_ch, exist_ok=True)

            cur_image = split_image[ch]
            for f in range(self.num_FOVs):
                tifffile.imwrite(os.path.join(cur_save_dir_ch, f"{self.well_name}_f{str(f+1).zfill(2)}.tiff"), cur_image[f])

    def _generate_TileConfiguration_middle_plane(self, well_name, plane):
        output_dir = os.path.join(self.save_dir, str(plane),  f"ch{self.ref_ch}")

        well_layout = self.xml_reader.get_well_layout()

        self.xml_reader.generate_TileConfiguration(well_layout, well_name, output_dir)
    
    def _copy_TileConfiguration_files(self):
        stitch_configuration_files = [f for f in os.listdir(os.path.join(self.save_dir, str(math.ceil(self.num_planes/2)),  f"ch{self.ref_ch}")) if f.endswith(".txt")]
        ch_directories = [os.path.join(self.save_dir, str(p), "ch1") for p in range(1, self.num_planes+1) if p != math.ceil(self.num_planes/2)]

        for ch_dir in ch_directories:
            ch_path = ch_dir

            for config in stitch_configuration_files:
                copy(os.path.join(self.save_dir, str(math.ceil(self.num_planes/2)),  f"ch{self.ref_ch}", config), os.path.join(ch_path, config))


    def _stitch_images(self):
        mid_plane = math.ceil(self.num_planes/2)
        orgDir = os.path.join(self.save_dir, str(mid_plane), f"ch{self.ref_ch}")
        saveDir = os.path.join(self.save_dir, str(mid_plane), "stitching")
        os.makedirs(saveDir, exist_ok=True)
        chName = f"ch{self.ref_ch}"
        pixelScale = self.xml_reader.get_pixel_scale()

        print("stitching first image:", mid_plane, chName)
        self._stitch_first_image(orgDir, saveDir, self.well_name, chName, pixelScale)
        
        ch_directories = [os.path.join(self.save_dir, str(p), f"ch{ch}") for p in range(1, self.num_planes+1) for ch in range(1, self.num_channels+1) if not (p == mid_plane and ch == self.ref_ch)]
        
        if len(ch_directories) != 0:
                self._copy_tile_configure_files(orgDir, os.path.join(self.save_dir, str(mid_plane)), ch_directories)

        ch_directories.append(orgDir)
        for ch_dir in ch_directories:
            orgDir = ch_dir
            plane = f"{os.path.basename(os.path.dirname(ch_dir))}"
            chName = f"{os.path.basename(ch_dir)}"

            saveDir = os.path.join(self.save_dir, plane, "stitching")
            os.makedirs(saveDir, exist_ok=True)

            print("stitching remaining image:", plane, chName)
            self._stitch_remaining_image(orgDir, saveDir, self.well_name, chName, pixelScale)

        for plane in range(1, self.num_planes+1):
            orgDir = os.path.join(self.save_dir, str(plane), "stitching")
            merged_save_dir = os.path.join(self.save_dir, "stitching")
            os.makedirs(merged_save_dir, exist_ok=True)
            self._mergeImages(orgDir, merged_save_dir, self.well_name, pixelScale, plane)


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

    
    def _mergeImages(self, orgDir, saveDir, wellName, pixelScale, plane):
        macro = """
        //@ String orgDir
        //@ String saveDir
        //@ String wellName
        //@ float scale
        //@ String plane
    
        File.openSequence(orgDir, " open");
        run("Images to Stack", "method=[Scale (smallest)] name="+wellName);

        run("Re-order Hyperstack ...", "channels=[Slices (z)] slices=[Channels (c)] frames=[Frames (t)]");
        imageID = getImageID();
        run("Set Scale...", "distance=1 known="+scale+" unit=um");
        saveAs("Tiff", saveDir+File.separator+wellName+"_p"+plane+".tiff");
        close("*");
        """

        args = {
            'orgDir': orgDir,
            'saveDir': saveDir,
            'wellName': wellName,
            'scale': pixelScale,
            'plane': str(plane)
        }

        self.ij.py.run_macro(macro, args)

    def _stack_images(self):
        stitched_dir = os.path.join(self.save_dir, "stitching")

        image_stack = []

        for im in os.listdir(stitched_dir):
            if im.endswith(".tiff"):
                image_stack.append(np.array(tifffile.imread(os.path.join(stitched_dir, im))))

        y_axis, x_axis = get_xy_axis_from_image(image_stack[0])
        images = np.reshape(image_stack, [self.num_planes, self.num_channels, y_axis, x_axis])

        full_file_path = os.path.join(self.save_dir, f"{self.well_name}.tiff")
        pixel_size_um = self.xml_reader.get_pixel_scale()
        axes_order = 'ZCYX'
        channels = self.xml_reader.get_channel_order()

        save_images(full_file_path, images, pixel_size_um, axes_order, channels)


if __name__ == "__main__":
    test_well_dir = r"Z:\Emma\Katie_3D_Spheroids\hs\eb59079d-f67a-4305-9d33-3f819798c47b\images\r05c03"
    xml_file = r"Z:\Emma\Katie_3D_Spheroids\hs\eb59079d-f67a-4305-9d33-3f819798c47b\eb59079d-f67a-4305-9d33.xml"
    save_dir = r"Z:\Emma\HiConA_3DStitching_test\Katie\r05c03"

    imagej_location = r"C:\Users\ewestlund\Fiji"

    HiConA3DStitching = HiConA3DStitching(test_well_dir, xml_file, save_dir, 1, imagej_location)
    HiConA3DStitching.process_3D_stitching()