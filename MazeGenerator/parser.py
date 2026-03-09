"""Module for parsing and validating maze configuration files."""

import os
from typing import Dict, Any, Tuple, Set


class Parser:
    """
    Parser for maze configuration files.

    Handles parameter reading, type conversion, and logical constraint
    checking, including minimum size for the '42' pattern and collision
    detection for entry/exit points. Supports '#' for comments.
    """

    def __init__(self, file_path: str):
        """
        Initialize the parser with the path to the config file.

        Args:
            file_path: Path to the configuration text file.
        """
        self.file_path: str = file_path
        self.raw_data: Dict[str, str] = {}
        self.validated_data: Dict[str, Any] = {}
        self.mandatory_keys: Set[str] = {
            'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE'
        }

    def parse(self) -> Dict[str, Any]:
        """
        Read the file and convert KEY=VALUE strings into a dictionary.

        Comments starting with # and empty lines are ignored.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            ValueError: If there are syntax errors in the file.

        Returns:
            Dictionary containing validated data.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"Configuration file '{self.file_path}' not found."
            )

        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Сначала убираем комментарии в конце строки, затем пробелы
                line = line.split('#')[0].strip()

                if not line:
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

        Raises:
            ValueError: If mandatory keys are missing or format is invalid.

        Returns:
            Dictionary with converted values.
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

            perfect_v = self.raw_data.get('PERFECT', 'false').lower()
            self.validated_data['perfect'] = (perfect_v == 'true')
            seed_val = self.raw_data.get('SEED', '42')
            self.validated_data['seed'] = int(seed_val)

        except (ValueError, TypeError, IndexError) as e:
            raise ValueError(
                f"Invalid data format (expected number/coordinates): {e}"
            )

        return self.validated_data

    def validate(self) -> bool:
        """
        Check logical rules: boundaries, min size, and collisions.

        Raises:
            ValueError: If parameters violate maze construction rules.

        Returns:
            True if validation is successful.
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
        x_off, y_off = (w - pat_w) // 2, (h - pat_h) // 2

        for name, (px, py) in [('Entry', d['entry']), ('Exit', d['exit'])]:
            if not (0 <= px < w and 0 <= py < h):
                raise ValueError(f"{name} {px, py} is out of bounds {w}x{h}.")

            # Проверка коллизии с паттерном "42"
            if (x_off <= px < x_off + pat_w and
                    y_off <= py < y_off + pat_h):
                if pattern_mask[py - y_off][px - x_off] == 1:
                    raise ValueError(
                        f"{name} {px, py} coincides with '42' pattern wall."
                    )

        if d['entry'] == d['exit']:
            raise ValueError("Entry and Exit points must be different.")
        return True

    def get_args(self) -> Tuple[int, int, Tuple[int, int],
                                Tuple[int, int], str, bool, int]:
        """
        Return a tuple of parameters for initializing MazeEngine.

        Returns:
            Tuple: (width, height, entry, exit, output_file, perfect, seed)
        """
        if not self.validated_data:
            self.parse()
        self.validate()

        d = self.validated_data
        return (
            d['width'], d['height'], d['entry'], d['exit'],
            d['output_file'], d['perfect'], d['seed']
        )
