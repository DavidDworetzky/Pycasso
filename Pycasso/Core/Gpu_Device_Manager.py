import torch
class Gpu_Device_Manager():
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    def get_device(self):
        return "cuda" if torch.cuda.is_available() else "cpu"



