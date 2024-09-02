import os
import re


class FilePathHandler:
    def __init__(self, archived_data_path: str):
        self.archived_data_path = archived_data_path + "\\"
        self.archived_data_config = os.path.join(self.archived_data_path,
                                                 self.get_name_from_regexstring(self.archived_data_path, ".*\.kw\.txt")[0])
        self.archived_image_path = self.archived_data_path + "\\images"
        self.well_names = self.get_name_from_regexstring(self.archived_image_path, 'r(\d+)c(\d+)')

    def get_name_from_regexstring(self, dir_path: str, str_pattern: str):
        matched_string = [match.group() for file_name in os.listdir(dir_path) if
                                 (match := re.search(str_pattern, file_name))]
        return matched_string

    # DO we need the below function in class or should we grab the images to process when needed
    def get_opera_phenix_images_from_FOV(self, well_name: str, pattern):
        well_path = os.path.join(self.archived_image_path, well_name)
        image_files = self.get_name_from_regexstring(well_path, pattern)
        return image_files

    def create_dir(save_path):
        if not os.path.exists(save_path):
        os.makedirs(save_path)


if __name__ == "__main__":
    archived_data_path = r"X:\Ross\20241705_RPE1P53KO_siMMR_live-cell\hs\88651da0-9ab0-4728-816f-15417fe0fa61"
    files = FilePathHandler(archived_data_path)


    field_of_view = 4
    for field in range(0, field_of_view):
        pattern = f"r\d+c\d+f0{field}p\d+-ch\d+t\d+.tiff"
        print(pattern)
        print(files.get_opera_phenix_images_from_FOV(files.well_names[0], pattern))
        ## do some processing

    print(files.archived_data_path)
    print(files.archived_data_config)
    print(files.well_names)