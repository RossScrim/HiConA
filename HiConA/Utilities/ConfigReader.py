import json
from pathlib import Path

class ConfigReader:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.config = None

    def load(self, remove_first_lines=0, remove_last_lines=0):
        suffix = self.file_path.suffix.lower()

        if suffix == ".json":
            self.config = self._load_json()

        elif suffix == ".txt":
            self.config = self._load_json_from_txt(remove_first_lines, remove_last_lines)

        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        return self.config

    def _load_json(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    def _load_json_from_txt(self, remove_first_lines, remove_last_lines):
        with open(self.file_path, "r") as f:
            lines = f.read().splitlines()

        if remove_last_lines > 0:
            lines = lines[remove_first_lines:-remove_last_lines]
        else:
            lines = lines[remove_first_lines:]

        json_text = "\n".join(lines)
        return json.loads(json_text)


if __name__ == "__main__":
    # Opera .txt JSON with header/footer
    opera_config = ConfigReader("/88651da0-9ab0-4728-816f.kw.txt").load(remove_first_lines=1, remove_last_lines=2)
    print(opera_config)
