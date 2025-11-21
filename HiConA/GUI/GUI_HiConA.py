import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from tkinter import Scrollbar, Canvas
from tkinter.filedialog import askdirectory, askopenfilename
import os
import json

from HiConA.Utilities.ConfigReader import ConfigReader
from HiConA.Utilities.FileManagement import FilePathHandler

class HiConAGUI:
    def __init__(self, window):
        print("Running")
        self.master = window
        self._load_variables()

        self._initiate_window()


    def _initiate_window(self):
        # Configure master
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(2, weight=1)

        # Initiating Frames
        source_frame = tb.Frame(self.master)
        source_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)

        separator = ttk.Separator(self.master, orient=tk.HORIZONTAL)
        separator.grid(row=1, column=0, ipadx=0, ipady=5, sticky=tk.EW)

        selection_frame = tb.Frame(self.master)
        selection_frame.grid(row=2, column=0, padx=5, pady=5, sticky=tk.NSEW)

        selection_frame.columnconfigure(0, weight=0, minsize=420) # Measurement frame
        selection_frame.columnconfigure(1, weight=0, minsize=600) # Processing frame
        selection_frame.columnconfigure(2, weight=0, minsize=200) # Analysis frame

        tb.Label(selection_frame, text="Measurements", font=("Segoe UI", 14)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        tb.Label(selection_frame, text="Processing Options", font=("Segoe UI", 14)).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        tb.Label(selection_frame, text="Analysis Options", font=("Segoe UI", 14)).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        # Source dir and Save dir selection
        # Variables
        self.src_entry_text = tk.StringVar()
        self.src_entry_text.set(self._set_variable("src_entry_text"))
        self.output_entry_text = tk.StringVar()
        self.output_entry_text.set(self._set_variable("output_entry_text"))

        # Widgets
        src_label = tb.Label(source_frame, text="Source directory", font=("Segoe UI", 14))
        src_label.grid(row=0, column=0, padx=10, pady=10)

        self.src_selected = tb.Entry(source_frame, text=self.src_entry_text, width=70, state='readonly')
        self.src_selected.grid(row=0, column=1, padx=10, pady=10)

        self.src_button = tb.Button(source_frame, text="...", command=lambda: self._get_directory("src_button"), bootstyle="secondary")
        self.src_button.grid(row=0, column=2, padx=10, pady=10)

        self.output_label = tb.Label(source_frame, text="Output directory", font=("Segoe UI", 14))
        self.output_label.grid(row=1, column=0, padx=10, pady=10)

        self.output_selected = ttk.Entry(source_frame, text=self.output_entry_text, width=70, state='readonly')
        self.output_selected.grid(row=1, column=1, padx=10, pady=10)

        self.output_button = ttk.Button(source_frame, text="...", command=lambda: self._get_directory("output_button"), bootstyle="secondary")
        self.output_button.grid(row=1, column=2, padx=10, pady=10)

        # Update button
        self.confirm_button = tb.Button(source_frame, text="Update", command=self._update_selection)
        self.confirm_button.grid(row=0, column=3, padx=10, pady=10, sticky=tk.E)


        # Processing and Analysis selection
        # Measurements
        # Measurement list with scrollbar
        measurement_frame = tb.Frame(selection_frame, height=600, width=420)
        measurement_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
        measurement_frame.grid_propagate(False)
        measurement_frame.pack_propagate(False)

        self.canvas = Canvas(measurement_frame, width=400, height=580, highlightthickness=0)
        self.int_measurement_frame = tb.Frame(self.canvas)
        scrollbar = Scrollbar(measurement_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill='both', expand=False)
        self.canvas.create_window((0,0), window=self.int_measurement_frame, anchor=tk.NW)
        self.int_measurement_frame.bind("<Configure>", self._configurefunction)

        self.measure_var_list = []

        # Processing options
        processing_frame = tb.Frame(selection_frame, height=600, width=400)
        processing_frame.grid(row=1, column=1, padx=5, pady=10, sticky=tk.NSEW)
        processing_frame.grid_propagate(False)
        

        separator = ttk.Separator(processing_frame, orient=tk.VERTICAL)
        separator.place(relx=1.0, rely=0, relheight=1.0, anchor=tk.NE)
        #separator.grid(rowspan=10, column=2, ipadx=10, ipady=350, sticky=tk.E)

        # Processing options
        self.bit8_state = tk.IntVar()
        self.sep_ch_state = tk.IntVar()
        self.proj_text = tk.StringVar()
        self.edf_ch_int = tk.IntVar()
        self.edf_ch_int.set(self._set_variable("EDF_channel_int"))
        self.stitching_state = tk.IntVar()
        self.stitching_ch_int = tk.IntVar()
        self.stitching_ch_int.set(self._set_variable("stitch_ref_ch_int"))

        self.processing_options = {"8bit": self.bit8_state,
                                   "sep_ch": self.sep_ch_state,
                                   "edf": self.proj_text,
                                   "stitching": self.stitching_state}


        self.bit8_check = tb.Checkbutton(processing_frame, text = "Convert to 8-bit",
                                         variable=self.bit8_state)
        self.bit8_check.grid(row=0, column=0, pady=5, sticky=tk.W)

        self.sep_ch_check = tb.Checkbutton(processing_frame, text="Separate channels          ",
                                           variable=self.sep_ch_state)
        self.sep_ch_check.grid(row=1, column=0, pady=5, sticky=tk.W)

        tb.Label(processing_frame, text="Extended Depth of Focus").grid(row=2, column=0, pady=20, sticky=tk.W)
        self.proj_combo = tb.Combobox(processing_frame, textvariable=self.proj_text, width=12, 
                                      state='readonly', values=["None", "Maximum", "Minimum", "ImageJ EDF"])
        self.proj_combo.grid(row=2, column=1, pady=15, sticky=tk.W)
        self.proj_combo.current(0)
        self.proj_combo.bind("<<ComboboxSelected>>", self._show_hidden_frame_bind)

        self.edf_frame = tb.Frame(processing_frame)
        tb.Label(self.edf_frame, text="Channel for ImageJ EDF").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.edfproj_entry = tb.Entry(self.edf_frame, text=self.edf_ch_int, width=2, background="White", validate='focus', 
                                      validatecommand=(self.master.register(self._validate_int), '%P')).grid(row=0, column=1, padx=38, sticky=tk.W)

        
        self.stitching_check = tb.Checkbutton(processing_frame, text = "Stitching",
                                         variable=self.stitching_state, command=lambda: self._show_hidden_frame_bind(True))
        self.stitching_check.grid(row=4, column=0, pady=10, sticky=tk.W)

        self.stitching_frame = tb.Frame(processing_frame)
        tb.Label(self.stitching_frame, text="Channel for Stitching").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.stitching_entry = tb.Entry(self.stitching_frame, text=self.stitching_ch_int, width=2, background="White", validate='focus', 
                                      validatecommand=(self.master.register(self._validate_int), '%P')).grid(row=0, column=1, padx=65, sticky=tk.W)

        self.imagej_frame = tb.Frame(processing_frame)
        tb.Label(self.imagej_frame, text="ImageJ.app Location").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.imagej_entry_text = tk.StringVar()
        self.imagej_entry_text.set(self._set_variable("imagej_loc_entry"))

        self.imagej_entry = tb.Entry(self.imagej_frame, text=self.imagej_entry_text, width=13, state='readonly')
        self.imagej_entry.grid(row=0, column=1, padx=20, pady=30, sticky=tk.W)

        self.imagej_button = tb.Button(self.imagej_frame, text="...", command=lambda: self._get_directory("imagej_button"), bootstyle="secondary")
        self.imagej_button.grid(row=0, column=2, pady=30, sticky=tk.W)

        # Analysis Frames
        analysis_frame = tb.Frame(selection_frame, height=600, width=200)
        analysis_frame.grid(row=1, column=2, padx=5, pady=5, sticky=tk.NSEW)
        analysis_frame.grid_propagate(False)

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
        self.confirm_button = tb.Button(selection_frame, text="Run", command=self._run_button, bootstyle="info")
        self.confirm_button.grid(row=2, column=3, padx=0, pady=0, sticky=tk.E)


    def _run_button(self):
        self.imagej_loc = self.imagej_entry_text.get()
        self.stitch_ref_ch = int(self.stitching_ch_int.get())
        self.EDFchannel = int(self.edf_ch_int.get())
        self.src_dir = self.src_entry_text.get()
        self.output_dir = self.output_entry_text.get()

        """Checks the choices have been made for directories and processing steps. """
        if self.src_dir == "" or not self.src_dir.endswith("hs"):
            Messagebox.show_info(title="Missing Information", message="Please choose the hs source directory")
        elif self.output_dir == "" or self.src_dir == self.output_dir:
            Messagebox.show_info(title="Missing Information", message="Please choose an output directory that's different from the source directory")
        elif len(self.measure_var_list) == 0:
            Messagebox.show_info(message="Please click on Update to see available measurements", title="Missing Information")
        elif all(x.get() == 0 for x in self.measure_var_list):
            Messagebox.show_info(message="Please select a measurement to analyse", title="Missing Information")
        elif self.proj_text.get() == "ImageJ EDF" and self.EDFchannel == 0:
            Messagebox.show_info(message="Please select a channel for the EDF process", title="Missing Information")
        elif self.stitching_state.get() == 1 and self.stitch_ref_ch == 0:
            Messagebox.show_info(message="Please select a reference channel for the stitching process", title="Missing Information")
        elif (self.proj_text.get() == "ImageJ EDF" or self.stitching_state.get() == 1) and self.imagej_entry_text.get() == "":
            Messagebox.show_info(message="Please select the location to ImageJ", title="Missing Information")
        else:
            self._save_variables()

            self.measurement_files_matched = self._get_measurement_to_process()
            self.processing_selection = self._define_processing()

            self.master.destroy()

    def _load_variables(self):
        self.saved_variables_f = os.path.join(os.path.dirname(__file__), "saved_variables.json")
        print(self.saved_variables_f)
        if os.path.isfile(self.saved_variables_f):
            with open(self.saved_variables_f, "r+") as f:
                self.saved_var = json.load(f)
            
    def _set_variable(self, variable_name):
        try:
            return self.saved_var[variable_name]
        except:
            return ""
        
    def _save_variables(self):
        # Save used variables using json for next run
        var_dict = {"src_entry_text": self.src_dir,
                    'output_entry_text': self.output_dir,
                    "EDF_channel_int": self.EDFchannel,
                    "stitch_ref_ch_int": self.stitch_ref_ch,
                    "imagej_loc_entry": self.imagej_loc}
            
        with open(self.saved_variables_f, "w+") as f:
            json.dump(var_dict, f)

    def _get_directory(self, button):
        """Asks users to choose the source and saving directories."""
        if button == "src_button":
            src_dir = askdirectory(title="Choose hs directory for images to be processed")
            self.src_entry_text.set(src_dir)
        if button == "output_button":
            save_dir = askdirectory(title="Choose saving directory for processed images")
            self.output_entry_text.set(save_dir)
        if button == "imagej_button":
            imagej_dir = askdirectory(title="Choose location for Fiji.app directory")
            self.imagej_entry_text.set(imagej_dir)
        self._validate(button)

    def _update_selection(self):
        self.src_dir = self.src_entry_text.get()
        if self.src_dir == "" or not self.src_dir.endswith("hs"):
            Messagebox.show_info(title="Missing Information", message="Please choose the hs source directory")
        else:

            self.measurement_dict, self.files = self._get_measurement_from_src()

            # Clear existing widgets
            for widget in self.int_measurement_frame.winfo_children():
                widget.destroy()

            for index, measurement in enumerate(self.measurement_dict.keys()):
                self.measure_var_list.append(tk.IntVar(value=0))

                cb_frame = tb.Frame(self.int_measurement_frame)
                cb_frame.pack(fill='x', pady=2)

                cb = tb.Checkbutton(cb_frame, variable=self.measure_var_list[index])
                cb.pack(side='left', padx=(0,5))

                label = tb.Label(cb_frame, text=measurement, wraplength=400, justify='left', anchor='w')
                label.pack(side='left', fill='x', expand=True)
             
                # Make label clickable to toggle checkbutton
                label.bind("<Button-1>", lambda e, var=self.measure_var_list[index]: var.set(1 - var.get()))

    def _get_measurement_from_src(self):
        measurement_dict = {}
        files = {}
        for measurement in [f for f in os.listdir(self.src_dir) if (os.path.isdir(os.path.join(self.src_dir, f)) and f != "_configdata")]:
            measurement_path = os.path.join(self.src_dir, measurement)

            cur_files = FilePathHandler(measurement_path)
            opera_config_file = ConfigReader(cur_files.archived_data_config).load(remove_first_lines=1, remove_last_lines=2)

            plate_name = opera_config_file["PLATENAME"]
            measure_num = opera_config_file["MEASUREMENT"].split(" ")
            guid = opera_config_file["GUID"]
            
            name = plate_name + " - " + measure_num[-1]
            measurement_dict[name] = guid 

            files[guid] = cur_files
        
        return dict(sorted(measurement_dict.items())), files

    def _get_measurement_to_process(self):
        measurement_to_process = [self.measurement_dict[list(self.measurement_dict.keys())[i]] for i in range(len(self.measurement_dict)) if self.measure_var_list[i].get() == 1]
        # returns key: guid, value: files
        return  dict(zip(measurement_to_process, [self.files[j] for j in measurement_to_process]))    

    def _define_processing(self):
        processing_selection = {'8bit': self.bit8_state.get(),
                                 'sep_ch': self.sep_ch_state.get(),
                                 'proj': self.proj_text.get(),
                                 'EDF_channel': self.edf_ch_int.get(),
                                 'stitching': self.stitching_state.get(),
                                 'stitch_ref_ch': self.stitching_ch_int.get(),
                                 'imagej_loc': self.imagej_entry_text.get(),
                                 'cellpose': self.cellpose_state.get(),
                                 'cellprofiler': self.cellprofiler_state.get(),
                                 'imagej': self.imagej_state.get()}
        return processing_selection

    def _validate(self, button):
        if button == "src_button":
            if self.src_entry_text.get() == "" or not self.src_entry_text.get().endswith("hs"):
                self.src_selected.config(bootstyle="danger")
            else:
                self.src_selected.config(bootstyle="default")
        elif button == "output_button":
            if self.output_entry_text.get() == "" or self.src_entry_text.get() == self.output_entry_text.get():
                self.output_selected.config(bootstyle="danger")
            else:
                self.output_selected.config(bootstyle="default")

    def _configurefunction(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.root.yview_scroll(int(-1*(event.delta/120)), "units")

    def _show_hidden_frame_bind(self, e): #add imageJ location appearing
            showimageJ = [0,0]
            if self.proj_text.get() == "ImageJ EDF":
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

    def get_input(self):
        return self.measurement_files_matched, self.processing_selection, self.output_dir
    

if __name__ == "__main__":
    print("Hej")
    root = tb.Window(themename="lumen", title="HiConA")
    root.geometry("1400x950")
    root.bind_all("<MouseWheel>")
    HiConA = HiConAGUI(root)
    root.mainloop()

    all_files, processes, output_dir = HiConA.get_input()

    print(all_files)
    print(processes)
    