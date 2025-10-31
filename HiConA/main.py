from HiConA_processor import HiConAProcessor
from GUI_source_window import SourceGUI
from GUI_selection_window import SelectionGUI

def main():
    source_window = SourceGUI()
    source_input = source_window.get_input()
    print(source_input)

    selection_window = SelectionGUI(source_input)
    measurements, processes = selection_window.get_input()

    print(measurements)
    print(processes)

    HiConAProcessor(measurements, processes)

if __name__ == '__main__':
    main()