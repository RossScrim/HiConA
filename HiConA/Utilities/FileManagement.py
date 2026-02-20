import os
import re


class FilePathHandler:
    def __init__(self, archived_data_path: str):
        self.archived_data_path = archived_data_path + "\\"
        self.archived_image_path = os.path.join(self.archived_data_path, "images")
        self.archived_data_config_xml = None
        self.archived_data_config = None
        self.well_names = []

        if not os.path.exists(self.archived_data_path):
            return

        self.xml_file_match = self._get_name_from_regexstring(archived_data_path, r".*\.xml")
        if self.xml_file_match:
            self.archived_data_config_xml = os.path.join(self.archived_data_path,self.xml_file_match[0])

        self.kw_file_match = self._get_name_from_regexstring(archived_data_path,r".*\.kw\.txt")
        if self.kw_file_match:
            self.archived_data_config = os.path.join(archived_data_path, self.kw_file_match[0])

        self.well_names = self._get_name_from_regexstring(self.archived_image_path, r'r(\d+)c(\d+)')

    def is_valid(self):
        # If the config file is missing, we can't interpret the images
        if self.archived_data_config_xml is None:
            return False
        if self.archived_data_config is None:
            return False
        # If the image folder is missing, there's nothing to process
        if not os.path.exists(self.archived_image_path):
            return False
        return True

    def _get_name_from_regexstring(self, dir_path: str, str_pattern: str):
        matched_strings = []
        macos_metadata_files = "._"

        for file_name in sorted(os.listdir(dir_path)):
            if file_name.startswith(macos_metadata_files):
                continue
            match = re.search(str_pattern, file_name)
            if match:
                matched_strings.append(match.group())

        return matched_strings

    # DO we need the below function in class or should we grab the images to process when needed
    def get_opera_phenix_images_from_FOV(self, well_name: str, pattern):
        well_path = os.path.join(self.archived_image_path, well_name)
        image_files = self._get_name_from_regexstring(well_path, pattern)
        return [os.path.join(well_path, file) for file in image_files]

    def build_imagename_pattern(self, FOV, timepoint=None):
        pattern = "r(\\d+)c(\\d+)f(0?)" + str(FOV) + "p(\\d+)-(ch(\\d+))"
        if timepoint is not None:
            pattern += f"t0?{timepoint}"
        else:
            pattern += "t0?1"
        pattern += ".tiff"
        return pattern

    def create_dir(self, save_path):
        return os.makedirs(save_path, exist_ok=True)

    def get_file_path(self, well_name):
        return os.path.join(self.archived_image_path, well_name)

    def get_well_fov_list(self, well_name):
        well_path = self.get_file_path(well_name)
        image_names = os.listdir(well_path)
        fovs = set()
        # This pattern says: "Find 'f', then capture all digits that follow it"
        # It stops as soon as it hits a non-digit (like 'p', 'c', or '_')
        fov_pattern = re.compile(r'f(\d+)')
        for f in image_names:
            if f.endswith(".db"):
                continue
            match = fov_pattern.search(f)
            if match:
                # .group(1) is JUST the numbers (e.g., '01')
                fovs.add(int(match.group(1)))
        return sorted(list(fovs))

if __name__ == "__main__":
    archived_data_path = r"Y:\Emma\Opera Phenix Test Data\hs\4e88424a-8346-4ec4-8142-cecbf124b857"
    files = FilePathHandler(archived_data_path)
    for well in files.well_names:
        print(files.get_well_fov_list(well))

        ## do some processing

    #print(files.archived_data_path)
    #print(files.archived_data_config)
    #print(files.well_names)