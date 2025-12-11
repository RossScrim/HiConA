import numpy as np
import os

from HiConA.Utilities.ConfigReader import ConfigReader
from HiConA.Utilities.IOread import load_images, save_images, create_directory
from HiConA.Backend.HiConAPreProcessor import HiConAPreProcessor
from HiConA.Backend.HiConAStitching import HiConAStitching
from HiConA.Utilities.Image_Utils import get_xy_axis_from_image


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
        """Creates the output directory and runs the pipeline for a single well."""
        well_output_dir = create_directory(os.path.join(self.output_dir, cur_well))
        self.stitching_dict = {"well_path": well_output_dir,
                               "xml_reader": self.xml_reader}
        self._run_pipeline(cur_well, well_output_dir)

    def _run_pipeline(self, cur_well, well_output_dir):
        """Manages the iteration over FOVs and timepoints for a well."""
        total_field_num = self._get_num_fov(cur_well)

        # Determine timepoints: single-timepoint -> [None], timelapse -> range(1, N+1)
        timepoints = range(1, self.timepoints + 1) if self.timepoints > 1 else [None]

        for cur_FOV in range(1, total_field_num + 1):
            images_to_stack = []

            for cur_time in timepoints:
                images = self._load_fov(cur_well, cur_FOV, timepoint=cur_time)
                processed = self._process_fov(images, well_name=cur_well, FOV=cur_FOV, timepoint=cur_time)

                if processed is None:
                    # Fail-fast for single-timepoint, log warning for timelapse
                    if len(timepoints) == 1:
                        raise RuntimeError(f"Processing failed for FOV {cur_FOV}, well {cur_well}")
                    else:
                        print(f"Warning: processing failed for FOV {cur_FOV}, timepoint {cur_time}")

                images_to_stack.append(processed)

            # Handle single image or stack
            if len(images_to_stack) > 1:
                final_image = np.stack(images_to_stack, axis=0)
            else:
                final_image = images_to_stack[0]

            # Build save name
            if self.timepoints > 1:
                suffix = "timelapse_hyperstack"
            else:
                suffix = "hyperstack"

            save_name = f"{cur_well}_f{cur_FOV}_{suffix}.tiff"
            self._save_image(well_output_dir, save_name, final_image)

        # Apply stitching if requested
        if self.processes_to_run.get("Stitching"):
            HiConAStitching(self.stitching_dict)

    # --- 4. Mid-Level Processing (Step Logic) ---

    def _process_fov(self, images, well_name=None, FOV=None, timepoint=None):
        """
        Processes a single FOV (and optional timepoint) using the selected segmentation method.
        """
        reshaped_images = self._prepare_hyperstack(images)
        try:
            processed_images = self._preprocessor(reshaped_images)

            #if self.processes_to_run.get("Cellpose"):
             #   processed_images = HiConACellpose(processed_images)
            #elif self.processes_to_run.get("ImageJ"):
                #processed_images = HiConAImageJ(processed_images)
            #else:
             #   raise ValueError("Choose exactly one: Cellpose=True or ImageJ=True")

        except ValueError as e:
            # Error handling catches issues during segmentation setup
            print(f"Error processing well {well_name}, FOV {FOV}, timepoint {timepoint}: {e}")
            return None

        # Return after try/except so it's always reachable
        return processed_images

    def _preprocessor(self, images):
        """Performs image normalization, projection, or EDF before segmentation."""
        # Get image dimensions
        processor = HiConAPreProcessor(images, self.config_file)
        processor.process(proj=self.processes_to_run.get("proj"),
                          edf_channel=self.processes_to_run.get("EDF_channel"),
                          to_8bit=self.processes_to_run.get("8bit", False)
                          )
        return processor.get_image()

    # --- 5. Low-Level Helpers (Utility Functions) ---

    def _get_image_axes(self):
        """Determines the dimension order string (e.g., 'TCZYX') for saving the hyperstack."""
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

    def _get_num_fov(self, well_name):
        """Determines the maximum FOV number from the files in a well's directory."""
        well_path = self.files.get_file_path(well_name)
        image_names = os.listdir(well_path)
        field_nums = [int(f[f.index("f")+1:f.index("p")]) for f in image_names]
        return max(field_nums)

    def _prepare_hyperstack(self, images):

        reshaped_images = np.reshape(images, [self.planes, self.channels, ydim, xdim])
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

    def _save_image(self, directory, filename, image):
        """Saves the processed hyperstack to disk."""
        full_path = os.path.join(directory, filename)
        save_images(full_path, image, self.axes)
        return full_path

if __name__ == "__main__":
    pass