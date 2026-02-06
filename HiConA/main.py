import ttkbootstrap as tb

from HiConA.Backend.HiConAWorkFlowHandler import HiConAWorkflowHandler
from HiConA.Backend.ImageJ_singleton import ImageJSingleton
from Utilities.ConfigReader import ConfigReader

from HiConA.GUI.GUI_HiConA import HiConAGUI


def main():
    root = tb.Window(themename="lumen", title="HiConA")
    root.geometry("1600x950")
    root.bind_all("<MouseWheel>")
    HiConA = HiConAGUI(root)
    root.mainloop()

    all_files, all_xml_readers, processes, output_dir = HiConA.get_input()

    print("Processing started!")

    for measurement_id in all_files.keys():
        #config_file = ConfigReader(all_files[measurement_id].archived_data_config).load(remove_first_lines=1, remove_last_lines=2)
        #if config_file is not None:
        #    print(config_file["PLATENAME"])

        #print("Processing measurement ID:", measurement_id)
        #print(all_files[measurement_id])
        #print(processes)
        HiConAWorkflowHandler(all_xml_readers[measurement_id], all_files[measurement_id], processes, output_dir).run()

    print("Processing finished!")
    ImageJSingleton.dispose()

if __name__ == '__main__':
    main()