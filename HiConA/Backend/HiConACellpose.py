import os
import json
import csv
import time
import re
from pathlib import Path
from cellpose import models, io, utils
import numpy as np
import matplotlib.pyplot as plt
import GPUtil
import tifffile

from HiConA.Utilities.IOread import create_directory

class HiConACellposeProcessor:
    def __init__(self, image, image_path):
        self.cellpose_config = self._load_cellpose_config()
        self.seg_ch = self.cellpose_config["channel"]
        self.diameter_data = []

        self.image = image
        self.image_path = image_path
        self.image_name = os.path.basename(os.path.normpath(self.image_path))

        self.well_path, self.measurement_path = self._get_well_path(image_path, r"r\d+c\d+$")

        self.data_processing_file_path = self._generate_processing_data_file()
    
    def _load_cellpose_config(self):
        cellpose_config_f = os.path.join(os.path.dirname(__file__), '..', 'GUI', "cellpose_config.json")
        if os.path.isfile(cellpose_config_f):
            with open(cellpose_config_f, "r+") as f:
                cellpose_config = json.load(f)
                return cellpose_config
        else:
            return None
        
    def _get_well_path(self, image_path, pattern):
        current = Path(image_path).resolve()
        compiled_pattern = re.compile(pattern)

        for parent in [current] + list(current.parents):
            if compiled_pattern.match(parent.name):
                return parent, parent.parent
            
        return None
    
    def _generate_processing_data_file(self):
        file_path = os.path.join(self.measurement_path, "processing_data.csv")
        if not os.path.exists(file_path):
            with open(file_path, mode='w', newline="") as f:
                writer = csv.writer(f)
                writer.writerow(['Filename', 'Estimated Diameter', 'Processing Time [s]'])
                f.close()
        
        return file_path
        
    def _create_dummy_mask(self, image_shape):
        dummy_mask = np.zeros(image_shape[:2], dtype=np.uint8)
        dummy_mask[5:15, 5:15]
        return dummy_mask
    
    def _print_gpu_usage(self):
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            print(f"GPU ID: {gpu.id}, GPU Load: {gpu.load*100}%, Memory Used: {gpu.memoryUsed}MB, Memory Total: {gpu.memoryTotal}MB")

    def _cellpose_segmentation(self):
        try:
            print(f"Processing {self.image_name}, Image shape: {self.image.shape}, dtype: {self.image.dtype}")

            # Start timer
            start_time = time.time()

            # Run cellpose
            model = models.Cellpose(gpu=True, model_type=self.cellpose_config["model"])
            
            masks, flows, styles, diams = model.eval(
                self.image,
                diameter = self.cellpose_config['diameter'],
                channels = [self.seg_ch, 0], #currently only uses one channel, https://cellpose.readthedocs.io/en/v3.1.1.1/settings.html
                flow_threshold = self.cellpose_config['flow_threshold'],
                cellprob_threshold = self.cellpose_config['cellprob_threshold'],
                niter = self.cellpose_config['niter'],
                batch_size = self.cellpose_config['batch_size'],
                do_3D = False
            )

            # End timer
            end_time = time.time()

            processing_time = end_time-start_time
            print(f'Processing time for {self.image_name}: {processing_time}')

            if masks is None or len(masks) == 0:
                print(f'No masks found for {self.image_name}')
                raise ValueError("No masks found")
            
            estimated_diameter = diams if isinstance(diams, (int, float)) else diams[0]
            print(f'Estimated diameter for {self.image_name}: {estimated_diameter}')

            outlines = utils.outlines_list(masks)
            if not outlines:
                print(f"No outlines found for {self.image_name}")
                raise ValueError("No outlines found")
            
            # Save the ROI file
            io.save_rois(masks, os.path.join(self.save_dir, self.image_name.replace('.tiff', '')))

            # Print GPU usage after processing each image
            self._print_gpu_usage()

            return [self.image_path, estimated_diameter, processing_time], masks
        except Exception as e:
            print(f"Error processing {self.image_name}: {e}")
            # Create a more substantial dummy mask
            dummy_mask = self._create_dummy_mask(self.image.shape)

            # Save the dummy mask as in ROI file
            try:
                io.save_rois(dummy_mask, os.path.join(self.save_dir, self.image_name.replace('.tiff', '')))
            except Exception as save_e:
                print(f"Error saving dummy mask for {self.image_name}: {save_e}")

            self._print_gpu_usage()

    def _update_data_processing_file(self, cur_diameter_data):
        with open(self.data_processing_file_path, mode='a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(cur_diameter_data)
            f.close()

    def _save_mask_image(self, masks):
        split_image = np.split(self.image, self.image.shape[-3], axis=-3) # Split along the channel dimension regardless of shape of image
        fig, ax = plt.subplots(figsize=(20,20))
        ax.imshow(np.squeeze(split_image[self.seg_ch-1], -3), cmap='gray')
        ax.imshow(masks, alpha=0.5, cmap='viridis')
        ax.axis('off')

        plt.savefig(os.path.join(self.save_dir, self.image_name.replace('.tiff', '_masks.png')), bbox_inches='tight', dpi=300)
        plt.close()

    def process(self):  
        self.save_dir = create_directory(os.path.join(self.well_path, "cellpose"))

        try:
            cur_diameter_data, masks = self._cellpose_segmentation()
        except Exception as e:
            print(f"Error segmenting image {self.image_path}: {e}")
        try:
            self._update_data_processing_file(cur_diameter_data)
        except Exception as e:
            print(f"Error saving data processing file {self.data_processing_file_path}: {e}")
        try:
            self._save_mask_image(masks)
        except Exception as e:
            print(f"Error saving masks image for {self.image_path}: {e}")

    def get_image(self):
        return self.image

if __name__ == "__main__":
    image_path = r"Z:\Emma\Training Images Florian NEW\25Ope42 - Plate2\r01c01\Stitched\r01c01.tiff"
    image = np.array(tifffile.imread(image_path))
    
    processor = HiConACellposeProcessor(image, image_path)
    processor.process()
    processor.get_image()


