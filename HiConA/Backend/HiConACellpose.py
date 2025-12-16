import os
import json
import csv
import time
import re
from cellpose import models, io, utils
import numpy as np
from skimage import io as skio
import GPUtil
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.filedialog import askdirectory

class HiConACellpose:
    def __init__(self, measurement_path):
        self.cellpose_config = self._load_cellpose_config()
        self.seg_ch = self.cellpose_config["channel"]
        self.diameter_data = []
        self.measurement_path = measurement_path
    
    def _load_cellpose_config(self):
        cellpose_config_f = os.path.join(os.path.dirname(__file__), '..', 'GUI', "cellpose_config.json")
        if os.path.isfile(cellpose_config_f):
            with open(cellpose_config_f, "r+") as f:
                cellpose_config = json.load(f)
                return cellpose_config
        else:
            return None
        
    def _create_dummy_mask(self, image_shape):
        dummy_mask = np.zeros(image_shape[:2], dtype=np.uint8)
        dummy_mask[5:15, 5:15]
        return dummy_mask
    
    def _print_gpu_usage(self):
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            print(f"GPU ID: {gpu.id}, GPU Load: {gpu.load*100}%, Memory Used: {gpu.memoryUsed}MB, Memory Total: {gpu.memoryTotal}MB")

    def _cellpose_segmentation(self, image_path):
        cur_diameter_data = []

        image_name = os.path.basename(os.path.normpath(image_path))

        try:
            image = skio.imread(image_path)

            print(f"Processing {image_name}, Image shape: {image.shape}, dtype: {image.dtype}")

            # Start timer
            start_time = time.time()

            # Run cellpose
            model = models.Cellpose(gpu=True, model_type=self.cellpose_config["model"])
            
            masks, flows, styles, diams = model.eval(
                image,
                diameter = self.cellpose_config['diameter'],
                channels = [0, 0], #currently only process in grey scale, https://cellpose.readthedocs.io/en/v3.1.1.1/settings.html
                flow_threshold = self.cellpose_config['flow_threshold'],
                cellprob_threshold = self.cellpose_config['cellprob_threshold'],
                niter = self.cellpose_config['niter'],
                batch_size = self.cellpose_config['batch_size'],
                do_3D = False
            )

            # End timer
            end_time = time.time()

            processing_time = end_time-start_time
            print(f'Processing time for {image_name}: {processing_time}')

            if masks is None or len(masks) == 0:
                print(f'No masks found for {image_name}')
                raise ValueError("No masks found")
            
            estimated_diameter = diams if isinstance(diams, (int, float)) else diams[0]
            print(f'Estimated diameter for {image_name}: {estimated_diameter}')

            cur_diameter_data.append([image_path, estimated_diameter, processing_time])

            outlines = utils.outlines_list(masks)
            if not outlines:
                print(f"No outlines found for {image_name}")
                raise ValueError("No outlines found")
            
            # Save the ROI file
            io.save_rois(masks, os.path.join(image_path, "..", image_name.replace('.tif', '')))

            # Print GPU usage after processing each image
            self._print_gpu_usage()

            return cur_diameter_data
        except Exception as e:
            print(f"Error processing {image_name}: {e}")
            # Create a more substantial dummy mask
            dummy_mask = self._create_dummy_mask(image.shape)

            # Save the dummy mask as in ROI file
            try:
                io.save_rois(dummy_mask, os.path.join(image_path, "..", image_name.replace('.tif', '')))
            except Exception as save_e:
                print(f"Error saving dummy mask for {image_name}: {save_e}")

            self._print_gpu_usage()

    def generate_data_processing_file(self):
        previous_files = [int(file.split("_")[-1][:-4]) for file in os.listdir(measurement_path) if file.endswith(".csv")]
        i = max(previous_files)+1 if len(previous_files) > 0 else 0

        csv_file_path = os.path.join(self.measurement_path, 'processing_data_'+str(i)+'.csv')
        with open(csv_file_path, mode='w', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Filename", "Estimated Diameter", "Processing Time [s]"])
            writer.writerows(self.diameter_data)

    def process(self, well_path):  
        if self.cellpose_config["process"] == "stitched image":
            stitched_path = os.path.join(well_path, "Stitched")
            all_images = [im for im in os.listdir(stitched_path) if im.endswith(str(self.seg_ch)+".tif")]
            stitched_image_path = os.path.join(stitched_path, all_images[0])
            
            cur_diameter_data = self._cellpose_segmentation(stitched_image_path)

            self.diameter_data.append(cur_diameter_data)
        elif self.cellpose_config['process'] == "each FOV":
            seg_ch_image_path = os.path.join(well_path, "ch"+str(self.seg_ch))
            all_images = [im for im in os.listdir(seg_ch_image_path) if im.endswith(".tif")]

            for image in all_images:
                image_path = os.path.join(seg_ch_image_path, image)

                cur_diameter_data = self._cellpose_segmentation(image_path)

                self.diameter_data.append(cur_diameter_data)


if __name__ == "__main__":
    measurement_path = r"Z:\Emma\Training Images Florian NEW\25Ope42 - Plate2"
    wells = [w for w in os.listdir(measurement_path) if os.path.isdir(os.path.join(measurement_path, w))]
    
    measurement_cellpose = HiConACellpose(measurement_path)
    for well in wells[:1]:
        well_path = os.path.join(measurement_path, well)
        measurement_cellpose.process(well_path)

    measurement_cellpose.generate_data_processing_file()


