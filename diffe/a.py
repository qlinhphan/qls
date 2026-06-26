import torch

# 1. Check if a CUDA-capable GPU is available
gpu_available = torch.cuda.is_available()
print(f"Is GPU available?: {gpu_available}")

if gpu_available:
    # 2. Get the number of available GPUs
    print(f"Number of GPUs: {torch.cuda.device_count()}")
    
    # 3. Get the ID of the current GPU
    print(f"Current GPU ID: {torch.cuda.current_device()}")
    
    # 4. Get the name of the GPU
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
