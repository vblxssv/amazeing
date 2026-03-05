import os

class Parser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_data = {}
        self.validated_data = {}
        self.mandatory_keys = {'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE'}

    def parse(self):
        """Считывает файл и сохраняет сырые строки."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Файл {self.file_path} не найден.")

        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    raise ValueError(f"Ошибка синтаксиса в строке {line_num}: нет '='")
                
                key, value = line.split('=', 1)
                self.raw_data[key.strip().upper()] = value.strip()
        
        return self._convert_types()

    def _convert_types(self):
        """Преобразует строки в объекты Python (int, tuple, bool)."""
        missing = self.mandatory_keys - set(self.raw_data.keys())
        if missing:
            raise ValueError(f"Отсутствуют ключи: {', '.join(missing)}")

        try:
            self.validated_data = {
                'width': int(self.raw_data['WIDTH']),
                'height': int(self.raw_data['HEIGHT']),
                'entry': tuple(map(int, self.raw_data['ENTRY'].split(','))),
                'exit': tuple(map(int, self.raw_data['EXIT'].split(','))),
                'output_file': self.raw_data['OUTPUT_FILE'],
                'perfect': self.raw_data.get('PERFECT', 'False').lower() == 'true'
            }
        except Exception as e:
            raise ValueError(f"Ошибка в формате данных: {e}")
        return self.validated_data

    def validate(self):
        """Проверяет логику (границы, размеры, совпадение точек)."""
        d = self.validated_data
        
        # 1. Проверка минимальных размеров
        if d['width'] < 2 or d['height'] < 2:
            raise ValueError("Размер лабиринта слишком мал (минимум 2x2).")
        
        # 2. Проверка границ
        for name, (x, y) in [('Вход', d['entry']), ('Выход', d['exit'])]:
            if not (0 <= x < d['width'] and 0 <= y < d['height']):
                raise ValueError(f"{name} {x,y} вне границ {d['width']}x{d['height']}.")
        
        # 3. Проверка на совпадение входа и выхода
        if d['entry'] == d['exit']:
            raise ValueError(f"Точки входа и выхода совпадают {d['entry']}. Они должны быть разными.")
            
        return True

    def get_args_tuple(self):
        """Возвращает кортеж параметров для MazeGenerator."""
        self.parse()
        self.validate()
        
        d = self.validated_data
        return (
            d['width'],
            d['height'],
            d['entry'],
            d['exit'],
            d['output_file'],
            d['perfect']
        )
