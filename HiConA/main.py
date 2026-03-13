import ttkbootstrap as tb

from HiConA.Utilities.bootstrap import setup_env
from HiConA.Utilities.OSEnvironmentalSetup import EnviromentalSetup
from HiConA.Backend.HiConAWorkFlowHandler import HiConAWorkflowHandler
from HiConA.Backend.ImageJ_singleton import ImageJSingleton
from HiConA.Utilities.ConfigReader import ConfigReader

from HiConA.GUI.GUI_HiConA import HiConAGUI


def main():
    "runs setup env is for JAVA"
    setup_env()
    system_config = EnviromentalSetup().system_config

    root = tb.Window(themename="lumen", title="HiConA")
    root.geometry("1600x950")
    root.bind_all("<MouseWheel>")
    HiConA = HiConAGUI(root)
    root.mainloop()

    all_files, all_xml_readers, processes, output_dir = HiConA.get_input()

    print("Processing started!")

    for measurement_id in all_files.keys():
        HiConAWorkflowHandler(all_xml_readers[measurement_id], all_files[measurement_id],
                              processes, output_dir, system_config).run()
    print("Processing finished!")
    ImageJSingleton.dispose()

if __name__ == '__main__':
    main()
