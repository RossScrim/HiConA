import ttkbootstrap as tb

from HiConA.Backend.HiConAWorkFlowHandler import HiConAWorkflowHandler
from Utilities.ConfigReader import ConfigReader

from GUI.GUI_HiConA import HiConAGUI



def main():
    root = tb.Window(themename="lumen", title="HiConA")
    root.geometry("1400x950")
    root.bind_all("<MouseWheel>")
    HiConA = HiConAGUI(root)
    root.mainloop()

    all_files, all_xml_readers, processes, output_dir = HiConA.get_input()

    for measurement_id in all_files.keys():
        config_file = ConfigReader(all_files[measurement_id].archived_data_config).load(remove_first_lines=1, remove_last_lines=2)
        if config_file is not None:
            print(config_file["PLATENAME"])

        print("Processing measurement ID:", measurement_id)
        print(all_files[measurement_id])
        print(processes)
        HiConAWorkflowHandler(all_xml_readers[measurement_id], all_files[measurement_id], processes, output_dir).run()


if __name__ == '__main__':
    main()