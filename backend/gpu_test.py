import torch

if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

x = torch.randn(10, 10).to(device)
print(x)
