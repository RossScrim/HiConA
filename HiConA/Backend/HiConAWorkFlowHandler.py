import numpy as np
import os

from HiConA.Utilities.ConfigReader import ConfigReader
from HiConA.Utilities.IOread import load_images, save_images, create_directory
from HiConA.Backend.PreProcessor import PreProcessor
from HiConA.Utilities.Image_Utils import get_xy_axis_from_image


class HiConAWorkflowHandler:
    def __init__(self, files, processes_to_run, output_dir):
        self.BFchannel = None
        self.files = files
        self.output_dir = create_directory(output_dir)
        self.processes_to_run = processes_to_run  # Dict with keys = process function name
        
        # extract experimental information from config file
        self.config_file = ConfigReader(files.archived_data_config).load(remove_first_lines=1, remove_last_lines=2)
        if self.config_file is not None:
            self.channels = len(self.config_file["CHANNEL"]) if isinstance(self.config_file["CHANNEL"], list) else 1
            self.planes = self.config_file["PLANES"]
            self.timepoints = self.config_file["TIMEPOINTS"]

        self.axes = self._get_image_axes()

    def _get_num_fov(self, well_name):
        well_path = self.files.get_file_path(well_name)
        image_names = os.listdir(well_path)
        field_nums = [int(f[f.index("f")+1:f.index("p")]) for f in image_names]
        return max(field_nums)

    def _get_image_axes(self):
        axes = ""
        proj = self.processes_to_run.get("proj")

        if self.timepoints > 1:
            axes += "T"
        if self.channels:
            axes += "C"

        if (self.planes > 1
                and proj not in "None"):
            axes += "Z"
        axes += "YX"
        return axes

    def _load_process_fov(self, well_name, FOV, timepoint=None):
        """
        Convenience helper to load images for a single FOV (and optional timepoint),
        process them,
        """
        image_pattern = self.files.build_imagename_pattern(FOV, timepoint)
        try:
            paths = self.files.get_opera_phenix_images_from_FOV(well_name, image_pattern)
            images = load_images(paths)
            processed = self._preprocessor(images)
            return processed

        except ValueError as e:
            print(f"Error processing well {well_name}, FOV {FOV}, timepoint {timepoint} with ValueError.")
            return None

    def _save_image(self, directory, filename, image):
        full_path = os.path.join(directory, filename)
        save_images(full_path, image, self.axes)
        return full_path

    def _process_well(self, cur_well):
        well_output_dir = self.output_dir
        if self.timepoints > 1:
            self._run_timelapse_pipeline(cur_well, well_output_dir)
        else:
            self._run_single_timepoint_pipeline(cur_well, well_output_dir)

    def _run_timelapse_pipeline(self, cur_well, well_output_dir):
        total_field_num = self._get_num_fov(cur_well)

        for cur_FOV in range(1, total_field_num + 1):
            current_images = []
            for cur_time in range(1, self.timepoints+1):
                processed_image = self._load_process_fov(cur_well, cur_FOV, timepoint=cur_time)
                current_images.append(processed_image)

            # Save images as timelapse stack
            time_lapse_image = np.stack(current_images, axis=0)
            save_name = f'{cur_well}_f{cur_FOV}_timelapse_hyperstack.tiff'
            self._save_image(well_output_dir, save_name, time_lapse_image)

    def _run_single_timepoint_pipeline(self, cur_well, well_output_dir):
        total_field_num = self._get_num_fov(cur_well)
        for cur_FOV in range(1, total_field_num + 1):
            processed_image = self._load_process_fov(cur_well, cur_FOV)
            # Save images
            save_name = f'{cur_well}_f{cur_FOV}_hyperstack.tiff'
            self._save_image(well_output_dir, save_name, processed_image)

    def _preprocessor(self, images):
        # Get image dimensions
        ydim, xdim = get_xy_axis_from_image(images)
        image = np.reshape(images, [self.planes, self.channels, ydim, xdim])
        processor = PreProcessor(image, self.config_file)
        processor.process(proj=self.processes_to_run["proj"],
                          edf_BFch="",
                          to_8bit=self.processes_to_run["8bit"],
                          imagej_loc="",
                          imagej_proc_order="",
                          imagej_after_stitching=False)

        return processor.get_image()

    def run(self):
        for cur_well in self.files.well_names:
            print("Processing well: " + cur_well)
            self._process_well(cur_well)

if __name__ == "__main__":
    pass