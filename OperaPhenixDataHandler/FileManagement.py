import os
import re
import fnmatch

def generate_well_names(dir_path: str):
    pattern = 'r(\d+)c(\d+)'

    unique_matched_wells = set()

    for file_name in os.listdir(dir_path):
        match = re.search(pattern, file_name)
        if match:
            matched_wells = match.group()
            unique_matched_wells.add(matched_wells)

    return sorted(unique_matched_wells)


def create_dir(save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)


def build_timelapse_image_filename(dir_path: str, well_name: str, field_name: str, plane: int, channel: int, time_point: int):
    filename = f"{well_name}{field_name}p{plane:02d}-ch{channel}sk{time_point}fk1fl1.tiff"
    return os.path.join(dir_path, filename)


def build_image_filename(dir_path: str, well_name: str, field_name: str, plane: int, channel: int):
    filename = f"{well_name}\{well_name}{field_name}p{plane:02d}-ch{channel:02d}t01.tiff"
    return os.path.join(dir_path, filename)


class FilePathHandler:
    def __init__(self, config_file):
        self.
class FileManagement:
    def __init__(self):
        pass