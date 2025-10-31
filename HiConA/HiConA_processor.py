import tifffile
import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
from tkinter import messagebox, Scrollbar, Canvas
from tkinter.filedialog import askdirectory, askopenfilename
import re
import os
import json

from ConfigReader import OperaExperimentConfigReader
from FileManagement import FilePathHandler
from ImageProcessing import ImageProcessor
from StitchingImageJ import StitchProcessing
from CellposeSegmentation import cellpose_organiser
from ImageJAfterStitching import ImageJProcessor

class HiConAProcessor:
    def __init__(self, measurements_to_process, selected_processes):
        pass