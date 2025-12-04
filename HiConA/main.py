import ttkbootstrap as tb
from GUI.GUI_HiConA import HiConAGUI
from Backend.HiConAWorkFlowHandler import HiConAWorkflowHandler

def main():
    root = tb.Window(themename="lumen", title="HiConA")
    root.geometry("1400x950")
    root.bind_all("<MouseWheel>")
    HiConA = HiConAGUI(root)
    root.mainloop()

    all_files, all_xml_files, processes, output_dir = HiConA.get_input()

    for measurement_id in all_files.keys():
        print("Processing measurement ID:", measurement_id)
        HiConAWorkflowHandler(all_files[measurement_id], processes, output_dir).run()

if __name__ == '__main__':
    main()