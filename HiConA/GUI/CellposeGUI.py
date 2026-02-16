class CellposeGUI:
    """GUI, getting input from user to run Opera processing."""

    def __init__(self):
        self.root = tk.Tk()

        # self.root.geometry("800x150")
        self.root.title("Stitching")

        # Choose directories
        self.directoryframe = tk.Frame(self.root)
        self.directoryframe.columnconfigure(0, weight=1)
        self.directoryframe.columnconfigure(1, weight=1)
        self.directoryframe.columnconfigure(2, weight=1)

        self.src_label = ttk.Label(self.directoryframe, text="Measurement Directory", font=("Segoe UI", 14))
        self.src_label.grid(row=0, column=0, padx=10, pady=10)

        self.src_entry_text = tk.StringVar()
        self.src_selected = ttk.Entry(self.directoryframe, text=self.src_entry_text, width=70, state='readonly')
        self.src_selected.grid(row=0, column=1, padx=10, pady=10)

        self.src_button = ttk.Button(self.directoryframe, text="...", command=lambda: self.get_directory("src_button"))
        self.src_button.grid(row=0, column=2, padx=10, pady=10)

        self.seg_ch_var = tk.IntVar()
        seg_ch_label = ttk.Label(self.directoryframe, text="Segmentation channel number:")
        seg_ch_label.grid(row=1, column=0, sticky=tk.EW, padx=10, pady=10)
        self.seg_ch_entry = ttk.Entry(self.directoryframe, text=self.seg_ch_var, width=2, background='White').grid(
            row=1, column=1, sticky=tk.EW)

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
            src_dir = askdirectory(title="Choose the directory for measurement to be processed")
            self.src_entry_text.set(src_dir)

    def src_confirm(self):
        """Checks the choices have been made for directories and processing steps. """
        if self.src_entry_text.get() == "":
            messagebox.showinfo(title="Missing Information",
                                message="Please choose the directory for the measurement to be processed.")
        elif self.seg_ch_var.get() == 0 or not isinstance(self.seg_ch_var.get(), int):
            messagebox.showinfo(title="Please enter which channel should be used for the segmentation.")
        else:
            self.src_dir = self.src_entry_text.get()
            self.seg_ch = self.seg_ch_var.get()
            self.root.destroy()

    def get_parameters(self):
        return self.src_dir, self.seg_ch