import json
from pathlib import Path

class ConfigReader:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.config = None

    def load(self):
        suffix = self.file_path.suffix.lower()

        try:
            if suffix == ".json":
                self.config = self._load_json()
            elif suffix == ".txt":
                self.config = self._load_json_from_txt()
            else:
                print(f"Skipping: Unsupported file type {suffix}")
                return None

            return self.config

        except (ValueError, json.JSONDecodeError) as e:
            # Instead of crashing, we log the error and return None
            print(f"Skipping dataset {self.file_path.name}: {e}")
            return None

    def _load_json(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    def _load_json_from_txt(self):
        with open(self.file_path, "r") as f:
            text = f.read()

        # Finding the first '{'
        first_bracket = text.find('{')
        last_bracket = text.rfind('}')

        if first_bracket == -1 or last_bracket == -1:
            raise ValueError("No JSON object found in the text file.")

        if first_bracket >= last_bracket:
            raise ValueError("Invalid structure: Opening bracket must come before the closing bracket.")

        try:
            json_text = text[first_bracket:last_bracket + 1]
            json_file = json.loads(json_text)  # Validate JSON format
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

        return json_file


if __name__ == "__main__":
    # Opera .txt JSON with header/footer
    opera_config = ConfigReader(r"C:\Users\rscrimgeour\PycharmProjects\HiConA\b1d444fb-e646-4659-9974.kw.txt").load()
    print(opera_config)
