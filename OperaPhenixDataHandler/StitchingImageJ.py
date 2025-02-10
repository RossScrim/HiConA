import imagej
import os
import re
import scyjava
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from shutil import copy

def rename_FOV(path):
    rename_order = ["f05", "f01", "f04", "f07", "f08", "f02", "f03", "f06", "f09"]
    files = [f for f in sorted(os.listdir(path)) if re.search(r"r\d*c\d*f\d*\.tiff", f)]
    #print(files)
    
    for i in range(len(files)):
        cur_name = files[i]
        new_name = cur_name.replace("f"+str(i+1), rename_order[i])

        os.rename(os.path.join(path, cur_name), os.path.join(path, new_name))

def stitch_first_imageJ(orgDir, saveDir, wellName, chName, ij):
    #In the macro, change where the bf.tiff is stored and where the processed_bf should be saved.
    macro = """
    //@ String orgDir
    //@ String saveDir
    //@ String wellName
    //@ String chName

    //path = replace(orgDir, "/", File.separator);
    //print(path);

    run("Grid/Collection stitching", "type=[Grid: column-by-column] order=[Down & Right                ] grid_size_x=3 grid_size_y=3 tile_overlap=5 first_file_index_i=1 directory=["+orgDir+"] file_names="+wellName+"f{ii}.tif output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap subpixel_accuracy computation_parameters=[Save memory (but be slower)] image_output=[Fuse and display]");
    saveAs("Tiff", saveDir+File.separator+wellName+"_"+chName+".tif");
    close("*");
    """

    args = {
        'orgDir': orgDir,
        'saveDir': saveDir,
        'wellName': wellName,
        'chName': chName
    }

    ij.py.run_macro(macro, args)

def stitch_remaining_imageJ(orgDir, saveDir, wellName, chName, ij):
    #In the macro, change where the bf.tiff is stored and where the processed_bf should be saved.
    macro = """
    //@ String orgDir
    //@ String saveDir
    //@ String wellName
    //@ String chName

    //path = replace(orgDir, "/", File.separator);
    //print(path);

    run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration] directory=["+orgDir+"] layout_file=TileConfiguration.registered.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 subpixel_accuracy computation_parameters=[Save memory (but be slower)] image_output=[Fuse and display]");

    saveAs("Tiff", saveDir+File.separator+wellName+"_"+chName+".tif");
    close("*");
    """

    args = {
        'orgDir': orgDir,
        'saveDir': saveDir,
        'wellName': wellName,
        'chName': chName
    }

    ij.py.run_macro(macro, args)

def mergeImages(orgDir, wellName, ij):
    macro = """
    //@ String orgDir
    //@ String wellName
    
    File.openSequence(orgDir, " open");
    run("Images to Stack", "method=[Scale (smallest)] name="+wellName);

    run("Re-order Hyperstack ...", "channels=[Slices (z)] slices=[Channels (c)] frames=[Frames (t)]");

    Stack.setChannel(1);
    run("Red");
    Stack.setChannel(2);
    run("Grays");

    saveAs("Tiff", orgDir+File.separator+wellName+".tif");

    close("*");
    """

    args = {
        'orgDir': orgDir,
        'wellName': wellName
    }

    ij.py.run_macro(macro, args)

def StitchProcessing(well_path, BFch):
    plugins_dir = "C:/Users/ewestlund/Fiji.app/plugins" #Add path to Fiji Plugins
    scyjava.config.add_option(f'-Dplugins.dir={plugins_dir}')
    ij = imagej.init("C:/Users/ewestlund/Fiji.app")#, mode="interactive") #Add path to Fiji.app folder
    #ij.ui().showUI()

    wellName = os.path.basename(os.path.normpath(well_path))

    stitched_path = os.path.join(well_path, "Stitched")
    if not os.path.exists(stitched_path):
        os.makedirs(stitched_path)

    BF_dir = "ch"+str(BFch)
    BF_path = os.path.join(well_path, BF_dir)

    ch_directories = [d for d in os.listdir(well_path) if os.path.isdir(os.path.join(well_path, d)) and d.startswith("ch") and d != BF_dir]


    stitch_first_imageJ(BF_path, stitched_path, wellName, BF_dir, ij)

    stitch_configuration_files = [f for f in os.listdir(BF_path) if f.endswith(".txt")]

    for ch_dir in ch_directories:
        ch_path = os.path.join(well_path, ch_dir)

        for config in stitch_configuration_files:
            copy(os.path.join(BF_path, config), os.path.join(ch_path, config))

        stitch_remaining_imageJ(ch_path, stitched_path, wellName, ch_dir, ij)

    mergeImages(stitched_path, wellName, ij)
    
    ij.dispose()


class StitchingGUI:
    """GUI, getting input from user to run Opera processing."""
    def __init__(self):
        self.root = tk.Tk()

        #self.root.geometry("800x150")
        self.root.title("Stitching")

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
        if self.src_entry_text.get() == "":
            messagebox.showinfo(title="Missing Information", message="Please choose source directory")
        elif self.save_entry_text.get() == "":
            messagebox.showinfo(title="Missing Information", message="Please choose saving directory")
        elif self.src_entry_text.get() == self.save_entry_text.get():
            messagebox.showinfo(title="Missing Information", message="Please choose a different saving directory from your source directory")
        else:
            self.src_dir = self.src_entry_text.get()
            self.save_dir = self.save_entry_text.get()
            self.root.destroy()

            return self.src_dir, self.save_dir


if __name__ == "__main__":
    StitchProcessing("Z:/Florian/bce184b7-d089-418f-b0cd-57c5193941ef/r06c01")
