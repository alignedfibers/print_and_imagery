import torch

def inspect_model(path):
    print(f"🔍 Inspecting model file: {path}")
    state = torch.load(path, map_location="cpu")

    print("\nTop-level keys:")
    for k in state.keys():
        print(" -", k)
    weights = state["params_ema"]   # Direct jump
    print("Count:", len(weights))
    for k, v in weights.items():
        print(k, v.shape)

model_path = "./models/RealESRGAN_x4plus_anime_6B.pth"
inspect_model(model_path)