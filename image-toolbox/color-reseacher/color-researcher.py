import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import cv2
import numpy as np
import sys

class ColorReacherApp:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Color Reacher App")
        
        # Load the image using OpenCV
        self.original_image = cv2.imread(image_path)
        self.filtered_image = self.original_image.copy()
        self.h_min, self.h_max = 0, 179
        self.s_min, self.s_max = 0, 255
        self.v_min, self.v_max = 0, 255
        
        # UI Layout
        self.create_widgets()
        self.update_filtered_image()

    def create_widgets(self):
        # Left Upper - HSV Range Sliders
        control_frame = ttk.LabelFrame(self.root, text="HSV Controls")
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # H Range Slider
        self.hue_slider = self.create_slider(control_frame, "Hue", 0, 179, self.on_slider_change)
        # S Range Slider
        self.sat_slider = self.create_slider(control_frame, "Saturation", 0, 255, self.on_slider_change)
        # V Range Slider
        self.val_slider = self.create_slider(control_frame, "Value", 0, 255, self.on_slider_change)
        
        # Left Lower - Empty Frame (Placeholder)
        placeholder_frame = ttk.Frame(self.root, width=200, height=200)
        placeholder_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Right Upper - Original Image Preview
        self.original_image_label = ttk.Label(self.root, text="Original Image")
        self.original_image_label.grid(row=0, column=1, padx=10, pady=10)
        self.original_image_canvas = tk.Label(self.root)
        self.original_image_canvas.grid(row=0, column=2, padx=10, pady=10)
        self.display_image(self.original_image, self.original_image_canvas)

        # Right Lower - Filtered Image Preview
        self.filtered_image_label = ttk.Label(self.root, text="Filtered Image")
        self.filtered_image_label.grid(row=1, column=1, padx=10, pady=10)
        self.filtered_image_canvas = tk.Label(self.root)
        self.filtered_image_canvas.grid(row=1, column=2, padx=10, pady=10)
        
    def create_slider(self, parent, text, from_, to, command):
        label = ttk.Label(parent, text=text)
        label.pack()
        slider = ttk.Scale(parent, from_=from_, to=to, orient="horizontal", command=command)
        slider.pack(fill="x", padx=5, pady=5)
        return slider

    def on_slider_change(self, event):
        self.h_min = int(self.hue_slider.get())
        self.s_min = int(self.sat_slider.get())
        self.v_min = int(self.val_slider.get())
        self.update_filtered_image()

    def update_filtered_image(self):
        # Convert original image to HSV
        hsv_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
        # Define the range for HSV filtering
        lower_bound = np.array([self.h_min, self.s_min, self.v_min])
        upper_bound = np.array([self.h_max, self.s_max, self.v_max])
        # Apply the mask
        mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
        filtered = cv2.bitwise_and(self.original_image, self.original_image, mask=mask)
        self.filtered_image = filtered
        # Display the filtered image
        self.display_image(self.filtered_image, self.filtered_image_canvas)

    def display_image(self, image, canvas):
        # Resize the image to fit the canvas
        image_resized = cv2.resize(image, (300, 300))
        # Convert color from BGR to RGB
        image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
        # Convert to PhotoImage format using OpenCV
        image_tk = tk.PhotoImage(data=cv2.imencode('.png', image_rgb)[1].tobytes())
        # Update the canvas
        canvas.image = image_tk
        canvas.configure(image=image_tk)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python color-reacher.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    root = tk.Tk()
    app = ColorReacherApp(root, image_path)
    root.mainloop()