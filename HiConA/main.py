import ttkbootstrap as tb

from HiConA.Backend.HiConAWorkFlowHandler import HiConAWorkflowHandler
from HiConA.Backend.ImageJ_singleton import ImageJSingleton
from HiConA.Utilities.ConfigReader import ConfigReader

from HiConA.GUI.GUI_HiConA import HiConAGUI

def main():
    """
    Calling HiConA GUI and HiConA Workflow Handler to process archived Opera Phenix data.
    """

    # Initialise root window
    root = tb.Window(themename="lumen", title="HiConA")
    root.geometry("1600x950")
    root.bind_all("<MouseWheel>")
    # Iniate GUI for user selection
    HiConA = HiConAGUI(root)
    root.mainloop()

    # Get selected measurements for processing, together with their xml_readers, which processes to run and the output directory for where to save processed data.
    all_files, all_xml_readers, processes, output_dir = HiConA.get_input()

    print("Processing started!")

    # Process each meaurement
    for measurement_id in all_files.keys():
        HiConAWorkflowHandler(all_xml_readers[measurement_id], all_files[measurement_id], processes, output_dir).run()
    
    print("Processing finished!")
    
    # Dispose of ImageJ instance
    ImageJSingleton.dispose()



if __name__ == '__main__':
    main()