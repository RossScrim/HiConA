import json
import csv


class JSONReader:
    def __init__(self, config_file):
        with open(config_file, 'r') as file:
            self.config = json.load(file)

    def get_config(self):
        return self.config

class OperaExperimentConfigReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.json_data = None

    def load_json_from_txt(self, remove_first_lines=0, remove_last_lines=0):
        """
        Loads a .txt file as JSON, optionally removing the specified number of lines from the beginning and end.

        Args:
            remove_first_lines (int): The number of lines to remove from the beginning.
            remove_last_lines (int): The number of lines to remove from the end.

        Returns:
            dict: The parsed JSON data as a dictionary, or None if an error occurs.
        """

        try:
            with open(self.file_path, 'r') as f:
                text = f.read()

            lines = text.splitlines()
            lines = lines[remove_first_lines:-remove_last_lines]
            json_text = '\n'.join(lines)

            self.json_data = json.loads(json_text)
            return self.json_data

        except FileNotFoundError:
            print(f"File '{self.file_path}' not found.")
            return None

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None

    def get_config(self):
        return self.json_data


if __name__ == "__main__":
    opera_config = OperaExperimentConfigReader("../88651da0-9ab0-4728-816f.kw.txt")
    opera_config_file = opera_config.load_json_from_txt(remove_first_lines=1, remove_last_lines=2)
    print(opera_config_file)
