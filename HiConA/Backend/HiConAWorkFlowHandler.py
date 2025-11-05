import tifffile
import numpy as np
import os
from HiConA.Utilities.ConfigReader import ConfigReader
from PreProcessor import PreProcessor


class HiConAWorkflowHandler:
    def __init__(self, files, processes_to_run, config_file, save_dir):
        self.files = files
        self.save_dir = save_dir
        self.processes_to_run = processes_to_run  # Dict with keys = process function name

        # extract experimental information from config file
        self.config_file = config_file
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

    def _load_config_file(self):
        return ConfigReader(
            self.files.archived_data_config).load(remove_first_lines=1, remove_last_lines=2)

    def _load_images(self, filepaths):
        im_arr = np.array([tifffile.imread(fp) for fp in filepaths])
        self.ydim, self.xdim = im_arr.shape[-2], im_arr.shape[-1]
        return im_arr

    def _save_images(self, full_file_path, images, axes_order = "YX"):
        tifffile.imwrite(full_file_path,
                images,
                imagej=True, metadata={'axes': f'{axes_order}'})

    def _well_save_dir(self, cur_well):
        well_save_dir = os.path.join(self.save_dir, cur_well)
        if not os.path.exists(well_save_dir):
            os.makedirs(well_save_dir, exist_ok=True)
        return well_save_dir

    def _get_image_axes(self):
        axes = ""
        if self.timepoints > 1:
            axes += "T"
        if self.channels > 1:
            axes += "C"
        if (self.planes > 1
                and not self.processes_to_run["max_projection"]
                and not self.processes_to_run[:"min_projection"]
                and not self.processes_to_run["EDF_projection"]):
            axes += "Z"
        axes += "YX"
        return axes

    def _build_imagename_pattern(self, FOV, timepoint=None):
        pattern = "r(\d+)c(\d+)f(0?" + str(FOV) + ")(p\d+)-(ch\d+)"
        if timepoint is not None:
            pattern += f"t0?{timepoint}"
        else:
            pattern += f"t01"
        pattern += r".tiff"
        return pattern

    def _load_process_fov(self, well_name, FOV, timepoint=None):
        """
        Convenience helper to load images for a single FOV (and optional timepoint),
        process them,
        """
        image_pattern = self._build_imagename_pattern(FOV, timepoint)
        try:
            paths = self.files.get_opera_phenix_images_from_FOV(well_name, image_pattern)
            images = self._load_images(paths)
            processed = self._preprocessor(images)
            return processed

        except ValueError as e:
            print(f"Error processing well {well_name}, FOV {FOV}, timepoint {timepoint} with ValueError.")
            return None

    def _process_well(self, cur_well):
        well_save_dir = self._well_save_dir(cur_well)
        if self.timepoints > 1:
            self._run_timelapse_pipeline(cur_well, well_save_dir)
        else:
            self._run_single_timepoint_pipeline(cur_well, well_save_dir)

    def _run_timelapse_pipeline(self, cur_well, well_save_dir):
        total_field_num = self._get_num_fov(cur_well)
        for cur_FOV in range(1, total_field_num + 1):
            current_images = []
            for cur_time in range(1, self.timepoints):
                processed_image = self._load_process_fov(cur_well, cur_FOV, timepoint=cur_time)
                current_images.append(processed_image)
            # Save images as timelapse stack
            time_lapse_image = np.stack(current_images, axis=0)
            save_name = f'{cur_well}_f{cur_FOV}_timelapse_hyperstack.tiff'
            full_save_path = os.path.join(well_save_dir, save_name)
            self._save_images(full_save_path, time_lapse_image)

    def _run_single_timepoint_pipeline(self, cur_well, well_save_dir):
        total_field_num = self._get_num_fov(cur_well)
        for cur_FOV in range(1, total_field_num + 1):
            processed_image = self._load_process_fov(cur_well, cur_FOV)
            # Save images
            save_name = f'{cur_well}_f{cur_FOV}_hyperstack.tiff'
            full_save_path = os.path.join(well_save_dir, save_name)
            self._save_images(full_save_path, processed_image)

    def _preprocessor(self, images):
            image = np.reshape(images, [self.planes, self.channels, self.xdim, self.ydim])
            processor = PreProcessor(image, self.config_file)
            processor.process(max_proj=self.processes_to_run["max_projection"],
                              to_8bit=self.processes_to_run["convert_to_8bit"],
                              min_proj=self.processes_to_run["min_projection"],
                              edf_proj=self.processes_to_run["EDF_projection"],
                              edf_BFch=self.BFchannel - 1,
                              imagej_loc=self.imagej_loc,
                              imagej_proc_order=self.imagej_proc_order)
            return processor.get_image()

    def run(self):
        for cur_well in self.files.well_names:
            print("Processing well: " + cur_well)
            self._process_well(cur_well)


if __name__ == "__main__":
    pass