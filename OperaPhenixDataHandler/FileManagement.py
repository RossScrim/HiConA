import os
import re
import ConfigReader


def create_dir(save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)


class FilePathCreator:
    def __init__(self, archived_data_path: str):
        self.archived_data_path = archived_data_path

        self.archived_image_path = self.archived_data_path + "\\images" # maybe shhold be a function rather than creating muliple paths that are useless
        self.well_names = self.get_well_names(self.archived_image_path)

        if not self.config_file["timelapse"]:
            self.timelapse_image_paths = self.build_timelapse_image_filename()

        else:
            self.image_paths =  self.build_image_filename()

    def get_well_names(self, dir_path: str):
        pattern = 'r(\d+)c(\d+)'
        unique_matched_wells = {match.group() for file_name in os.listdir(dir_path) if
                                (match := re.search(pattern, file_name))}
        return sorted(unique_matched_wells)

    def build_timelapse_image_filename(self, dir_path: str, well_names: list, field_name: str, planes: int, channels: int,
                                       timepoints: int):
        image_paths = []
        for well_name in well_names:
            well_path = os.path.join(dir_path, well_name)
            for channel in range(1, channels + 1):
                for time_point in range(1, timepoints + 1):
                    for plane in range(1, planes + 1):
                        filename = f"{well_name}{field_name}p{plane:02d}-ch{channel:02d}t{time_point:02d}.tiff"
                        image_path = os.path.join(well_path, filename)
                        if os.path.isfile(image_path):
                            image_paths.append(filename)
                        else:
                            print(f'{filename} does not exist')
        return image_paths

    def build_image_filename(self, dir_path: str, well_names: list, field_name: str, planes: int, channels: int):
        image_paths = []
        for well_name in well_names:
            well_path = os.path.join(dir_path, well_name)
            for channel in range(1, channels + 1):
                for plane in range(1, planes + 1):
                    filename = f"{well_name}{field_name}p{plane:02d}-ch{channel:02d}t01.tiff"
                    image_path = os.path.join(dir_path,filename)
                    if os.path.isfile(image_path):
                        image_paths.append(filename)
                    else:
                        print(f'{filename} does not exist')
        return image_paths


if __name__ == "__main__":
    config = ConfigReader.ConfigReader("../config.json")
    config_file = config.get_config()
    print(FilePathCreator(config_file).well_paths)
