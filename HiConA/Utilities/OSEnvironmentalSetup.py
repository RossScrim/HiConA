import os
import platform
import torch
from torch import multiprocessing

class EnviromentalSetup:
    def __init__(self):
        self.system_OS = platform.system()
        self.GPU = self._check_gpu()
        self.python_vers = platform.python_version()
        self.cpu_cores = os.cpu_count()
        self.system_config = self._build_system_config()

    def _check_gpu(self):
        if self.system_OS == "Darwin":
            GPU_status = False
        else:
            GPU_status = torch.cuda.is_available()
        return GPU_status

    def _build_system_config(self):
        return dict(OS = self.system_OS, GPU =self.GPU,
                    python_version = self.python_vers, cpu_cores = self.cpu_cores)

if __name__ == "__main__":
    print(EnviromentalSetup().system_config)














































