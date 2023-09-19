import cv2
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor
import glob
import itertools
from collections import Counter

def load_and_resize_image(image_path, size):
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        return cv2.resize(image, (size, size))
    except Exception as e:
        return None

def find_best_match(segment, element_images, used_blocks_counts, penalty):
    segment = segment.astype(np.float32)
    abs_diffs = np.mean(np.abs(segment - element_images), axis=(1, 2, 3))


    for index in range(len(element_images)):
        abs_diffs[index] += used_blocks_counts[index] * penalty

    best_match_index = np.argmin(abs_diffs)
    best_match = element_images[best_match_index]
    best_match_difference = abs_diffs[best_match_index]
    used_blocks_counts[best_match_index] += 1
    return best_match, best_match_difference != float("inf")

def create_photomosaic(source_image_path, blocks_folder, segment_size, image_size, brightness, penalty):
    img = cv2.imread("media/"+source_image_path)
    resized = cv2.resize(img, image_size)

    img_contrast = cv2.convertScaleAbs(resized, alpha=brightness, beta=0.9)
    mg_detail = cv2.detailEnhance(img_contrast, sigma_s=20, sigma_r=10)
    mg_detail = cv2.detailEnhance(mg_detail, sigma_s=20, sigma_r=10)
    source_image = mg_detail
    element_image_paths = glob.glob(os.path.join(blocks_folder, "*"))
    with ThreadPoolExecutor() as executor:
        element_images = list(executor.map(lambda p: load_and_resize_image(p, segment_size), element_image_paths))

    height, width = source_image.shape[:2]
    num_segments_y = height // segment_size
    num_segments_x = width // segment_size

    replaced_blocks = 0
    mosaic_image = np.zeros_like(source_image)
    used_blocks_counts = Counter()

    for i, j in itertools.product(range(num_segments_y), range(num_segments_x)):
        segment = source_image[i * segment_size: (i + 1) * segment_size, j * segment_size: (j + 1) * segment_size]
        best_match, was_replaced = find_best_match(segment, element_images, used_blocks_counts, penalty)
        mosaic_image[i * segment_size: (i + 1) * segment_size, j * segment_size: (j + 1) * segment_size] = best_match
        replaced_blocks += was_replaced

    return mosaic_image, replaced_blocks

"""penalty - штрафы для повторяющихся сегментов, чем больше тем равномернее распределение, но возможны артефакты
    default 0.025-0.1 """

def generate_mosaics(image_path, blocks_folders, segment_size, image_size, brightness=0.9, penalty=0.025):
    mosaics = []
    for blocks_folder in blocks_folders:
        mosaic, _ = create_photomosaic(image_path, blocks_folder, segment_size, image_size, brightness, penalty)
        mosaics.append(mosaic)
    return mosaics
