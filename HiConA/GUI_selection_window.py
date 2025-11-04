import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from tkinter import Scrollbar, Canvas
from tkinter.filedialog import askdirectory, askopenfilename
import os
import json

from ConfigReader import OperaExperimentConfigReader
from FileManagement import FilePathHandler

class SelectionGUI:
    def __init__(self, source_input):
        print("Running Selection Window")
        self.src_dir = source_input["src_dir"]
        self.save_dir = source_input["save_dir"]

        self.saved_var = self._load_variables()

        self.measurement_dict, self.config_files = self._get_measurement_from_src()

        self.root = tb.Window(themename="lumen", title="HiConA")
        self.root.geometry("1270x850")
        self.root.bind_all("<MouseWheel>")
        self._initiate_window()
        self.root.mainloop()


    def _get_measurement_from_src(self):
        measurement_dict = {}
        config_files = {}
        for measurement in [f for f in os.listdir(self.src_dir) if (os.path.isdir(os.path.join(self.src_dir, f)) and f != "_configdata")]:
            measurement_path = os.path.join(self.src_dir, measurement)

            files = FilePathHandler(measurement_path)
            opera_config_file = OperaExperimentConfigReader(files.archived_data_config).load_json_from_txt(remove_first_lines=1, remove_last_lines=2)

            plate_name = opera_config_file["PLATENAME"]
            measure_num = opera_config_file["MEASUREMENT"].split(" ")
            guid = opera_config_file["GUID"]
            
            name = plate_name + " - " + measure_num[-1]
            measurement_dict[name] = guid 
            config_files[guid] = opera_config_file
        
        return dict(sorted(measurement_dict.items())), config_files
    
    def _load_variables(self):
        self.saved_variables_f = os.path.join(os.path.dirname(__file__), "saved_variables_selection.json")
        if os.path.isfile(self.saved_variables_f):
            with open(self.saved_variables_f, "r+") as f:
                return json.load(f)
    
    def _set_variable(self, variable_name):
        try:
            return self.saved_var[variable_name]
        except:
            return ""

    def _configurefunction(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=350, height=720)

    def _on_mousewheel(self, event):
        self.root.yview_scroll(int(-1*(event.delta/120)), "units")

    def _define_processing(self):
         processing_selection = {'8bit': self.bit8_state.get(),
                                 'sep_ch': self.sep_ch_state.get(),
                                 'edf_proj': self.edfproj_text.get(),
                                 'EDF_channel': self.edf_ch_int.get(),
                                 'stitching': self.stitching_state.get(),
                                 'stitch_ref_ch': self.stitching_ch_int.get(),
                                 'imagej_loc': self.imagej_entry_text.get(),
                                 'cellpose': self.cellpose_state.get(),
                                 'cellprofiler': self.cellprofiler_state.get(),
                                 'imagej': self.imagej_state.get()}
         return processing_selection
    
    def _get_directory(self, button):
        #Asks users to choose directories.
        if button == "imagej_button":
            imagej_dir = askdirectory(title="Choose location for Fiji.app directory")
            self.imagej_entry_text.set(imagej_dir)
        if button == "macro_button":
            macro_file = askopenfilename(title="Choose location for ImageJ macro file")
            self.macro_entry_text.set(macro_file)
        if button == "arg_button":
            arg_file = askopenfilename(title="Choose location for ImageJ arguments file")
            self.arg_entry_text.set(arg_file)

    
    def _show_hidden_frame_bind(self, e): #add imageJ location appearing
            showimageJ = [0,0]
            if self.edfproj_text.get() == "ImageJ EDF":
                self.edf_frame.grid(row=3, columnspan=4, pady=10, sticky=tk.W)
                showimageJ[0] = 1
            else:
                self.edf_frame.grid_forget()
                showimageJ[0] = 0
            
            if self.stitching_state.get() == 1:
                self.stitching_frame.grid(row=5, columnspan=4, pady=10, sticky=tk.W)
                showimageJ[1] = 1
            else:
                self.stitching_frame.grid_forget()
                showimageJ[1] = 0

            if True in (t == 1 for t in showimageJ):
                self.imagej_frame.grid(row=6, columnspan=4, pady=20, sticky=tk.W)
            else:
                self.imagej_frame.grid_forget()


    def _validate_int(self,x):
        if x.isdigit() and x != 0:
            return True
        else:
            return False
    
    def _save_variables(self, EDFchannel, stitch_ref_ch, imagej_loc):
        # Save used variables using json for next run
        var_dict = {"EDF_channel": EDFchannel,
                    "stitch_ref_ch": stitch_ref_ch,
                    "imagej_loc": imagej_loc}
            
        with open(self.saved_variables_f, "w+") as f:
            json.dump(var_dict, f)

    def _get_measurement_to_process(self):
        measurement_to_process = [self.measurement_dict[list(self.measurement_dict.keys())[i]] for i in range(len(self.measurement_dict)) if self.measure_var_list[i].get() == 1]
        return dict(zip(measurement_to_process, [self.config_files[j] for j in measurement_to_process])) # key: guid, value: corresponding config file       


    def _confirm_button(self):
        imagej_loc = self.imagej_entry_text.get()
        stitch_ref_ch = int(self.stitching_ch_int.get())
        EDFchannel = int(self.edf_ch_int.get())

        if all(x.get() == 0 for x in self.measure_var_list):
            Messagebox.show_info(message="Please select a measurement to analyse", title="Missing Information")
        elif self.edfproj_text.get() == "ImageJ EDF" and EDFchannel == 0:
            Messagebox.show_info(message="Please select a channel for the EDF process", title="Missing Information")
        elif self.stitching_state.get() == 1 and stitch_ref_ch == 0:
            Messagebox.show_info(message="Please select a reference channel for the stitching process", title="Missing Information")
        elif (self.edfproj_text.get() == "ImageJ EDF" or self.stitching_state.get() == 1) and self.imagej_entry_text.get() == "":
            Messagebox.show_info(message="Please select the location to ImageJ", title="Missing Information")
        else:
            self._save_variables(EDFchannel, stitch_ref_ch, imagej_loc)

            self.measurement_config_matched = self._get_measurement_to_process()
            self.processing_selection = self._define_processing()

            self.root.destroy()

    def _initiate_window(self):
        # Head of window
        tb.Label(self.root, text="Measurements", font=("Segoe UI", 14)).grid(row=0, column=0, padx=10, pady=5)
        tb.Label(self.root, text="Processing Options", font=("Segoe UI", 14)).grid(row=0, column=1, padx=70, pady=5, sticky=tk.W)
        
        separator = ttk.Separator(self.root, orient=tk.VERTICAL)
        #separator.place(x=320, y=0, relheight=0.9, relwidth=1)
        separator.grid(column=2, rowspan=10, ipadx=10, ipady=350, sticky=tk.E)
        
        tb.Label(self.root, text="Analysis Options", font=("Segoe UI", 14)).grid(row=0, column=3, padx=50, pady=5, sticky=tk.W)

        # Measurement list with scrollbar
        measurement_frame = tb.Frame(self.root, height=800)
        measurement_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)
        self.canvas = Canvas(measurement_frame)
        int_measurement_frame = tb.Frame(self.canvas)
        scrollbar = Scrollbar(measurement_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left")
        self.canvas.create_window((0,0), window=int_measurement_frame, anchor=tk.NW)
        int_measurement_frame.bind("<Configure>", self._configurefunction)

        self.measure_var_list = []

        for index, measurement in enumerate(self.measurement_dict.keys()):
             self.measure_var_list.append(tk.IntVar(value=0))
             tb.Checkbutton(int_measurement_frame, variable=self.measure_var_list[index],
                            text=measurement).pack(fill="x")
        

        # Processing Frame
        processing_frame = tb.Frame(self.root)
        processing_frame.grid(row=1, column=1, padx=5, pady=10, sticky=tk.NW)
        processing_frame.propagate(0)

        # Processing options
        self.bit8_state = tk.IntVar()
        self.sep_ch_state = tk.IntVar()
        self.edfproj_text = tk.StringVar()
        self.edf_ch_int = tk.IntVar()
        self.stitching_state = tk.IntVar()
        self.stitching_ch_int = tk.IntVar()

        self.processing_options = {"8bit": self.bit8_state,
                                   "sep_ch": self.sep_ch_state,
                                   "edf": self.edfproj_text,
                                   "stitching": self.stitching_state}


        self.bit8_check = tb.Checkbutton(processing_frame, text = "Convert to 8-bit",
                                         variable=self.bit8_state)
        self.bit8_check.grid(row=0, column=0, pady=5, sticky=tk.W)

        self.sep_ch_check = tb.Checkbutton(processing_frame, text="Separate channels          ",
                                           variable=self.sep_ch_state)
        self.sep_ch_check.grid(row=1, column=0, pady=5, sticky=tk.W)

        tb.Label(processing_frame, text="Extended Depth of Focus").grid(row=2, column=0, pady=20, sticky=tk.W)
        self.proj_combo = tb.Combobox(processing_frame, textvariable=self.edfproj_text, width=12, 
                                      state='readonly', values=["None", "Maximum", "Minimum", "ImageJ EDF"])
        self.proj_combo.grid(row=2, column=1, pady=15, sticky=tk.W)
        self.proj_combo.current(0)
        self.proj_combo.bind("<<ComboboxSelected>>", self._show_hidden_frame_bind)

        self.edf_frame = tb.Frame(processing_frame)
        tb.Label(self.edf_frame, text="Channel for ImageJ EDF").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.edfproj_entry = tb.Entry(self.edf_frame, text=self.edf_ch_int, width=2, background="White", validate='focus', 
                                      validatecommand=(self.root.register(self._validate_int), '%P')).grid(row=0, column=1, padx=38, sticky=tk.W)

        
        self.stitching_check = tb.Checkbutton(processing_frame, text = "Stitching",
                                         variable=self.stitching_state, command=lambda: self._show_hidden_frame_bind(True))
        self.stitching_check.grid(row=4, column=0, pady=10, sticky=tk.W)

        self.stitching_frame = tb.Frame(processing_frame)
        tb.Label(self.stitching_frame, text="Channel for Stitching").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.stitching_entry = tb.Entry(self.stitching_frame, text=self.stitching_ch_int, width=2, background="White", validate='focus', 
                                      validatecommand=(self.root.register(self._validate_int), '%P')).grid(row=0, column=1, padx=65, sticky=tk.W)

        self.imagej_frame = tb.Frame(processing_frame)
        tb.Label(self.imagej_frame, text="ImageJ.app Location").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.imagej_entry_text = tk.StringVar()
        self.imagej_entry_text.set(self._set_variable("imagej_loc"))

        self.imagej_entry = tb.Entry(self.imagej_frame, text=self.imagej_entry_text, width=13, state='readonly')
        self.imagej_entry.grid(row=0, column=1, padx=20, pady=30, sticky=tk.W)

        self.imagej_button = tb.Button(self.imagej_frame, text="...", command=lambda: self._get_directory("imagej_button"), bootstyle="secondary")
        self.imagej_button.grid(row=0, column=2, pady=30, sticky=tk.W)

        # Analysis Frames
        analysis_frame = tb.Frame(self.root, width=800)
        analysis_frame.grid(row=1, column=3, padx=20, pady=10, sticky=tk.NW)
        analysis_frame.propagate(0)

        # Analysis Options
        self.cellprofiler_state = tk.IntVar() 
        self.imagej_state = tk.IntVar()
        self.cellpose_state = tk.IntVar()     

        self.analysis_options = {"cellprofiler": self.cellpose_state,
                                 "cellpose": self.cellpose_state,
                                 "imagej": self.imagej_state}

        self.imagej_check = tb.Checkbutton(analysis_frame, text = "ImageJ",
                                         variable=self.cellpose_state)
        self.imagej_check.grid(row=0, column=0, pady=5, sticky=tk.W)  
        
        self.cellprofiler_check = tb.Checkbutton(analysis_frame, text = "Cellprofiler",
                                         variable=self.cellprofiler_state)
        self.cellprofiler_check.grid(row=1, column=0, pady=5, sticky=tk.W)  

        self.cellpose_check = tb.Checkbutton(analysis_frame, text = "Cellpose",
                                         variable=self.imagej_state)
        self.cellpose_check.grid(row=2, column=0, pady=5, sticky=tk.W)


        # Confirm button
        self.buttonframe = tk.Frame(self.root)
        self.buttonframe.grid(row=2, column=4, sticky=tk.N)

        self.confirm_button = ttk.Button(self.buttonframe, text="OK", command=self._confirm_button)
        self.confirm_button.grid(row=0, column=0, padx=0, pady=0, sticky=tk.W)
    
    def get_input(self):
        return self.measurement_config_matched, self.processing_selection


if __name__ == "__main__":
    input = {"src_dir": r"C:\Users\ewestlund\Documents\Python Projects\HiConA\Opera Phenix Test Data\hs", "save_dir": r"C:\Users\ewestlund\Documents\Python Projects\HiConA\Saving Dir Test"}
    w = SelectionGUI(input)
    measurements, processes = w.get_input()
    print("Will process measurements:")
    print(measurements)
    print("Selected processes: ")
    print(processes)