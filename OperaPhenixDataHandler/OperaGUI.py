import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
import re
import os

from ConfigReader import OperaExperimentConfigReader
from FileManagement import FilePathHandler

class OperaGUI:
    """GUI, getting input from user to run Opera processing."""
    def __init__(self):
        self.root = tk.Tk()

        self.root.geometry("800x200")
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

        # Choose processing steps
        self.checkframe = tk.Frame(self.root)
        self.checkframe.columnconfigure(0, weight=1)
        self.checkframe.columnconfigure(1, weight=1)
        self.checkframe.columnconfigure(2, weight=1)
        self.checkframe.columnconfigure(3, weight=1)

        self.bit8_state = tk.IntVar()
        self.timelapse_state = tk.IntVar()
        self.maxproj_state = tk.IntVar()
        self.stitching_state = tk.IntVar()

        self.bit8_check = ttk.Checkbutton(self.checkframe, text="Convert to 8-bit", variable=self.bit8_state)
        self.bit8_check.grid(row=0, column=0, padx=10, pady=10)

        self.timelapse_check = ttk.Checkbutton(self.checkframe, text="Timelapse Data", variable=self.timelapse_state)
        self.timelapse_check.grid(row=0, column=1, padx=10, pady=10)

        self.maxproj_check = ttk.Checkbutton(self.checkframe, text="Perform maximum projection", variable=self.maxproj_state)
        self.maxproj_check.grid(row=0, column=2, padx=10, pady=10)

        self.stitching_check = ttk.Checkbutton(self.checkframe, text="Stitch images", variable=self.stitching_state)
        self.stitching_check.grid(row=0, column=3, padx=10, pady=10)

        self.checkframe.pack()

        # Confirm button
        self.buttonframe = tk.Frame(self.root)
        self.buttonframe.columnconfigure(0, weight=1)

        self.confirm_button = ttk.Button(self.buttonframe, text="OK", command=self.confirm)
        self.confirm_button.grid(row=0, column=0, padx=58, pady=10, sticky=tk.E)
        
        self.buttonframe.pack(fill='x')

        self.root.mainloop()
    
    def get_directory(self, button):
        """Asks users to choose the source and saving directories."""
        if button == "src_button":
            src_dir = askdirectory(title="Choose directory for images to be processed")
            self.src_entry_text.set(src_dir)
        if button == "save_button":
            save_dir = askdirectory(title="Choose saving directory for processed images")
            self.save_entry_text.set(save_dir)

    def confirm(self):
        """Checks the choices have been made for directories and processing steps. """
        if self.src_entry_text.get() == "" or not self.src_entry_text.get().endswith("hs"):
            messagebox.showinfo(title="Missing Information", message="Please choose the hs source directory")
        elif self.save_entry_text.get() == "":
            messagebox.showinfo(title="Missing Information", message="Please choose saving directory")
        elif (self.bit8_state.get() == 0 and self.timelapse_state.get() == 0 and self.maxproj_state.get() == 0 and self.stitching_state.get()):
            messagebox.showinfo(title="Missing Information", message="Please select processing actions")
        else:
            src_dir = self.src_entry_text.get()
            save_dir = self.save_entry_text.get()


            bit8 = self.bit8_state.get()
            timelapse = self.timelapse_state.get()
            maxproj = self.maxproj_state.get()
            stitch = self.stitching_state.get()

            OperaProcessing(src_dir, save_dir, bit8, timelapse, maxproj, stitch)
            self.run_processing(src_dir, save_dir, bit8, timelapse, maxproj)
        
    def run_processing(self, src_dir, save_dir, bit8, timelapse, maxproj):
        message_text = "Running processing on images in directory " + src_dir + "\n which will be saved in directory " + save_dir +".\n\nPerforming "
        if bit8 == 1:
            message_text += "converting to 8-bit \n"
        if timelapse == 1:
            message_text += "timelapse merge \n"
        if maxproj == 1:
            message_text += "maximum projection \n"
        messagebox.showinfo(title="Processing Configuration", message=message_text)


class OperaProcessing:
    """Performs the specified processing steps on the images selected from the GUI."""
    def __init__(self, src_dir, save_dir, bit8, timelapse, maxproj, stitch):
        #messagebox.showinfo(title="Opera Class", message="Time for processing!")
        for measurement in [f for f in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, f))]:
            measurementPath = os.path.join(src_dir, measurement)
            #print(measurementPath)
            files = self.get_file_paths(measurementPath)
            print(files.archived_data_path)
            #print(files.archived_data_config)
            #print(files.well_names)

            opera_config_file = self.get_metadata(files.archived_data_config)
            print(opera_config_file)


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
        

OperaGUI()