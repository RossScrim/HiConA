import numpy as np
import os
import tifffile

from HiConA.Utilities.ConfigReader import ConfigReader
from HiConA.Utilities.IOread import load_images, save_images, create_directory
from HiConA.Backend.HiConAPreProcessor import HiConAPreProcessor
from HiConA.Backend.HiConAStitching import HiConAStitching
from HiConA.Utilities.Image_Utils import get_xy_axis_from_image
from HiConA.Backend.HiConAImageJMacro import HiConAImageJProcessor


class HiConAWorkflowHandler:
    def __init__(self, xml_reader, files, processes_to_run, output_dir):
        self.files = files
        self.processes_to_run = processes_to_run  # Dict with keys = process function name
        self.xml_reader = xml_reader
        # extract experimental information from config file
        self.config_file = ConfigReader(files.archived_data_config).load(remove_first_lines=1, remove_last_lines=2)
        if self.config_file is not None:
            self.channels = len(self.config_file["CHANNEL"]) if isinstance(self.config_file["CHANNEL"], list) else 1
            self.planes = self.config_file["PLANES"]
            self.timepoints = self.config_file["TIMEPOINTS"]
            self.measurement_name = self.config_file["PLATENAME"]

        self.output_dir = os.path.join(output_dir, self.measurement_name)
        self.axes = self._get_image_axes()
    # --- 2. Public Interface ---

    def run(self):
        """Starts the high-content imaging processing workflow."""
        for cur_well in self.files.well_names:
            print("Processing well: " + cur_well)
            self._process_well(cur_well)

    # --- 3. High-Level Flow Control (Well/Pipeline Management) ---
    def _process_well(self, cur_well):
        """Process a single well, including optional stitching and advanced processing."""
        well_output_dir = create_directory(os.path.join(self.output_dir, cur_well))
        if self.processes_to_run.get("stitching", 1):
            self._run_stitching_pipeline(cur_well, well_output_dir)
        else:
            self._run_preprocessing_pipeline(cur_well, well_output_dir)

        if self.processes_to_run.get("imagej", 1):
            self._run_imagej_pipeline(cur_well, well_output_dir)
        elif self.processes_to_run.get("cellpose", 1):
            self._run_cellpose_pipeline(cur_well, well_output_dir)

    def _run_preprocessing_pipeline(self, cur_well, well_output_dir):
        """Loop over FOVs and timepoints, preprocess, apply optional advanced processing, and save."""
        total_fov = self._get_num_fov(cur_well)
        timepoints = range(1, self.timepoints + 1) if self.timepoints > 1 else [None]

        for fov in range(1, total_fov + 1):
            images_to_stack = []
            for t in timepoints:
                images = self._load_fov(cur_well, fov, t)
                preprocessed = self._apply_preprocess(images)
                images_to_stack.append(preprocessed)

            print(np.shape(images_to_stack))
            # Stack multiple timepoints into a single hyperstack if needed
            if len(images_to_stack) > 1:
                final_image = np.stack(images_to_stack, axis=0)
                suffix = "timelapse_hyperstack"
            else:
                final_image = images_to_stack[0]
                suffix = "hyperstack"
            print(np.shape(final_image), "final image shape")
            save_name = os.path.join(well_output_dir, f"{cur_well}_f{str(fov).zfill(2)}_{suffix}.tiff")
            self._save_fov(save_name, final_image)

            #TODO Add function for splitting channels, both timelapse data and 2D and 3D
            #if self.processes_to_run.get("stitching", 1) or self.processes_to_run.get("sep_ch", 1):
            #    for ch in range(self.channels):
            #        ch_dir = create_directory(os.path.join(well_output_dir, f"ch{ch+1}"))
            #        split_image = final_image[ch,:,:]
            #        save_split_name = os.path.join(ch_dir, f"{cur_well}_f{str(fov).zfill(2)}.tiff")
            #        self._save_fov(save_split_name, split_image)

    def _run_stitching_pipeline(self, cur_well, well_output_dir):
        """Loop over FOVs and timepoints, preprocess, apply optional advanced processing, and save."""
        total_fov = self._get_num_fov(cur_well)
        timepoints = range(1, self.timepoints + 1) if self.timepoints > 1 else [None]

        stitching_dict = {"well_output_dir": well_output_dir,
                          "xml_reader":self.xml_reader}

        for t in timepoints:
            for fov in range(1, total_fov + 1):
                preprocessed = self._load_fov(cur_well, fov, t)
                preprocessed = self._apply_preprocess(preprocessed)

                #final_image = preprocessed
                #suffix = "hyperstack"
                #save_name = os.path.join(well_output_dir, f"{cur_well}_f{str(fov).zfill(2)}_{suffix}.tiff")
                #self._save_fov(save_name, final_image)

                #TODO Look at 3D. Currently only works for 2D images
                for ch in range(self.channels):
                    ch_dir = create_directory(os.path.join(well_output_dir, f"ch{ch+1}"))
                    split_image = preprocessed[ch,:,:]
                    save_split_name = os.path.join(ch_dir, f"{cur_well}_f{str(fov).zfill(2)}.tiff")
                    self._save_fov(save_split_name, split_image)

            HiConAStitching(stitching_dict)
            #TODO processed = self._apply_advanced_processes(stitched_images)

    def _run_imagej_pipeline(self, cur_well, well_output_dir):
        image_path = os.path.join(well_output_dir, "Stitched", cur_well+".tiff")
        image = np.array(tifffile.imread(image_path))[0]
        imagejprocessor = HiConAImageJProcessor(image)
        imagejprocessor.process()
        processed_image = imagejprocessor.get_image()

        save_name = os.path.join(well_output_dir, "Stitched", f"{cur_well}_imagejprocessed.tiff")
        self._save_fov(save_name, processed_image)

    def _run_cellpose_pipeline(self, cur_well, well_output_dir):
        pass

    def _apply_preprocess(self, images):
        """Normalize, project, or EDF the hyperstack before any further processing."""
        hyperstack = self._prepare_hyperstack(images)
        print(np.shape(hyperstack))
        processor = HiConAPreProcessor(hyperstack, self.config_file)
        processor.process(
            projection=self.processes_to_run.get("proj"),
            EDF_channel=self.processes_to_run.get("EDF_channel"),
            to_8bit=self.processes_to_run.get("8bit", False)
        )
        return processor.get_image()

    def _apply_advanced_processes(self, hyperstack):
        """Optional segmentation (Cellpose/ImageJ) on single FOV or stitched hyperstack."""
        if self.processes_to_run.get("cellpose", 1):
            # Example placeholder: replace with your actual Cellpose class
            HiConACellpose(hyperstack)
        elif self.processes_to_run.get("imagej", 1):
            # Example placeholder: replace with your actual ImageJ processing
            HiConAImageJ(hyperstack)

    # --- 5. Low-Level Helpers (Utility Functions) ---
    def _get_image_axes(self):
        """Determines the dimension order string (e.g., 'TCZYX') for saving the hyperstack."""
        axes = ""
        proj = self.processes_to_run.get("proj")
        if self.timepoints > 1:
            axes += "T"
        if (self.planes > 1 and proj == "None"):
            axes += "Z"
        if self.channels and not self.processes_to_run.get("stitching", 1):
            axes += "C"
        axes += "YX"

        return axes

    def _get_num_fov(self, well_name):
        """Determines the maximum FOV number from the files in a well's directory."""
        well_path = self.files.get_file_path(well_name)
        image_names = os.listdir(well_path)
        field_nums = [int(f[f.find("f")+1:f.find("p")]) for f in image_names if not f.endswith(".db")]
        return max(field_nums)

    def _prepare_hyperstack(self, images):
        y_axis, x_axis = get_xy_axis_from_image(images)
        reshaped_images = np.reshape(images, [self.planes, self.channels, y_axis, x_axis])
        return reshaped_images

    def _load_fov(self,well_name, FOV, timepoint=None):
        """
           Load images for a specific FOV (and optional timepoint) using the generic loader.

           Parameters:
               well_name (str): Name of the well
               FOV (int): Field of view number
               timepoint (int, optional): Timepoint index. Defaults to None.
         """
        image_pattern = self.files.build_imagename_pattern(FOV, timepoint)
        paths = self.files.get_opera_phenix_images_from_FOV(well_name, image_pattern)
        return load_images(paths)

    def _save_fov(self, full_path, image):
        pixel_size_um = self.xml_reader.get_pixel_scale()
        print(pixel_size_um)
        print(self.axes)
        """Saves the processed hyperstack to disk."""
        save_images(full_path, image, pixel_size_um, self.axes)
        return full_path

if __name__ == "__main__":
    pass