import torch
print(("cpu","cuda")[torch.cuda.is_available()])