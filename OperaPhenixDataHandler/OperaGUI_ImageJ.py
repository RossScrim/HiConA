import tifffile
import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
from tkinter import messagebox, Scrollbar, Canvas
from tkinter.filedialog import askdirectory, askopenfilename
import re
import os
import pickle
import json

from .ConfigReader import OperaExperimentConfigReader
from .FileManagement import FilePathHandler
from .ImageProcessing import ImageProcessor
from .StitchingImageJ import StitchProcessing
from .CellposeSegmentation import cellpose_organiser
from .ImageJAfterStitching import ImageJProcessor

class OperaGUI:
    """GUI, getting input from user to run Opera processing."""
    def __init__(self):
        self.cur_py_dir = os.path.dirname(__file__)
        self.save_variables_file = os.path.join(self.cur_py_dir, "saved_variables.json")
        if os.path.isfile(self.save_variables_file):
            with open(self.save_variables_file, "r+") as f:
                self.saved_var = json.load(f)

        self.src_window()

        self.process_window()

    def src_window(self):
        self.root = tk.Tk()

        #self.root.geometry("800x150")
        self.root.title("Opera Phenix Image Processing")

         # Choose directories
        self.directoryframe = tk.Frame(self.root)
        #self.directoryframe.columnconfigure(0, weight=1)
        #self.directoryframe.columnconfigure(1, weight=1)
        #self.directoryframe.columnconfigure(2, weight=1)

        self.src_label = ttk.Label(self.directoryframe, text="Source directory", font=("Segoe UI", 14))
        self.src_label.grid(row=0, column=0, padx=10, pady=10)

        self.src_entry_text = tk.StringVar()
        try:
            self.src_entry_text.set(self.saved_var["src_entry_text"])
        except:
            pass
        self.src_selected = ttk.Entry(self.directoryframe, text=self.src_entry_text, width=70, state='readonly')
        self.src_selected.grid(row=0, column=1, padx=10, pady=10)

        self.src_button = ttk.Button(self.directoryframe, text="...", command=lambda: self.get_directory("src_button"))
        self.src_button.grid(row=0, column=2, padx=10, pady=10)

        self.save_label = ttk.Label(self.directoryframe, text="Saving directory", font=("Segoe UI", 14))
        self.save_label.grid(row=1, column=0, padx=10, pady=10)

        self.save_entry_text = tk.StringVar()
        try:
            self.save_entry_text.set(self.saved_var["save_entry_text"])
        except:
            pass
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

        self.root.geometry("800x800")
        self.root.title("Processing Selection")

        ttk.Label(self.root, text='Measurements', font=("Segoe UI", 14)).grid(column=0, row=0, padx=20, pady=0)
        ttk.Label(self.root, text='2D Processing Options', font=("Segoe UI", 14)).grid(column=1, row=0, padx=70, pady=0, sticky=tk.W)
        #self.imageJ_Label = ttk.Label(self.root, text='ImageJ Options', font=("Segoe UI", 14))
        #ttk.Label(self.root, text='3D Processing Options', font=("Segoe UI", 14)).grid(column=2, row=0, padx=20, pady=0)

        # Display the available measurements
        measure_frame = tk.Frame(self.root, height=800)
        measure_frame.grid(column=0, row=1, padx=5, sticky=tk.N)
        self.canvas = Canvas(measure_frame)
        int_measure_frame = tk.Frame(self.canvas)
        scrollbar = Scrollbar(measure_frame, orient ="vertical", command = self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left")
        self.canvas.create_window((0,0), window=int_measure_frame, anchor=tk.NW)
        int_measure_frame.bind("<Configure>", self.configurefunction)

        self.measure_var_list = []

        for index, measure in enumerate(self.measurement_dict.keys()):
            self.measure_var_list.append(tk.IntVar(value=0))
            ttk.Checkbutton(int_measure_frame, variable=self.measure_var_list[index],
                text=measure).pack(fill='x')
            

        # Display 2D processing options
        option_frame = tk.Frame(self.root, width=500)
        option_frame.grid(column=1, row=1, padx=5, sticky=tk.NW)
        option_frame.propagate(0)

        self.bit8_state = tk.IntVar()
        #self.timelapse_state = tk.IntVar()
        self.maxproj_state = tk.IntVar()
        self.minproj_state = tk.IntVar()
        self.edfproj_state = tk.IntVar()
        self.separate_ch_state = tk.IntVar()
        self.stitching_state = tk.IntVar()
        self.cellpose_state = tk.IntVar()
        self.imagej_state = tk.IntVar()

        #TODO Names of keys should match ImageProcessing functions?
        self.processing_options = {"convert_to_8bit": self.bit8_state, 
                                   "max_projection": self.maxproj_state,
                                   "min_projection":self.minproj_state, 
                                   "EDF_projection":self.edfproj_state,
                                   "separate_ch":self.separate_ch_state,
                                   "stitching": self.stitching_state, 
                                   "cellpose": self.cellpose_state,
                                   "ImageJ": self.imagej_state} # Add processing variable states to this list

        self.bit8_check = ttk.Checkbutton(option_frame, text="Convert to 8-bit", 
                                          variable=self.bit8_state).grid(row=0, column=0, sticky=tk.W)

        #self.timelapse_check = ttk.Checkbutton(option_frame, text="Timelapse Data", variable=self.timelapse_state).pack(fill='x')

        self.maxproj_check = ttk.Checkbutton(option_frame, text="Perform maximum projection", 
                                             variable=self.maxproj_state).grid(row=1, column=0, sticky=tk.W)

        self.minproj_check = ttk.Checkbutton(option_frame, text="Perform minimum projection", 
                                             variable=self.minproj_state).grid(row=2, column=0, sticky=tk.W)

        self.edfproj_check = ttk.Checkbutton(option_frame, text="Perform EDF projection on BF channel", 
                                             variable=self.edfproj_state, command=self.show_imagej_frame).grid(row=3, column=0, sticky=tk.W)
        self.edfproj_BFch_var = tk.IntVar()
        try:
            self.edfproj_BFch_var.set(self.saved_var["BF_channel"])
        except:
            pass
        edfproj_BF_label = ttk.Label(option_frame, text="BF channel number:", width=2).grid(row=4, column=0, sticky=tk.EW, padx=18)
        self.edfproj_BFch_entry = ttk.Entry(option_frame, text=self.edfproj_BFch_var, width=2, background='White').grid(row=4, column=0, sticky=tk.W, padx=135)

        self.separate_ch_check = ttk.Checkbutton(option_frame, text="Separate image channels",
                                                 variable=self.separate_ch_state).grid(row=5, column=0, sticky=tk.W)

        self.stitching_check = ttk.Checkbutton(option_frame, text="Stitch images (width x height)", 
                                               variable=self.stitching_state).grid(row=6, column=0, sticky=tk.W)
        self.stitching_var_width = tk.IntVar()
        self.stitching_var_height = tk.IntVar()
        try:
            self.stitching_var_width.set(self.saved_var["stitch_width"])
            self.stitching_var_height.set(self.saved_var["stitch_height"])
        except:
            pass
        self.stitching_entry = ttk.Entry(option_frame, text=self.stitching_var_width, width=2, background='White').grid(row=7, column=0, sticky=tk.W, padx=20)
        stitching_label = ttk.Label(option_frame, text="x").grid(row=7, column=0, sticky=tk.W, padx=40)
        self.stitching_entry = ttk.Entry(option_frame, text=self.stitching_var_height, width=2, background='White').grid(row=7, column=0, sticky=tk.W, padx=52)
        self.stitch_ref_var = tk.IntVar()
        try:
            self.stitch_ref_var.set(self.saved_var["stitch_ref_ch"])
        except:
            pass
        stitch_ref_label = ttk.Label(option_frame, text="Stitching ref channel:").grid(row=8, column=0, sticky=tk.W, padx=18)
        self.stitch_ref_entry = ttk.Entry(option_frame, text=self.stitch_ref_var, width=2, background="White").grid(row=8, column=0, padx=135, sticky=tk.W)
        
        self.cellpose_check = ttk.Checkbutton(option_frame, text="Perform cellpose segmentation", 
                                              variable=self.cellpose_state).grid(row=9, column=0, sticky=tk.W)

        self.imagej_check = ttk.Checkbutton(option_frame, text="Run ImageJ Macro",
                                            variable=self.imagej_state, command=self.show_imagej_frame).grid(row=10, column=0, sticky=tk.W)
        

        # Frame for imageJ location - only activates when user has ticked on EDF processing or ImageJ Script
        self.imagej_frame = tk.Frame(option_frame, width=550)
        self.macro_selection_frame = tk.Frame(option_frame, width=550)

        ttk.Label(self.imagej_frame, text='ImageJ Options', font=("Segoe UI", 14)).grid(row=0, column=1, padx=0, sticky=tk.NW)
        self.imagej_label = ttk.Label(self.imagej_frame, text="Fiji.app directory    ").grid(row=1, column=0, padx=0, pady=10, sticky=tk.W)

        self.imagej_entry_text = tk.StringVar()
        try:
            self.imagej_entry_text.set(self.saved_var["imagej_loc"])
        except:
            pass
        self.imagej_selected = ttk.Entry(self.imagej_frame, text=self.imagej_entry_text, width=25, state='readonly')
        self.imagej_selected.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.imagej_button = ttk.Button(self.imagej_frame, text="...", command=lambda: self.get_directory("imagej_button"), width=5)
        self.imagej_button.grid(row=1, column=2, padx=0, pady=5, sticky=tk.W)

        # For macro and arguments files selection
        self.interactive_state = tk.IntVar()
        try:
            self.interactive_state.set(self.saved_var["interactive"])
        except:
            pass
        self.interactive_check = ttk.Checkbutton(self.macro_selection_frame, text="Interactive mode", variable=self.interactive_state)
        self.interactive_check.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.macro_label = ttk.Label(self.macro_selection_frame, text="ImageJ macro").grid(row=1, column=0, padx=0, pady=5, sticky=tk.W)

        self.macro_entry_text = tk.StringVar()
        try:
            self.macro_entry_text.set(self.saved_var["macro_file"])
        except:
            pass
        self.macro_selected = ttk.Entry(self.macro_selection_frame, text=self.macro_entry_text, width=25, state='readonly')
        self.macro_selected.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.macro_button = ttk.Button(self.macro_selection_frame, text="...", command=lambda: self.get_directory("macro_button"), width=5)
        self.macro_button.grid(row=1, column=2, padx=0, pady=5, sticky=tk.W)

        self.arg_label = ttk.Label(self.macro_selection_frame, text="ImageJ Arguments").grid(row=2, column=0, padx=0, pady=5, sticky=tk.W)

        self.arg_entry_text = tk.StringVar()
        try:
            self.arg_entry_text.set(self.saved_var["args_file"])
        except:
            pass
        self.arg_selected = ttk.Entry(self.macro_selection_frame, text=self.arg_entry_text, width=25, state='readonly')
        self.arg_selected.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.arg_button = ttk.Button(self.macro_selection_frame, text="...", command=lambda: self.get_directory("arg_button"), width=5)
        self.arg_button.grid(row=2, column=2, padx=0, pady=5, sticky=tk.W)

        self.imagej_process_label = ttk.Label(self.macro_selection_frame, text="Apply macro").grid(row=3, column=0, sticky=tk.W)
        self.imagej_order_text = tk.StringVar()
        try:
            self.imagej_order_text.set(self.saved_var["proc_order"])
        except:
            pass
        self.imagej_combobox = ttk.Combobox(self.macro_selection_frame, textvariable=self.imagej_order_text, state='readonly', values=["to stack", "after MIP/EDF", "after stitching"])
        self.imagej_combobox.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        imagej_information_button = ttk.Button(self.macro_selection_frame, text="Macro/args files guidelines", command=self.display_imagej_info)
        imagej_information_button.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

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
        self.buttonframe.grid(column=2, row=2, sticky=tk.N)

        self.confirm_button = ttk.Button(self.buttonframe, text="OK", command=self.proc_confirm)
        self.confirm_button.grid(row=0, column=0, padx=0, pady=10, sticky=tk.W)

        self.root.mainloop()

    def display_imagej_info(self):
        messagebox.showinfo(title="Guidelines for ImageJ macro and arguments files", message="The macro should be an .ijm and the arguments a .json file.\n\n"
        "The image gets opened by the Opera data handler so start the macro from the first image operation.\n\n"
        "The arguments for the macro should be in a dictionary within the .json file.\n\n"
        "The arguments will be put at the beginning of the macro by the Opera data handler, so there is no need to add the arguments specifics at the top of the macro.\n\n")

    def show_imagej_frame(self):
            edf = self.edfproj_state.get()
            imagej = self.imagej_state.get()

            if edf == 1 or imagej == 1:
                self.imagej_frame.grid(column=0, row=11, sticky=tk.NW)
                if imagej == 1:
                    self.macro_selection_frame.grid(column=0, row=12, sticky=tk.NW)
                else:
                    self.macro_selection_frame.grid_forget()
            else:
                self.imagej_frame.grid_forget()
                self.macro_selection_frame.grid_forget()

    def configurefunction(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=350, height=720)
    
    def get_directory(self, button):
        """Asks users to choose the source and saving directories."""
        if button == "src_button":
            src_dir = askdirectory(title="Choose directory for images to be processed")
            self.src_entry_text.set(src_dir)
        if button == "save_button":
            save_dir = askdirectory(title="Choose saving directory for processed images")
            self.save_entry_text.set(save_dir)
        if button == "imagej_button":
            imagej_dir = askdirectory(title="Choose location for Fiji.app directory")
            self.imagej_entry_text.set(imagej_dir)
        if button == "macro_button":
            macro_file = askopenfilename(title="Choose location for ImageJ macro file")
            self.macro_entry_text.set(macro_file)
        if button == "arg_button":
            arg_file = askopenfilename(title="Choose location for ImageJ arguments file")
            self.arg_entry_text.set(arg_file)

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
        imagej_loc = self.imagej_entry_text.get()
        interactive_mode = self.interactive_state.get()
        imagej_macro = self.macro_entry_text.get()
        imagej_args = self.arg_entry_text.get()
        
        stitch_ref_ch = int(self.stitch_ref_var.get())
        BFchannel = int(self.edfproj_BFch_var.get())
        stitch_width = int(self.stitching_var_width.get())
        stitch_height = int(self.stitching_var_height.get())

        if all(x.get() == 0 for x in self.measure_var_list):
            messagebox.showinfo(title="Missing Information", message="Please select a measurement to analyse")
        elif all(x.get() == 0 for x in self.processing_options.values()):
            messagebox.showinfo(title="Missing Information", message="Please select a 2D processing option")
        #No 3D options added yet - add here when needed
        elif self.edfproj_state.get() == 1 and (not isinstance(BFchannel, int) or BFchannel == 0):
            messagebox.showinfo(title="Missing Information", message="Please provide the BF channel number")
        elif (self.edfproj_state.get() == 1 or self.imagej_state.get() == 1) and imagej_loc == "":
            messagebox.showinfo(title="Missing Information", message="Please choose the location for the Fiji.app directory")
        elif (self.imagej_state.get() == 1) and (imagej_macro == "" or imagej_args == ""):
            messagebox.showinfo(title="Missing Information", message="Please choose the location for the ImageJ macro and arguments files")
        elif self.imagej_state.get() == 1 and imagej_proc_order == "":
            messagebox.showinfo(title="Missing Information", message="Please choose when the macro should be applied in the dropdown menu.")
        elif self.stitching_state.get() == 1 and (not isinstance(stitch_width, int) or stitch_width == 0 or not isinstance(stitch_height, int) or stitch_height == 0):
            messagebox.showinfo(title="Missing Information", message="Please provide the dimensions for the stitched image")
        elif self.stitching_state.get() == 1 and (not isinstance(stitch_ref_ch, int) or stitch_ref_ch == 0):
            messagebox.showinfo(title="Missing Information", message="Please provide the stitching reference channel number")
        else:        
            # Save imagej config file using json
            if self.imagej_state.get() == 1:
                imagej_dict = {"fiji_loc": imagej_loc, "macro_file": imagej_macro, "args_file": imagej_args, "interactive": interactive_mode, "proc_order": imagej_proc_order}
                # Open this file when running ImageJ processor
                self.imagej_config_file = os.path.join(self.cur_py_dir, "imagej_config.json")
                with open(self.imagej_config_file, "w+") as f:
                    json.dump(imagej_dict, f)
                imagej_proc_order = self.imagej_order_text.get()
            else:
                imagej_proc_order = None

            # Save used variables using json for next run
            var_dict = {"src_entry_text": self.src_dir, 
                        "save_entry_text": self.save_dir,
                        "BF_channel": BFchannel,
                        "stitch_ref_ch": stitch_ref_ch,
                        "stitch_width": stitch_width,
                        "stitch_height": stitch_height, 
                        "imagej_loc": imagej_loc, 
                        "macro_file": imagej_macro, 
                        "args_file": imagej_args,
                        "interactive": interactive_mode,
                        "proc_order": imagej_proc_order}
            
            with open(self.save_variables_file, "w+") as f:
                json.dump(var_dict, f)

            self.measure_to_process = [self.measurement_dict[list(self.measurement_dict.keys())[i]] for i in range(len(self.measurement_dict)) if self.measure_var_list[i].get() == 1]
            self.processes_to_run = {k:v.get() for k, v in self.processing_options.items()}
            self.root.destroy()
            
            for cur_measurement in self.measure_to_process:
                cur_plate_name = list(self.measurement_dict.keys())[list(self.measurement_dict.values()).index(cur_measurement)]
                cur_files = FilePathHandler(os.path.join(self.src_dir, cur_measurement))
                
                cur_save_dir = os.path.join(self.save_dir, cur_plate_name)
                if not os.path.exists(cur_save_dir):
                    os.makedirs(cur_save_dir)
                
                OperaProcessing(cur_files,
                                self.processes_to_run,
                                cur_save_dir,
                                BFchannel=BFchannel,
                                stitch_width=stitch_width,
                                stitch_height=stitch_height,
                                stitch_ref_ch=stitch_ref_ch,
                                imagej_loc=imagej_loc,
                                imagej_proc_order=imagej_proc_order)


class OperaProcessing():
    """Performs the specified processing steps on the measurements selected from the GUI."""
    def __init__(self, files, processes_to_run, save_dir, BFchannel, stitch_width, stitch_height, stitch_ref_ch, imagej_loc, imagej_proc_order):

        self.files = files
        self.save_dir = save_dir
        self.processes_to_run = processes_to_run # Dict with keys = process function name, and values = 0 or 1, indicating chosen processes
        self.imagej_loc = imagej_loc
        self.imagej_proc_order = imagej_proc_order
        self.config_file = OperaExperimentConfigReader(
            self.files.archived_data_config).load_json_from_txt(remove_first_lines=1, remove_last_lines=2)
        
        self.FOVs = self.config_file["FIELDS"]
        if type(self.config_file["CHANNEL"]) is list:
            self.channels = len(self.config_file["CHANNEL"])
        else:
            self.channels = 1
        self.planes = self.config_file["PLANES"]
        self.timepoints = self.config_file["TIMEPOINTS"]

        self.BFch = BFchannel
        self.stitch_width = stitch_width
        self.stitch_height = stitch_height
        if stitch_ref_ch == 0:
            self.stitch_ref_ch = BFchannel
        else:
            self.stitch_ref_ch = stitch_ref_ch

        if self.processes_to_run["stitching"] == 1:
            self.FOV_rename_order = self.get_stitching_order()
        else:
            self.FOV_rename_order = ["0"+str(num) for num in range(1, self.FOVs+1)]

        self.is_data_timelapse = self.check_is_data_timelapse()
        self.run()
        
    def check_is_data_timelapse(self):
        if self.timepoints > 1:
            return True
        else:
            return False

    def load_images(self, filepaths):
        im_arr = []
        for filepath in filepaths:
            im_arr.append(tifffile.imread(filepath))
            if len(im_arr) == 1:
                self.xdim = len(im_arr[0][1])
                self.ydim = len(im_arr[0][0])
        im_arr = np.array(im_arr)
        return im_arr

    def get_stitching_order(self): #Need to figure out a smart way to do this
        if self.stitch_height == 2 and self.stitch_width == 2:
            return ["0"+str(x) for x in range(1, 5)]
        elif self.stitch_height == 3 and self.stitch_width == 3:
            return ["05"] + ["0"+str(x) for x in range(1, 10) if x!=5]
        elif self.stitch_height == 4 and self.stitch_width == 4:
            return ["10"] + ["0"+str(x) for x in range(1, 10)] + [str(x) for x in range(11, 17)]
        elif self.stitch_height == 5 and self.stitch_width == 5:
            return ["13"] + ["0"+str(x) for x in range(1, 10)] + [str(x) for x in range(11, 26) if x!=13]
        elif self.stitch_height == 11 and self.stitch_width == 9:
            return ["50"] + ["0"+str(x) for x in range(1, 10)] + [str(x) for x in range(10,100) if x!=50]
        else:
            print("WARNING: Stitching will not be performed correctly!")
        
    def run(self):
        for cur_well in self.files.well_names:
            cur_save = os.path.join(self.save_dir, cur_well)
            self.files.create_dir(cur_save)

            if not self.is_data_timelapse:
                for cur_FOV in range(1, self.FOVs+1):
                    pattern = fr"r\d+c\d+f0?{cur_FOV}p\d+-ch\d+t\d+.tiff?"
                    cur_image_name = self.files.get_opera_phenix_images_from_FOV(cur_well, pattern)
                    images = self.load_images(cur_image_name)
                
                    try:
                        images = np.reshape(images, [self.planes, self.channels, self.xdim, self.ydim])
                        processor = ImageProcessor(images, self.config_file)
                        processor.process(max_proj=self.processes_to_run["max_projection"], 
                                          to_8bit=self.processes_to_run["convert_to_8bit"], 
                                          min_proj=self.processes_to_run["min_projection"], 
                                          edf_proj=self.processes_to_run["EDF_projection"], 
                                          edf_BFch=self.BFch-1,
                                          imagej_loc=self.imagej_loc,
                                          imagej_proc_order = self.imagej_proc_order)

                    except ValueError as e:
                        print("Error processing well " + cur_well + " field " + str(cur_FOV) + " with ValueError.")
                        continue

                    try:
                        if np.ndim(processor.get_image()) == 4:
                            tifffile.imwrite(cur_save + "/" + cur_well + "f" + self.FOV_rename_order[cur_FOV-1] + ".tif",
                                         processor.get_image(), imagej=True, metadata={'axes': 'ZCYX'})
                            
                            if self.processes_to_run["separate_ch"] == 1:
                                for ch in range(self.channels):
                                    ch_save_path = os.path.join(cur_save, "ch"+str(ch+1))
                                    if not os.path.exists(ch_save_path):
                                        os.makedirs(ch_save_path)
                                    tifffile.imwrite(ch_save_path + "/" + cur_well + "f" + self.FOV_rename_order[cur_FOV-1] + ".tif",
                                                     processor.get_image()[:,ch,:,:], imagej=True, metadata={'axes': 'ZYX'})
                        else:
                            tifffile.imwrite(cur_save + "/" + cur_well + "f" + self.FOV_rename_order[cur_FOV-1] + ".tif",
                                         processor.get_image(), imagej=True, metadata={'axes': 'CYX'})


                            if self.processes_to_run["stitching"] == 1 or self.processes_to_run["separate_ch"] == 1:
                                for ch in range(self.channels):
                                    ch_save_path = os.path.join(cur_save, "ch"+str(ch+1))
                                    if not os.path.exists(ch_save_path):
                                        os.makedirs(ch_save_path)
                                    tifffile.imwrite(ch_save_path+"/"+cur_well+"f"+self.FOV_rename_order[cur_FOV-1]+".tif", 
                                                     processor.get_image()[ch,:,:], imagej=True, metadata={'axes':'YX'})
                    
                    except Exception as e:
                        print(f"An unexpected error {e} while saving data")
                        continue


                if self.processes_to_run["stitching"] == 1 and len([f for f in os.listdir(cur_save) if f.endswith(".tif")]) == len(self.FOV_rename_order):
                    try:    
                        StitchProcessing(cur_save, self.stitch_ref_ch, self.imagej_loc, self.stitch_height, self.stitch_width)
            
                    except ValueError as e:
                        print("Error stitching well " + cur_well + " with ValueError.")
                        continue

                #TODO Add imagej processing after stitching!
                if self.imagej_proc_order == "after stitching":
                    
                    try:
                        stitch_loc = os.path.join(cur_save, "Stitched")
                        stitch_pattern = fr".*_ch\d*.tiff?"
                        image_files = self.files.get_name_from_regexstring(stitch_loc, stitch_pattern)
                        post_stitched_image_name = [os.path.join(stitch_loc, image_files[i]) for i in range(len(image_files))]
                        post_stitched_images = self.load_images(post_stitched_image_name)

                        post_stitched_processor = ImageJProcessor(post_stitched_images)
                        post_stitched_processor.process()
                    except:
                        print("Error processing well " + cur_well + " with ImageJ macro after stitching")
                        continue

                    try:
                        tifffile.imwrite(stitch_loc + "/" + cur_well + "_imagejProcessed.tif",
                                         post_stitched_processor.get_image(), imagej=True, metadata={'axes': 'CYX'})
                    except Exception as e:
                        print(f"An unexpected error {e} while saving data")
                        continue
                    
            else:
                for cur_FOV in range(1, self.FOVs+1):
                    print("FOVcall")
                    processed_image = []
                    for timepoint in range(1, self.timepoints):
                        print("Timepoint call")
                        pattern = fr"r\d+c\d+f0?{cur_FOV}p\d+-ch\d+t0?{timepoint}.tiff"
                        cur_image_name = self.files.get_opera_phenix_images_from_FOV(cur_well, pattern)
                        images = self.load_images(cur_image_name)

                        try:
                            images = np.reshape(images, [self.planes, self.channels, self.xy, self.xy])
                            processor = ImageProcessor(images, self.config_file)
                            processor.process(max_proj=self.processes_to_run["max_projection"], 
                                              to_8bit=self.processes_to_run["convert_to_8bit"], 
                                              min_proj=self.processes_to_run["min_projection"],
                                              imagej_proc_order = self.imagej_proc_order)
                            processed_image.append(processor.get_image())

                        except ValueError as e:
                            print("Error processing well " + cur_well + " field " + str(cur_FOV) + " with ValueError.")
                            continue

                    processed_images = np.array(processed_image)

                    try:
                        if np.ndim(processed_images) == 5:
                            tifffile.imwrite(cur_save+"/"+cur_well + "f"+self.FOV_rename_order[cur_FOV-1]+".tif", processed_images,
                                         imagej=True, metadata={'axes':'TZCYX'})
                        else:
                            tifffile.imwrite(cur_save + "/" + cur_well + "f" + self.FOV_rename_order[cur_FOV-1] + ".tif", processed_images,
                                         imagej=True, metadata={'axes': 'TCYX'})
                    
                    except Exception as e:
                        print(f"An unexpected error {e} while saving data")
                        continue
                    
        if self.processes_to_run["cellpose"] == 1:
            try:
                cellpose_organiser(self.save_dir, self.BFch)
            except:
                print("Error segmenting with Cellpose.")

        print(f"Done processing to {cur_save}!")        
        
if __name__ == "__main__":
    OperaGUI()