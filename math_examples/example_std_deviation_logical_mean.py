import numpy as np
import pandas as pd

# Generate a sample dataset (random grayscale pixel values)
np.random.seed(42)  # Ensures reproducibility
data = np.random.randint(0, 256, size=100)  # 100 pixel values (0-255)

# Reshape into a 10x10 "bingo card" format
reshaped_data = data.reshape(10, 10)

# Normalize to range [0,1]
# Python is new and different to me, 
# This divides each element in table by 255 and keeps data shape
normalized_data = reshaped_data / 255.0

# Compute statistics
mean_value = np.mean(normalized_data)
mean_deviation = np.mean(np.abs(normalized_data - mean_value))
std_deviation = np.std(normalized_data)

# Print normalized data as a table
print("\nNormalized Pixel Data (10x10 Grid):")
df = pd.DataFrame(normalized_data)
print(df.round(3).to_string(index=False, header=False))  # Clean table format

# Print computed statistics
print("\nStatistics:")
print(f"Mean (Normalized): {mean_value:.4f}")
print(f"Mean Deviation (MAD): {mean_deviation:.4f}")
print(f"Standard Deviation: {std_deviation:.4f}")
