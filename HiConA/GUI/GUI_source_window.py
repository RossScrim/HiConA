import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as tb
from tkinter import messagebox
from tkinter.filedialog import askdirectory
import os
import json

class SourceGUI:
    def __init__(self):
        self.saved_var = self._load_variables()
        
        self.root = tb.Window(themename="lumen", title="HiConA")
        self._initiate_window()

        self.root.mainloop()

    def _load_variables(self):
        self.saved_variables_f = os.path.join(os.path.dirname(__file__), "saved_variables_source.json")
        if os.path.isfile(self.saved_variables_f):
            with open(self.saved_variables_f, "r+") as f:
                return json.load(f)
            
    def _set_variable(self, variable_name):
        try:
            return self.saved_var[variable_name]
        except:
            return ""
        
    def _validate(self, button):
        if button == "src_button":
            if self.src_entry_text.get() == "" or not self.src_entry_text.get().endswith("hs"):
                self.src_selected.config(bootstyle="danger")
            else:
                self.src_selected.config(bootstyle="default")
        elif button == "save_button":
            if self.save_entry_text.get() == "" or self.src_entry_text.get() == self.save_entry_text.get():
                self.save_selected.config(bootstyle="danger")
            else:
                self.save_selected.config(bootstyle="default")

    def _get_directory(self, button):
        """Asks users to choose the source and saving directories."""
        if button == "src_button":
            src_dir = askdirectory(title="Choose hs directory for images to be processed")
            self.src_entry_text.set(src_dir)
        if button == "save_button":
            save_dir = askdirectory(title="Choose saving directory for processed images")
            self.save_entry_text.set(save_dir)
        self._validate(button)

    def _src_confirm(self):
        """Checks the choices have been made for directories and processing steps. """
        if self.src_entry_text.get() == "" or not self.src_entry_text.get().endswith("hs"):
            messagebox.showinfo(title="Missing Information", message="Please choose the hs source directory")
        elif self.save_entry_text.get() == "" or self.src_entry_text.get() == self.save_entry_text.get():
            messagebox.showinfo(title="Missing Information", message="Please choose a saving directory that's different from the source directory")
        else:
            self.src_dir = self.src_entry_text.get()
            self.save_dir = self.save_entry_text.get()

            self._save_variables()
            
            self.root.quit()

    def _save_variables(self):
        # Save used variables using json for next run
        var_dict = {"src_entry_text": self.src_dir, 
                    "save_entry_text": self.save_dir}
            
        with open(self.saved_variables_f, "w+") as f:
            json.dump(var_dict, f)

    def _initiate_window(self):
        directory_frame = tb.Frame(self.root, bootstyle="default")
        directory_frame.grid(row=0, column=0, padx=5, pady=5)

        src_label = tb.Label(directory_frame, text="Source directory", font=("Segoe UI", 14))
        src_label.grid(row=0, column=0, padx=10, pady=10)

        self.src_entry_text = tk.StringVar()
        self.src_entry_text.set(self._set_variable("src_entry_text"))

        self.src_selected = tb.Entry(directory_frame, text=self.src_entry_text, width=70, state='readonly')
        self.src_selected.grid(row=0, column=1, padx=10, pady=10)

        self.src_button = tb.Button(directory_frame, text="...", command=lambda: self._get_directory("src_button"), bootstyle="secondary")
        self.src_button.grid(row=0, column=2, padx=10, pady=10)

        self.save_label = tb.Label(directory_frame, text="Saving directory", font=("Segoe UI", 14))
        self.save_label.grid(row=1, column=0, padx=10, pady=10)

        self.save_entry_text = tk.StringVar()
        self.save_entry_text.set(self._set_variable("save_entry_text"))
        
        self.save_selected = ttk.Entry(directory_frame, text=self.save_entry_text, width=70, state='readonly')
        self.save_selected.grid(row=1, column=1, padx=10, pady=10)

        self.save_button = ttk.Button(directory_frame, text="...", command=lambda: self._get_directory("save_button"), bootstyle="secondary")
        self.save_button.grid(row=1, column=2, padx=10, pady=10)

        # Confirm button
        button_frame = tb.Frame(self.root, bootstyle="default")
        button_frame.columnconfigure(0, weight=1)
        button_frame.grid(row=1, column=0, padx=5)

        self.confirm_button = tb.Button(directory_frame, text="OK", command=self._src_confirm)
        self.confirm_button.grid(row=2, column=2, padx=10, pady=10, sticky=tk.E)

    def get_input(self):
        return {"src_dir": self.src_dir, "save_dir": self.save_dir}


if __name__ == "__main__":
    w = SourceGUI()
    input = w.get_input()
    print("Will start selection window with source directory "+ input["src_dir"] + " and saving directory " + input["save_dir"])