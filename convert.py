import cv2
import numpy as np

img = cv2.imread("image.jpeg").astype(np.float32)
img[...,0] *= 0.5   # reduce blue
img[...,1] *= 2.0   # boost green
img[...,2] *= 4.0   # boost red
img = np.clip(img, 0, 255).astype(np.uint8)
cv2.imwrite("corrected.jpg", img)

