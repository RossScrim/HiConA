import imagej
import os
import re
import scyjava
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from shutil import copy

class HiConAStitching:
    def __init__(self, stitching_dir): # stitching_dir to include imagej_loc, path to well to process, reference channel. Where to generate the TileConfigurationFile...?
        print("initialising")
        imagej_loc = stitching_dir["imagej_loc"]
        self._initiate_imagej(imagej_loc)

        well_path = stitching_dir["well_path"]
        ref_ch = stitching_dir["ref_ch"]
        self._process_well(well_path, ref_ch)


    def _initiate_imagej(self, imagej_loc):
        plugins_dir = os.path.join(imagej_loc, "plugins") # Path to Fiji Plugins
        scyjava.config.add_option(f'-Dplugins.dir={plugins_dir}')
        self.ij = imagej.init(imagej_loc)  # Path to Fiji-folder
    
    def _create_dir(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def _copy_tile_configure_files(self, ref_ch_dir, well_path, ch_directories):
        stitch_configuration_files = [f for f in os.listdir(ref_ch_dir) if f.endswith(".txt")]

        for ch_dir in ch_directories:
            ch_path = os.path.join(well_path, ch_dir)

            for config in stitch_configuration_files:
                copy(os.path.join(ref_ch_dir, config), os.path.join(ch_path, config))

    def _stitch_first_image(self, orgDir, saveDir, wellName, chName):
    #In the macro, change where the bf.tiff is stored and where the processed_bf should be saved.
        macro = """
        //@ String orgDir
        //@ String saveDir
        //@ String wellName
        //@ String chName

        run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration] directory=["+orgDir+"] layout_file=TileConfiguration_"+wellName+".txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap computation_parameters=[Save memory (but be slower)] image_output=[Fuse and display]");
        saveAs("Tiff", saveDir+File.separator+wellName+"_"+chName+".tif");
        close("*");
        """

        args = {
            'orgDir': orgDir,
            'saveDir': saveDir,
            'wellName': wellName,
            'chName': chName
        }

        self.ij.py.run_macro(macro, args)

    def _stitch_remaining_image(self, orgDir, saveDir, wellName, chName):
        #In the macro, change where the bf.tiff is stored and where the processed_bf should be saved.
        macro = """
        //@ String orgDir
        //@ String saveDir
        //@ String wellName
        //@ String chName

        run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration] directory=["+orgDir+"] layout_file=TileConfiguration_"+wellName+".registered.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 subpixel_accuracy computation_parameters=[Save memory (but be slower)] image_output=[Fuse and display]");

        saveAs("Tiff", saveDir+File.separator+wellName+"_"+chName+".tif");
        close("*");
        """

        args = {
            'orgDir': orgDir,
            'saveDir': saveDir,
            'wellName': wellName,
            'chName': chName
        }

        self.ij.py.run_macro(macro, args)

    
    def _mergeImages(self, orgDir, wellName):
        macro = """
        //@ String orgDir
        //@ String wellName
    
        File.openSequence(orgDir, " open");
        run("Images to Stack", "method=[Scale (smallest)] name="+wellName);

        run("Re-order Hyperstack ...", "channels=[Slices (z)] slices=[Channels (c)] frames=[Frames (t)]");

        saveAs("Tiff", orgDir+File.separator+wellName+".tif");

        close("*");
        """

        args = {
            'orgDir': orgDir,
            'wellName': wellName
        }

        self.ij.py.run_macro(macro, args)
    
    def _process_well(self, well_path, ref_ch):
        wellName = os.path.basename(os.path.normpath(well_path))

        stitched_path = os.path.join(well_path, "Stitched")
        self._create_dir(stitched_path)

        ch_directories = [d for d in os.listdir(well_path) if os.path.isdir(os.path.join(well_path, d)) and d.startswith("ch") and d != "ch"+str(ref_ch)]
        ref_ch_dir = os.path.join(well_path, "ch"+str(ref_ch))

        self._stitch_first_image(ref_ch_dir, stitched_path, wellName, "ch"+str(ref_ch))

        self._copy_tile_configure_files(ref_ch_dir, well_path, ch_directories)

        for ch_dir in ch_directories:
            ch_path = os.path.join(well_path, ch_dir)

            self._stitch_remaining_image(ch_path, stitched_path, wellName, ch_dir)

        if len(ch_directories) != 0:
            self._mergeImages(stitched_path, wellName)
    
        self.ij.dispose()

if __name__ == "__main__":
    test_path = r"Z:\Emma\MMC poster\Processed\18112025_LS411N_ATX968_S9.6 - 1\r04c05"
    ref_ch = 2
    imagej_loc = r"C:\Users\ewestlund\Fiji"

    stitching_dir = {
        "imagej_loc": imagej_loc,
        "well_path": test_path,
        "ref_ch": ref_ch
    }

    HiConAStitching(stitching_dir)