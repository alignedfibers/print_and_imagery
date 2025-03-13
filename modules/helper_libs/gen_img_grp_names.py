import os
import collections
import mimetypes
from pathlib import Path
import cv2  # OpenCV for SIFT features
import numpy as np
from sentence_transformers import SentenceTransformer  # Lightweight CLIP alternative
from sklearn.cluster import KMeans

# Set up a lightweight text model for keyword extraction
model = SentenceTransformer('all-MiniLM-L6-v2')  # Small and CPU-friendly

def extract_sift_features(image_path):
    """Extracts lightweight SIFT features from an image for fast keyword matching."""
    try:
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            return []
        sift = cv2.SIFT_create()
        keypoints, descriptors = sift.detectAndCompute(img, None)
        return descriptors if descriptors is not None else []
    except Exception as e:
        print(f"⚠️ Error processing {image_path}: {e}")
        return []

def get_keywords_from_descriptors(descriptor_list, num_clusters=5):
    """Clusters image descriptors and converts them into simple feature words."""
    if len(descriptor_list) == 0:
        return []
    descriptors = np.vstack(descriptor_list)
    kmeans = KMeans(n_clusters=min(num_clusters, len(descriptors)), n_init=10)
    kmeans.fit(descriptors)
    return [f"feature_{i}" for i in range(len(kmeans.cluster_centers_))]

def generate_group_name(dest_dir, max_chars=32):
    """Generates a short descriptive name for a group based on sampled images."""
    image_files = [p for p in Path(dest_dir).glob("*.jpg") if mimetypes.guess_type(p)[0] and "image" in mimetypes.guess_type(p)[0]]
    
    if not image_files:
        return "empty_folder"

    # Sample every 5th image
    sampled_images = image_files[::5] if len(image_files) > 5 else image_files
    
    descriptor_list = [extract_sift_features(img) for img in sampled_images if extract_sift_features(img)]

    # Extract common keywords
    keywords = get_keywords_from_descriptors(descriptor_list)

    # Count occurrences and select most frequent
    keyword_counts = collections.Counter(keywords)
    sorted_keywords = sorted(keyword_counts.keys(), key=lambda k: -keyword_counts[k])

    # Create group name
    name = "_".join(sorted_keywords)[:max_chars].strip("_")
    return name if name else "unknown"
