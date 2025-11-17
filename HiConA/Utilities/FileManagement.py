import os
import re


class FilePathHandler:
    def __init__(self, archived_data_path: str):
        self.archived_data_path = archived_data_path + "\\"
        self.archived_data_config = os.path.join(self.archived_data_path,
                                                 self._get_name_from_regexstring(
                                                     self.archived_data_path, r'.*\.kw\.txt')[0])
        self.archived_image_path = self.archived_data_path + "images"
        self.well_names = self._get_name_from_regexstring(self.archived_image_path, r'r(\d+)c(\d+)')

    def _get_name_from_regexstring(self, dir_path: str, str_pattern: str):
        matched_strings = []
        for file_name in sorted(os.listdir(dir_path)):
            match = re.search(str_pattern, file_name)
            if match:
                matched_strings.append(match.group())
        return matched_strings

    # DO we need the below function in class or should we grab the images to process when needed
    def get_opera_phenix_images_from_FOV(self, well_name: str, pattern):
        well_path = os.path.join(self.archived_image_path, well_name)
        image_files = self._get_name_from_regexstring(well_path, pattern)
        return [os.path.join(well_path, file) for file in image_files]

    def create_dir(self, save_path):
        return os.makedirs(save_path, exist_ok=True)

    def get_file_path(self, well_name):
        return os.path.join(self.archived_image_path, well_name)


if __name__ == "__main__":
    archived_data_path = r"X:\DSR\CONFOFAC\GLIOTEAM-OPERA\vmolinari\hs\d3d31154-c106-4002-a94c-82d30ba740e3"
    files = FilePathHandler(archived_data_path)

    field_of_view = 2
    for field in range(0, field_of_view):
        pattern = fr"r\d+c\d+f0{field}p\d+-ch\d+t\d+.tiff"
        print(pattern)
        print(files.get_opera_phenix_images_from_FOV(files.well_names[0], pattern))
        ## do some processing

    #print(files.archived_data_path)
    #print(files.archived_data_config)
    #print(files.well_names)