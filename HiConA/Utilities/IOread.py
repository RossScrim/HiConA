import os
import tifffile
import numpy as np

def load_images(filepaths):
    im_arr = np.array([tifffile.imread(fp) for fp in filepaths])
    return im_arr

def save_images(full_file_path, images, pixel_size_um, axes_order="YX"):
    tifffile.imwrite(full_file_path,
                     images,
                     imagej=True, 
                     metadata={
                        'axes': f'{axes_order}',
                        'PhysicalSizeX': pixel_size_um,
                        'PhysicalSizeY': pixel_size_um,
                        'PhysicalSizeXUnit': 'um',
                        'PhysicalSizeYUnit': 'um'})

def create_directory(output_path: str) -> str:
    os.makedirs(output_path, exist_ok=True)
    return output_path