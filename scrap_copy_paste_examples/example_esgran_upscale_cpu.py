import torch
from PIL import Image
import numpy as np
from realesrgan import RealESRGAN
#from realesrgan import RealESRGANer

device = torch.device('cpu')

model = RealESRGAN(device, scale=4)
model.load_weights('RealESRGAN_x4.pth', download=True)

path_to_image = 'input_blkbg_2752732759.png'
image = Image.open(path_to_image).convert('RGB')

sr_image = model.predict(image)

sr_image.save('sr_image.png')