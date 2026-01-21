import cv2
import numpy as np
import os

class ImageProcessor:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.image = self._load_image()
        self.processed_images = {} 

    def _load_image(self) -> np.ndarray:
        """Private method to safely load image."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Image not found at: {self.file_path}")
        
        img = cv2.imread(self.file_path)
        if img is None:
            raise ValueError("Failed to read image data.")
        return img

    def get_metadata(self) -> dict:
        """Returns image dimensions and channel info."""
        height, width, channels = self.image.shape
        return {
            "height": height,
            "width": width,
            "channels": channels
        }

    def show_image(self, window_name: str, image: np.ndarray = None):
        """Displays image in a GUI window."""
        if image is None:
            image = self.image
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 320)
        cv2.imshow(window_name, image)

    def show_separate_channels(self):
        """Splits and displays individual B, G, R channels."""
        b, g, r = cv2.split(self.image)
        
        zeros = np.zeros(self.image.shape[:2], dtype="uint8")

        self.show_image("Channel - Blue", cv2.merge([b, zeros, zeros]))
        self.show_image("Channel - Green", cv2.merge([zeros, g, zeros]))
        self.show_image("Channel - Red", cv2.merge([zeros, zeros, r]))

    def swap_channels(self, order: str = "RGB") -> np.ndarray:
        b, g, r = cv2.split(self.image)
        
        if order == "RGB":
            swapped_img = cv2.merge([r, g, b])
        elif order == "GRB":
             swapped_img = cv2.merge([g, r, b])
        else:
            swapped_img = self.image

        self.processed_images['swapped'] = swapped_img
        return swapped_img

    def to_grayscale(self) -> np.ndarray:
        gray_img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.processed_images['grayscale'] = gray_img
        return gray_img

    def to_binary(self, threshold_val: int = 127) -> np.ndarray:
        if 'grayscale' not in self.processed_images:
            self.to_grayscale()
        
        _, binary_img = cv2.threshold(
            self.processed_images['grayscale'], 
            threshold_val, 
            255, 
            cv2.THRESH_BINARY
        )
        self.processed_images['binary'] = binary_img
        return binary_img

    def save_image(self, image: np.ndarray, output_path: str):
        cv2.imwrite(output_path, image)
        print(f"[System] Image saved successfully at: {output_path}")