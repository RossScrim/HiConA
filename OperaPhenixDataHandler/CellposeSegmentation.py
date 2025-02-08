import os
import csv
import time
import re
from cellpose import models, io, utils
import numpy as np
from skimage import io as skio
import GPUtil


def cellpose_model():
    model = models.Cellpose(gpu=True, model_type='cyto3')

    #parameters
    diameter = None
    channels = [0, 0]
    flow_threshold = 0.4
    cellprob_threshold = 0.0
    niter = 0
    batch_size = 64 # Adjust based on your GPU capabilities

    return model, diameter, channels, flow_threshold, cellprob_threshold, niter, batch_size

# Function to create a more substantial dummy mask
def create_dummy_mask(image_shape):
    dummy_mask = np.zeros(image_shape[:2], dtype=np.uint8)
    dummy_mask[5:15, 5:15] = 1  # Create a small square mask
    return dummy_mask

# Function to print GPU usage
def print_gpu_usage():
    gpus = GPUtil.getGPUs()
    for gpu in gpus:
        print(f"GPU ID: {gpu.id}, GPU Load: {gpu.load*100}%, Memory Used: {gpu.memoryUsed}MB, Memory Total: {gpu.memoryTotal}MB")




def cellpose_segmentations(cur_well_path):
    cur_diameter_data = []
    image_dir_path = os.path.join(cur_well_path, "Stitched")
    try:
        images = [im for im in os.listdir(image_dir_path) if re.match(".*_ch2.tif", im)] #Change ch to BF image
        bf_image = images[0]
    except Exception as e:
        print(f"{image_dir_path} or the BF image may not exist.")
        return cur_diameter_data
    
    bf_image_path = os.path.join(image_dir_path, bf_image)

    try:
        image = skio.imread(bf_image_path)

        print(f"Processing {bf_image}, Image shape: {image.shape}, dtype: {image.dtype}")

        #Start timer
        start_time = time.time()

        #Run cellpose
        model, diameter, channels, flow_threshold, cellprob_threshold, niter, batch_size = cellpose_model()

        masks, flows, styles, diams = model.eval(
            image,
            diameter=diameter,
            channels=channels,
            flow_threshold=flow_threshold,
            cellprob_threshold=cellprob_threshold,
            niter=niter,
            batch_size=batch_size,
            do_3D=False
        )

        #End time
        end_time = time.time()

        processing_time = end_time-start_time
        print(f"Processing time for {bf_image}: {processing_time}")

        if masks is None or len(masks) == 0:
            print(f"No masks found for {bf_image}")
            raise ValueError("No masks found")
        
        estimated_diameter = diams if isinstance(diams, (int, float)) else diams[0]
        print(f"Estimated diameter for {bf_image}: {estimated_diameter}")
                

        cur_diameter_data.append([bf_image, estimated_diameter, processing_time])

        outlines = utils.outlines_list(masks)
        if not outlines:
            print(f"No outlines found for {bf_image}")
            raise ValueError("No outlines found")
        
        #Save the ROI file
        io.save_rois(masks, os.path.join(image_dir_path, bf_image.replace(".tif", "")))

        # Print GPU usage after processing each image
        print_gpu_usage()

        return cur_diameter_data

    except Exception as e:
        print(f"Error processing {bf_image}: {e}")
        # Create a more substantial dummy mask
        dummy_mask=create_dummy_mask(image.shape)

        # Save the dummy mask as in ROI file
        try:
            io.save_rois(dummy_mask, os.path.join(image_dir_path, bf_image.replace('.tif', '')))
        
        except Exception as save_e:
            print(f"Error saving dummy mask for {bf_image}: {save_e}")

        # Print GPU usage after processing each image
        print_gpu_usage()

    



def cellpose_organiser(measurement_path):                   
    # List to store filename, estimated diameter, and processing time
    diameter_data = []
    wells = [w for w in os.listdir(measurement_path) if os.path.isdir(os.path.join(measurement_path, w))]
    print(wells)

    for well in wells:
        well_path = os.path.join(measurement_path, well)
        cur_diameter_data = cellpose_segmentations(well_path)

        diameter_data.append(cur_diameter_data)


    csv_file_path = os.path.join(measurement_path, "processing_data.csv")
    with open(csv_file_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Filename", "Estimated Diameter", "Processing Time [s]"])
        writer.writerows(diameter_data)

    print(f"Diameter data and processing times have been saved to {csv_file_path}")

if __name__ == "__main__":
    cellpose_organiser("Z:/Florian/bce184b7-d089-418f-b0cd-57c5193941ef")