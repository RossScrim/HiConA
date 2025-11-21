import os
import tifffile
import numpy as np

def load_images(filepaths):
    im_arr = np.array([tifffile.imread(fp) for fp in filepaths])
    return im_arr

def save_images(full_file_path, images, axes_order="YX"):
    tifffile.imwrite(full_file_path,
                     images,
                     imagej=True, metadata={'axes': f'{axes_order}'})

def create_directory(output_path: str) -> str:
    os.makedirs(output_path, exist_ok=True)
    return output_path