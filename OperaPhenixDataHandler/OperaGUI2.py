import tifffile
import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
from tkinter import messagebox
from tkinter.filedialog import askdirectory
import re
import os

from ConfigReader import OperaExperimentConfigReader
from FileManagement import FilePathHandler
from ImageProcessing import ImageProcessor
from StitchingImageJ import StitchProcessing

class OperaGUI:
    """GUI, getting input from user to run Opera processing."""
    def __init__(self):
        self.src_window()

        self.process_window()

    def src_window(self):
        self.root = tk.Tk()

        #self.root.geometry("800x150")
        self.root.title("Opera Phenix Image Processing")

         # Choose directories
        self.directoryframe = tk.Frame(self.root)
        self.directoryframe.columnconfigure(0, weight=1)
        self.directoryframe.columnconfigure(1, weight=1)
        self.directoryframe.columnconfigure(2, weight=1)

        self.src_label = ttk.Label(self.directoryframe, text="Source directory", font=("Segoe UI", 14))
        self.src_label.grid(row=0, column=0, padx=10, pady=10)

        self.src_entry_text = tk.StringVar()
        self.src_selected = ttk.Entry(self.directoryframe, text=self.src_entry_text, width=70, state='readonly')
        self.src_selected.grid(row=0, column=1, padx=10, pady=10)

        self.src_button = ttk.Button(self.directoryframe, text="...", command=lambda: self.get_directory("src_button"))
        self.src_button.grid(row=0, column=2, padx=10, pady=10)

        self.save_label = ttk.Label(self.directoryframe, text="Saving directory", font=("Segoe UI", 14))
        self.save_label.grid(row=1, column=0, padx=10, pady=10)

        self.save_entry_text = tk.StringVar()
        self.save_selected = ttk.Entry(self.directoryframe, text=self.save_entry_text, width=70, state='readonly')
        self.save_selected.grid(row=1, column=1, padx=10, pady=10)

        self.save_button = ttk.Button(self.directoryframe, text="...", command=lambda: self.get_directory("save_button"))
        self.save_button.grid(row=1, column=2, padx=10, pady=10)

        self.directoryframe.pack()

        # Confirm button
        self.buttonframe = tk.Frame(self.root)
        self.buttonframe.columnconfigure(0, weight=1)

        self.confirm_button = ttk.Button(self.buttonframe, text="OK", command=self.src_confirm)
        self.confirm_button.grid(row=0, column=0, padx=58, pady=10, sticky=tk.E)
        
        self.buttonframe.pack(fill='x')

        self.root.mainloop()

    def process_window(self):
        self.root = tk.Tk()

        #self.root.geometry("800x800")
        self.root.title("Processing Selection")

        ttk.Label(self.root, text='Measurements', font=("Segoe UI", 14)).grid(column=0, row=0, padx=20, pady=0)
        ttk.Label(self.root, text='2D Processing Options', font=("Segoe UI", 14)).grid(column=1, row=0, padx=20, pady=0)
        #ttk.Label(self.root, text='3D Processing Options', font=("Segoe UI", 14)).grid(column=2, row=0, padx=20, pady=0)

        # Display the available measurements
        measure_frame = tk.Frame(self.root)
        measure_frame.grid(column=0, row=1, padx=5, sticky=tk.N)

        self.measure_var_list = []

        for index, measure in enumerate(self.measurement_dict.keys()):
            self.measure_var_list.append(tk.IntVar(value=0))
            ttk.Checkbutton(measure_frame, variable=self.measure_var_list[index],
                text=measure).pack(fill='x')
            
        # Display 2D processing options
        option_frame = tk.Frame(self.root)
        option_frame.grid(column=1, row=1, padx=5, sticky=tk.N)

        self.bit8_state = tk.IntVar()
        self.timelapse_state = tk.IntVar()
        self.maxproj_state = tk.IntVar()
        self.minproj_state = tk.IntVar()
        self.edfproj_state = tk.IntVar()
        self.stitching_state = tk.IntVar()

        #TODO Names of keys should match ImageProcessing functions?
        self.processing_options = {"convert_to_8bit": self.bit8_state, "timelapse_data": self.timelapse_state, "max_projection": self.maxproj_state,"min_projection":self.minproj_state, "EDF_projection":self.edfproj_state, "stitching": self.stitching_state} # Add processing variable states to this list

        self.bit8_check = ttk.Checkbutton(option_frame, text="Convert to 8-bit", variable=self.bit8_state).pack(fill='x')

        self.timelapse_check = ttk.Checkbutton(option_frame, text="Timelapse Data", variable=self.timelapse_state).pack(fill='x')

        self.maxproj_check = ttk.Checkbutton(option_frame, text="Perform maximum projection", variable=self.maxproj_state).pack(fill='x')

        self.minproj_check = ttk.Checkbutton(option_frame, text="Perform minimum projection", variable=self.minproj_state).pack(fill='x')

        self.edfproj_check = ttk.Checkbutton(option_frame, text="Perform EDF projection (BF)", variable=self.edfproj_state).pack(fill='x')

        self.stitching_check = ttk.Checkbutton(option_frame, text="Stitch images", variable=self.stitching_state).pack(fill='x')
        
        #Add 3D options here
        """
        # Display 3D processing options
        option_3D_frame = tk.Frame(self.root)
        option_3D_frame.grid(column=2, row=1, padx=5, sticky=tk.N)

        self.option1_state = tk.IntVar()
        self.option2_state = tk.IntVar()

        self.option1_check = ttk.Checkbutton(option_3D_frame, text="Option1", variable=self.option1_state).pack(fill='x')

        self.option2_check = ttk.Checkbutton(option_3D_frame, text="Option2", variable=self.option2_state).pack(fill='x')
        """
        # Confirm button
        self.buttonframe = tk.Frame(self.root)
        self.buttonframe.grid(column=2, row=2)

        self.confirm_button = ttk.Button(self.buttonframe, text="OK", command=self.proc_confirm)
        self.confirm_button.grid(row=0, column=0, padx=5, pady=10, sticky=tk.E)

        self.root.mainloop()

    
    def get_directory(self, button):
        """Asks users to choose the source and saving directories."""
        if button == "src_button":
            src_dir = askdirectory(title="Choose directory for images to be processed")
            self.src_entry_text.set(src_dir)
        if button == "save_button":
            save_dir = askdirectory(title="Choose saving directory for processed images")
            self.save_entry_text.set(save_dir)

    def src_confirm(self):
        """Checks the choices have been made for directories and processing steps. """
        if self.src_entry_text.get() == "" or not self.src_entry_text.get().endswith("hs"):
            messagebox.showinfo(title="Missing Information", message="Please choose the hs source directory")
        elif self.save_entry_text.get() == "":
            messagebox.showinfo(title="Missing Information", message="Please choose saving directory")
        elif self.src_entry_text.get() == self.save_entry_text.get():
            messagebox.showinfo(title="Missing Information", message="Please choose a different saving directory from your source directory")
        else:
            self.src_dir = self.src_entry_text.get()
            self.save_dir = self.save_entry_text.get()
            self.root.destroy()

            self.src_processing()

    def src_processing(self):
        self.measurement_dict = {}
        for measurement in [f for f in os.listdir(self.src_dir) if (os.path.isdir(os.path.join(self.src_dir, f)) and f != "_configdata")]:
            measurement_path = os.path.join(self.src_dir, measurement)

            files = self.get_file_paths(measurement_path)
            opera_config_file = self.get_metadata(files.archived_data_config)

            plate_name = opera_config_file["PLATENAME"]
            measure_num = opera_config_file["MEASUREMENT"].split(" ")
            guid = opera_config_file["GUID"]
            
            name = plate_name + " - " + measure_num[-1]
            self.measurement_dict[name] = guid 
        
        self.measurement_dict = dict(sorted(self.measurement_dict.items()))
        #print(self.measurement_dict.keys())

    def get_metadata(self, config_path: str):
        """Call FileManagement class to get metadata for images. Returns opera_config_file."""
        kw_file = config_path
        #print(kw_file)
        opera_config = OperaExperimentConfigReader(kw_file)
        return opera_config.load_json_from_txt(remove_first_lines=1, remove_last_lines=2)

    def get_file_paths(self, src_dir: str):
        """Call ConfigReader to get file paths for all wells."""
        archived_data_path = src_dir
        return FilePathHandler(archived_data_path) 
    
    def proc_confirm(self):
        if all(x.get() == 0 for x in self.measure_var_list):
            messagebox.showinfo(title="Missing Information", message="Please select a measurement to analyse")
        elif all(x.get() == 0 for x in self.processing_options.values()):
            messagebox.showinfo(title="Missing Information", message="Please select a 2D processing option")
        #No 3D options added yet - add here when needed
        else:
            #TODO Is there a nicer way to create the measure_to_process list? 
            self.measure_to_process = [self.measurement_dict[list(self.measurement_dict.keys())[i]] for i in range(len(self.measurement_dict)) if self.measure_var_list[i].get() == 1]
            self.measure_to_process_plate_name = [list(self.measurement_dict.keys())[list(self.measurement_dict.values()).index(v)] for v in self.measure_to_process]
            self.processes_to_run = {k:v.get() for k, v in self.processing_options.items()}
            self.root.destroy()
            for cur_ind in range(len(self.measure_to_process)):
                cur_measurement = self.measure_to_process[cur_ind]
                cur_plate_name = self.measure_to_process_plate_name[cur_ind]

                cur_files = FilePathHandler(os.path.join(self.src_dir, cur_measurement))
                cur_save_dir = os.path.join(self.save_dir, cur_plate_name)
                if not os.path.exists(cur_save_dir):
                    os.makedirs(cur_save_dir)
                OperaProcessing(cur_files, self.processes_to_run, cur_save_dir)




class OperaProcessing():
    """Performs the specified processing steps on the measurements selected from the GUI."""
    def __init__(self, files, processes_to_run, save_dir):

        self.files = files
        self.save_path = r"C:\Users\ewestlund\OneDrive - The Institute of Cancer Research\Desktop"
        self.save_dir = save_dir
        self.processes_to_run = processes_to_run # Dict with keys = process function name, and values = 0 or 1, indicating chosen processes
        self.config_file = OperaExperimentConfigReader(self.files.archived_data_config).load_json_from_txt(remove_first_lines=1, remove_last_lines=2)
        self.FOVs = self.config_file["FIELDS"]
        self.channels = len(self.config_file["CHANNEL"])
        self.planes = self.config_file["PLANES"]

        self.run()
        #TODO Loop through each measurement in measure_to_process.
        # Everything from the measurement is in src_path + measurement - get kw.txt for metadata and location for wells.
        # Loop through each FOV in each well and send to ImageProcessing.py

    def load_images(self, filepaths):
        im_arr = []
        for filepath in filepaths:
            im_arr.append(tifffile.imread(filepath))
            #print(im_arr)
            if len(im_arr) == 1:
                self.xy = len(im_arr[0])
        
        im_arr = np.array(im_arr)
        return im_arr

    
    def run(self):
        for cur_well in self.files.well_names[:8]:
            cur_save = os.path.join(self.save_dir, cur_well)
            self.files.create_dir(cur_save)
            
            for cur_FOV in range(1, self.FOVs+1):
                FOV_rename_order = ["05", "01", "04", "07", "08", "02", "03", "06", "09"]
                pattern = fr"r\d+c\d+f0?{cur_FOV}p\d+-ch\d+t\d+.tiff"
                cur_image_name = self.files.get_opera_phenix_images_from_FOV(cur_well, pattern)
                images = self.load_images(cur_image_name)
    
                try:
                    images = np.reshape(images, [self.planes, self.channels, self.xy, self.xy])
                    processor = ImageProcessor(images, self.config_file)
                    processor.process(max_proj=self.processes_to_run["max_projection"], to_8bit=self.processes_to_run["convert_to_8bit"], min_proj=self.processes_to_run["min_projection"], edf_proj=self.processes_to_run["EDF_projection"])
                    tifffile.imwrite(cur_save+"/"+cur_well+"f"+FOV_rename_order[cur_FOV-1]+".tif", processor.get_image(), imagej=True, metadata={'axes':'CYX'})

                    for ch in range(self.channels):
                        ch_save_path = os.path.join(cur_save, "ch"+str(ch+1))
                        if not os.path.exists(ch_save_path):
                            os.makedirs(ch_save_path)
                        tifffile.imwrite(ch_save_path+"/"+cur_well+"f"+FOV_rename_order[cur_FOV-1]+".tif", processor.get_image()[ch,:,:], imagej=True, metadata={'axes':'YX'})
                    
                except ValueError as e:
                    print("Error processing well " + cur_well + " field " + str(cur_FOV) + " with ValueError.")
                    continue
                
            try:
                if self.processes_to_run["EDF_projection"] == 1:     
                    StitchProcessing(cur_save)
            
            except ValueError as e:
                print("Error stitching well " + cur_well + " with ValueError.")
                continue
            

        print("Done!")        
        
if __name__ == "__main__":
    OperaGUI()