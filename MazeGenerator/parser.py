import os
from typing import Dict, Any, Tuple


class Parser:
    """
    Class for parsing and validating the maze configuration file.
    Handles parameter reading, type conversion, and logical constraint
    checking, including minimum size for the '42' pattern and collision
    detection for entry/exit points.
    """

    def __init__(self, file_path: str):
        """
        Initialize the parser with the path to the config file.

        :param file_path: Path to the configuration text file.
        """
        self.file_path = file_path
        self.raw_data: Dict[str, str] = {}
        self.validated_data: Dict[str, Any] = {}
        self.mandatory_keys = {
            'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE'
        }

    def parse(self) -> Dict[str, Any]:
        """
        Read the file and convert KEY=VALUE strings into a Python dictionary.

        :raises FileNotFoundError: If the configuration file is not found.
        :raises ValueError: If there are syntax errors in the file.
        :return: Dictionary containing validated data.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"Configuration file '{self.file_path}' not found."
            )

        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    raise ValueError(
                        f"Syntax error at line {line_num}: missing '='"
                    )

                key, value = line.split('=', 1)
                self.raw_data[key.strip().upper()] = value.strip()

        return self._convert_types()

    def _convert_types(self) -> Dict[str, Any]:
        """
        Convert string values from the file into appropriate Python types.

        :raises ValueError: If mandatory keys are missing or format is invalid.
        """
        missing = self.mandatory_keys - set(self.raw_data.keys())
        if missing:
            raise ValueError(
                f"Missing mandatory keys in config: {', '.join(missing)}"
            )

        try:
            self.validated_data = {
                'width': int(self.raw_data['WIDTH']),
                'height': int(self.raw_data['HEIGHT']),
                'entry': tuple(map(int, self.raw_data['ENTRY'].split(','))),
                'exit': tuple(map(int, self.raw_data['EXIT'].split(','))),
                'output_file': self.raw_data['OUTPUT_FILE'],
            }

            perfect_val = self.raw_data.get('PERFECT', 'false').lower()
            self.validated_data['perfect'] = (perfect_val == 'true')
            seed_val = self.raw_data.get('SEED', '42')
            self.validated_data['seed'] = int(seed_val)

        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Invalid data format (expected number/coordinates): {e}"
            )

        return self.validated_data

    def validate(self) -> bool:
        """
        Check logical rules: boundaries, min size for '42', and collisions.

        :raises ValueError: If parameters violate maze construction rules.
        :return: True if validation is successful.
        """
        d = self.validated_data
        w, h = d['width'], d['height']

        if w < 9 or h < 7:
            raise ValueError(
                f"Maze size {w}x{h} is too small. "
                "Minimum 9x7 required for '42' pattern."
            )
        pattern_mask = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1]
        ]
        pat_w, pat_h = 7, 5
        x_offset = (w - pat_w) // 2
        y_offset = (h - pat_h) // 2

        for name, (px, py) in [('Entry', d['entry']), ('Exit', d['exit'])]:
            if not (0 <= px < w and 0 <= py < h):
                raise ValueError(f"{name} {px, py} is out of bounds {w}x{h}.")
            if (x_offset <= px < x_offset + pat_w and
                    y_offset <= py < y_offset + pat_h):
                local_x = px - x_offset
                local_y = py - y_offset
                if pattern_mask[local_y][local_x] == 1:
                    raise ValueError(
                        f"{name} {px, py} coincides with '42' pattern wall."
                    )

        if d['entry'] == d['exit']:
            raise ValueError("Entry and Exit points must be different.")

        return True

    def get_args_tuple(self) -> Tuple[int, int, Tuple[int, int],
                                      Tuple[int, int], str, bool, int]:
        """
        Return a tuple of parameters for initializing MazeGenerator.

        Order: (width, height, entry, exit, output_file, perfect, seed)
        """
        if not self.validated_data:
            self.parse()
        self.validate()

        d = self.validated_data
        return (
            d['width'],
            d['height'],
            d['entry'],
            d['exit'],
            d['output_file'],
            d['perfect'],
            d['seed']
        )
