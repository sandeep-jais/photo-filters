import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageOps

def resize_image(image_path, size=(100, 100)):
    image = Image.open(image_path)

    # Convert image to RGBA if it's in P mode (palette)
    if image.mode == 'P':
        image = image.convert('RGBA')
    
    if image.mode == 'L':
        image = image.convert('RGB')
    
    # Add a white background and resize
    image_with_background = ImageOps.expand(image, border=0, fill='white')
    image_resized = image_with_background.resize(size)
    return image_resized

# Convert PIL image to QPixmap for PyQt5
def pil_to_pixmap(pil_image):
    data = pil_image.tobytes("raw", "RGBA")
    qimage = QImage(data, pil_image.size[0], pil_image.size[1], QImage.Format_ARGB32)
    pixmap = QPixmap.fromImage(qimage)
    return pixmap

class LogoWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Define the layout
        self.setWindowTitle('All-In-One Filters')
        self.setGeometry(100, 100, 300, 200)

        main_layout = QHBoxLayout()


        # Define the images and python files mapping
        self.python_scripts = {
            'basic_logo.png': 'basicFilters.py',
            'insta_logo.png': 'instaFilters.py',
            'apple_logo.png': 'iphoneFilters.py'
        }

        # Create labels for each image
        self.apple_logo = QLabel(self)
        self.insta_logo = QLabel(self)
        self.basic_logo = QLabel(self)

        # Create labels for text
        self.apple_label = QLabel('Apple Filters', alignment=Qt.AlignCenter)
        self.insta_label = QLabel('Instagram Filters', alignment=Qt.AlignCenter)
        self.basic_label = QLabel('Basic Filters', alignment=Qt.AlignCenter)

        # Set the images
        self.set_image(self.basic_logo, 'basic_logo.png')
        self.set_image(self.insta_logo, 'insta_logo.png')
        self.set_image(self.apple_logo, 'apple_logo.png')

        # Create vertical layouts for each image and label

        basic_layout = QVBoxLayout()
        basic_layout.addWidget(self.basic_logo)
        basic_layout.addWidget(self.basic_label)

        insta_layout = QVBoxLayout()
        insta_layout.addWidget(self.insta_logo)
        insta_layout.addWidget(self.insta_label)

        apple_layout = QVBoxLayout()
        apple_layout.addWidget(self.apple_logo)
        apple_layout.addWidget(self.apple_label)

        # Add vertical layouts to the main horizontal layout
        main_layout.addLayout(basic_layout)
        main_layout.addLayout(insta_layout)
        main_layout.addLayout(apple_layout)

        self.setLayout(main_layout)

    def set_image(self, label, image_path):
        resized_image = resize_image(image_path, size=(100, 100))
        pixmap = pil_to_pixmap(resized_image)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        label.mousePressEvent = lambda event, path=image_path: self.run_python_script(path)

    def run_python_script(self, image_path):
        script_path = self.python_scripts.get(image_path)
        if script_path:
            subprocess.run(['python3', script_path])
        else:
            print(f"Script for {image_path} not found.")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = LogoWindow()
    window.show()

    sys.exit(app.exec_())
