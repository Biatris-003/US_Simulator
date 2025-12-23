from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        
    def plot_image(self, image, title, vmin=-60, vmax=0):
        self.fig.clear()
        # Re-add subplot
        ax = self.fig.add_subplot(111)
        
        if image is not None:
            im = ax.imshow(image, cmap='gray', vmin=vmin, vmax=vmax, aspect='auto')
            ax.set_title(title, fontweight='bold')
            ax.set_xlabel("Lateral")
            ax.set_ylabel("Depth")
            self.fig.colorbar(im, ax=ax, label="dB")
        
        self.draw()

    def plot_comparison(self, img_fund, img_harm):
        self.fig.clear()
        
        # Fund
        ax1 = self.fig.add_subplot(121)
        if img_fund is not None:
            im1 = ax1.imshow(img_fund, cmap='gray', vmin=-60, vmax=0, aspect='auto')
            ax1.set_title("Fundamental", fontweight='bold')
            ax1.set_xlabel("Lateral")
            ax1.set_ylabel("Depth")
        
        # Harm
        ax2 = self.fig.add_subplot(122)
        if img_harm is not None:
            im2 = ax2.imshow(img_harm, cmap='gray', vmin=-60, vmax=0, aspect='auto')
            ax2.set_title("Harmonic", fontweight='bold')
            ax2.set_xlabel("Lateral")
            ax2.set_yticks([]) # Hide Y
            
            # Shared colorbar
            cbar = self.fig.colorbar(im2, ax=[ax1, ax2], fraction=0.046, pad=0.04)
            cbar.set_label("dB")
            
        self.draw()