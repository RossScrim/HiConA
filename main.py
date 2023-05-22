import datetime
import os
import fnmatch
import timeit
import tifffile
import numpy as np
from ConfigReader import ConfigReader


def generate_well_names(row_start: int, row_end: int,
                        col_start: int, col_end: int):
    name = []
    for r in range(row_start, row_end+1):
        row = 'r' + "%02d" % r
        for c in range(col_start, col_end+1):
            col = 'c' + "%02d" % c
            name.append(row+col)
    return name


def create_dir(save_path):
    if not os.path.exists(save_path):
        os.mkdir(save_path)


def get_timelapse_images(dir_path:str, well_name: str, field_name: str, planes: int, channels: int, timepoints: int):
    images = []
    for channel in range(1, channels + 1):
        channel_name = 'ch' + str(channel)
        for time_point in range(1, timepoints + 1):
            time_name = 'sk' + str(time_point)
            for plane in range(1, planes + 1):
                plane_name = 'p' + "%02d" % plane
                file_name = dir_path + '\\' + well_name + field_name + plane_name + '-' + channel_name + time_name + 'fk1fl1' + '.tiff'
                if os.path.isfile(file_name):
                    images.append(tifffile.imread(file_name))
                else:
                    print(file_name + " does not exist")
    return np.array(images)


def find_files(filename: list, dir_pathname: str):
    found_files = [file for file in os.listdir(dir_pathname) if fnmatch.fnmatch(file, filename+'*.*')]
    return found_files


def convert_to_8bit(images):
    image_8bit = []
    for image in images:
        image_8bit.append(np.uint8((image/np.max(image)) * 255))
    return np.array(image_8bit)


if __name__ == "__main__":
    params = ConfigReader("config.json").get_config()

    # define parameters
    load_path = params["load_directory"]
    save_path = params["save_directory"]

    row_min = params["row_min"]
    row_max = params["row_max"]
    col_min = params["col_min"]
    col_max = params["col_max"]

    image_size_x = params["image_x"]
    image_size_y = params["image_y"]
    number_of_timepoints = params["number_of_timepoints"]
    number_of_channels = params["number_of_channels"]
    number_of_planes = params["number_of_planes"]
    number_of_fields = params["number_of_fields"]

    create_dir(save_path)
    start = timeit.default_timer()

    well_names = generate_well_names(row_min, row_max, col_min, col_max)
    for well_name in well_names:
        well_file = find_files(well_name, load_path)
        print(f"processing {well_name} - ", datetime.datetime.now())

        for field in range(1, number_of_fields + 1):
            field_name = 'f' + "%02d" % field
            print(f"processing {field_name} - ", datetime.datetime.now())
            timelapse_images = convert_to_8bit(get_timelapse_images(load_path, well_name, field_name, number_of_planes,
                                     number_of_channels, number_of_timepoints))
            timeimages = np.reshape(timelapse_images, (number_of_timepoints*number_of_channels,
                                                       number_of_planes, image_size_y, image_size_x)).max(axis=1),
            save_name = well_name + field_name + '_MAX_Projection-timelapse.tiff'
            tifffile.imwrite(save_path + '\\' + save_name,
                             np.swapaxes(np.reshape(timeimages, (number_of_channels, number_of_timepoints, image_size_y, image_size_x)),
                                         0, 1),
                             imagej=True,
                             metadata={'axes': 'TCYX'})
            print(f"Finished {field_name} - ", datetime.datetime.now())

        print(f"Finished {well_name} - ", datetime.datetime.now())
        final_time = timeit.default_timer()
    print(f"All images took {final_time}s to merge")














