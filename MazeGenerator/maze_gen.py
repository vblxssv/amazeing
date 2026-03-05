from abc import ABC, abstractmethod


class IGenAlgorithm(ABC):
    @abstractmethod
    def generate(self, width: int, height: int, entry: tuple[int, int],
                 exit: tuple[int, int], seed: int):
        pass


class PerfectMazeGen(IGenAlgorithm):
    def generate(self, width, height, entry, exit, seed):
        pass


class NonPerfectMazeGen(IGenAlgorithm):
    def generate(self, width, height, entry, exit, seed):
        pass


class MazeGen:
    def __init__(self, width: int, height: int, entry: tuple[int, int],
                 exit: tuple[int, int], output_file: str, perfect: bool,
                 seed: int):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.seed = seed
        if perfect:
            self.algorithm = PerfectMazeGen()
        else:
            self.algorithm = NonPerfectMazeGen()

    
    
