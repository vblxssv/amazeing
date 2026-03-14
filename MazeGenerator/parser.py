import os
import sys
from typing import Any, Dict, List, Set, Tuple


class Parser:
    """Parser for maze configuration files."""

    def __init__(self, file_path: str) -> None:
        """
        Initialize the parser with a file path.

        Args:
            file_path: Path to the configuration file.
        """
        self.file_path: str = file_path
        self.raw_data: Dict[str, str] = {}
        self.validated_data: Dict[str, Any] = {}
        self.mandatory_keys: Set[str] = {
            "WIDTH",
            "HEIGHT",
            "ENTRY",
            "EXIT",
            "OUTPUT_FILE",
        }

    def parse(self) -> Dict[str, Any]:
        """
        Parse the configuration file and convert values to appropriate types.

        Returns:
            A dictionary containing validated maze parameters.

        Raises:
            FileNotFoundError: If the config file does not exist.
            ValueError: If there is a syntax error or missing keys.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"Configuration file '{self.file_path}' not found."
            )

        with open(self.file_path, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                clean_line: str = line.split("#")[0].strip()
                if not clean_line:
                    continue
                if "=" not in clean_line:
                    raise ValueError(
                        f"Syntax error at line {line_num}: missing '='"
                    )

                key, value = clean_line.split("=", 1)
                self.raw_data[key.strip().upper()] = value.strip()

        return self._convert_types()

    def _convert_types(self) -> Dict[str, Any]:
        """
        Internal method to convert raw string data to Python types.

        Returns:
            Dictionary with converted types.
        """
        missing_keys: Set[str] = (
            self.mandatory_keys - set(self.raw_data.keys())
        )
        if missing_keys:
            raise ValueError(
                f"Missing mandatory keys: {', '.join(missing_keys)}"
            )

        try:
            self.validated_data = {
                "width": int(self.raw_data["WIDTH"]),
                "height": int(self.raw_data["HEIGHT"]),
                "entry": tuple(map(int, self.raw_data["ENTRY"].split(","))),
                "exit": tuple(map(int, self.raw_data["EXIT"].split(","))),
                "output_file": self.raw_data["OUTPUT_FILE"],
            }
            perfect_v: str = self.raw_data.get("PERFECT", "false").lower()
            self.validated_data["perfect"] = perfect_v == "true"
            self.validated_data["seed"] = int(self.raw_data.get("SEED", "42"))
        except (ValueError, TypeError, IndexError) as error:
            raise ValueError(f"Invalid data format: {error}")

        return self.validated_data

    def validate(self) -> bool:
        """
        Validate the logic of the maze parameters.

        Returns:
            True if all checks pass.

        Raises:
            ValueError: If dimensions are invalid or points are out of bounds.
        """
        width: int = self.validated_data["width"]
        height: int = self.validated_data["height"]

        if width <= 0 or height <= 0:
            raise ValueError(
                f"Invalid maze dimensions: {width}x{height}. "
                "Dimensions must be positive integers."
            )

        if width * height < 2:
            raise ValueError(
                f"Maze size {width}x{height} is too small. "
                "Total cells must be at least 2 for distinct Entry/Exit."
            )

        pat_w, pat_h = 7, 5
        can_fit_pattern = width >= 9 and height >= 7

        if not can_fit_pattern:
            print(
                f"Error: Maze size {width}x{height} is too small. "
                f"'42' pattern will be omitted.", file=sys.stderr
            )

        points: List[Tuple[str, Tuple[int, int]]] = [
            ("Entry", self.validated_data["entry"]),
            ("Exit", self.validated_data["exit"]),
        ]

        for name, (px, py) in points:
            if not (0 <= px < width and 0 <= py < height):
                raise ValueError(
                    f"{name} ({px}, {py}) is out of bounds {width}x{height}."
                )

        if can_fit_pattern:
            pattern_mask = [
                [1, 0, 0, 0, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 1, 1],
            ]
            x_off = (width - pat_w) // 2
            y_off = (height - pat_h) // 2

            for name, (px, py) in points:
                if (x_off <= px < x_off + pat_w and
                        y_off <= py < y_off + pat_h):
                    if pattern_mask[py - y_off][px - x_off] == 1:
                        raise ValueError(
                            f"{name} ({px}, {py}) coincides with '42' pattern."
                        )

        if self.validated_data["entry"] == self.validated_data["exit"]:
            raise ValueError("Entry and Exit points must be different.")

        return True

    def get_args(self) -> Tuple[int, int, Tuple[int, int],
                                Tuple[int, int], str, bool, int]:
        """
        Perform parsing and validation, then return parameters as a tuple.

        Returns:
            Tuple: (width, height, entry, exit, output_file, perfect, seed)
        """
        if not self.validated_data:
            self.parse()
        self.validate()
        d = self.validated_data
        return (
            d["width"], d["height"], d["entry"], d["exit"],
            d["output_file"], d["perfect"], d["seed"]
        )
