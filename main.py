import datetime
import os
import fnmatch
import re
import timeit
import tifffile
import numpy as np
from ConfigReader import ConfigReader


def generate_well_names(dir_path: str):
    pattern = 'r(\d+)c(\d+)'

    file_names = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

    unique_matched_wells = set()

    for file_name in file_names:
        # Use re.search to find the first match
        match = re.search(pattern, file_name)
        if match:
            matched_wells = match.group()
            unique_matched_wells.add(matched_wells)

    return sorted(unique_matched_wells)


def create_dir(save_path):
    if not os.path.exists(save_path):
        os.mkdir(save_path)


def build_image_filename(dir_path: str, well_name: str, field_name: str, plane: int, channel: int, time_point: int):
    return f'{dir_path}/{well_name}{field_name}p{plane:02d}-ch{channel}sk{time_point}fk1fl1.tiff'


def file_exists(file_name: str):
    return os.path.isfile(file_name)


def read_image(file_name: str):
    return tifffile.imread(file_name)


def get_timelapse_images(dir_path: str, well_name: str, field_name: str, planes: int, channels: int, timepoints: int):
    images = []

    for channel in range(1, channels + 1):
        for time_point in range(1, timepoints + 1):
            for plane in range(1, planes + 1):
                file_name = build_image_filename(dir_path, well_name, field_name, plane, channel, time_point)
                if file_exists(file_name):
                    images.append(read_image(file_name))
                else:
                    print(f'{file_name} does not exist')

    return np.array(images)


def process_well(well_name, load_path, save_path, number_of_fields, number_of_planes, number_of_channels,
                 number_of_timepoints, convert_8bit):
    print(f"Processing {well_name} - {datetime.datetime.now()}")

    for field in range(1, number_of_fields + 1):
        field_name = f'f{field:02d}'
        print(f"Processing {field_name} - {datetime.datetime.now()}")

        try:
            timelapse = get_timelapse_images(load_path, well_name, field_name, number_of_planes,
                                                             number_of_channels, number_of_timepoints)

            image_size_x = timelapse.shape[-1]
            image_size_y = timelapse.shape[-2]

            if convert_8bit:
                timelapse = convert_to_8bit(timelapse)
            # Reshape the array if there are multiple fields
            if number_of_fields > 1:
                timelapse = np.reshape(timelapse, (number_of_timepoints * number_of_channels,
                                                   number_of_planes, image_size_y, image_size_x)).max(axis=1)

            save_name = f'{well_name}{field_name}_timelapse.tiff'
            tifffile.imwrite(f'{save_path}/{save_name}',
                             np.swapaxes(np.reshape(timelapse, (
                             number_of_channels, number_of_timepoints, image_size_y, image_size_x)),
                                         0, 1),
                             imagej=True,
                             metadata={'axes': 'TCYX'})

            print(f"Finished {field_name} - {datetime.datetime.now()}")
        except FileNotFoundError as e:
            print(f"Error processing {field_name}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing {field_name}: {e}")

    print(f"Finished {well_name} - {datetime.datetime.now()}")


def find_files(filename: list, dir_pathname: str):
    found_files = [file for file in os.listdir(dir_pathname) if fnmatch.fnmatch(file, filename+'*.*')]
    return found_files


def convert_to_8bit(images):
    image_8bit = []
    for image in images:
        image_8bit.append(np.uint8((image/np.max(image)) * 255))
    return np.array(image_8bit)


def main():
    params = ConfigReader("config.json").get_config()

    # define parameters
    load_path = params["load_directory"]
    save_path = params["save_directory"]

    convert_8bit = params["convert_to_8bit"]

    number_of_timepoints = params["number_of_timepoints"]
    number_of_channels = params["number_of_channels"]
    number_of_planes = params["number_of_planes"]
    number_of_fields = params["number_of_fields"]

    create_dir(save_path)
    start = timeit.default_timer()

    well_names = generate_well_names(load_path)
    start_time = timeit.default_timer()

    for well_name in well_names:
        process_well(well_name, load_path, save_path, number_of_fields, number_of_planes, number_of_channels,
                     number_of_timepoints, convert_8bit)

    final_time = timeit.default_timer()
    print(f"All images took {final_time-start_time:.2f}s to merge")


if __name__ == "__main__":
    main()











