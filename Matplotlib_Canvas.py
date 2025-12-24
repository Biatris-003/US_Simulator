from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='white')
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        
    def plot_image(self, image, title, vmin=-60, vmax=0):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        if image is not None:
            im = ax.imshow(image, cmap='gray', vmin=vmin, vmax=vmax, aspect='auto')
            ax.set_title(title, fontweight='bold', fontsize=12, color='#2c3e50', pad=10)
            ax.set_xlabel("Lateral", fontsize=10, fontweight='600', color='#34495e')
            ax.set_ylabel("Depth", fontsize=10, fontweight='600', color='#34495e')
            
            cbar = self.fig.colorbar(im, ax=ax, label="dB")
            cbar.set_label("dB", fontsize=10, fontweight='600', color='#34495e')
            cbar.ax.tick_params(labelsize=9, colors='#34495e')
            
            for spine in ax.spines.values():
                spine.set_edgecolor('#bdc3c7')
                spine.set_linewidth(1.5)
            
            ax.tick_params(colors='#34495e', labelsize=9)
        
        self.fig.tight_layout()
        self.draw()

    def plot_comparison(self, img_fund, img_harm):
        self.fig.clear()
        
        self.fig.subplots_adjust(left=0.08, right=0.88, wspace=0.15)
        
        # Fund
        ax1 = self.fig.add_subplot(121)
        if img_fund is not None:
            im1 = ax1.imshow(img_fund, cmap='gray', vmin=-60, vmax=0, aspect='auto')
            ax1.set_title("Fundamental", fontweight='bold', fontsize=12, 
                         color='#3498db', pad=10)
            ax1.set_xlabel("Lateral", fontsize=10, fontweight='600', color='#34495e')
            ax1.set_ylabel("Depth", fontsize=10, fontweight='600', color='#34495e')
            
         
            for spine in ax1.spines.values():
                spine.set_edgecolor('#bdc3c7')
                spine.set_linewidth(1.5)
            
            ax1.tick_params(colors='#34495e', labelsize=9)
        
        # Harm
        ax2 = self.fig.add_subplot(122)
        if img_harm is not None:
            im2 = ax2.imshow(img_harm, cmap='gray', vmin=-60, vmax=0, aspect='auto')
            ax2.set_title("Harmonic", fontweight='bold', fontsize=12, 
                         color='#e74c3c', pad=10)
            ax2.set_xlabel("Lateral", fontsize=10, fontweight='600', color='#34495e')
            ax2.set_yticks([]) # Hide Y
            

            for spine in ax2.spines.values():
                spine.set_edgecolor('#bdc3c7')
                spine.set_linewidth(1.5)
            
            ax2.tick_params(colors='#34495e', labelsize=9)
            

            cbar = self.fig.colorbar(im2, ax=[ax1, ax2], fraction=0.035, pad=0.08)
            cbar.set_label("dB", fontsize=10, fontweight='600', color='#34495e')
            cbar.ax.tick_params(labelsize=9, colors='#34495e')
            
        self.draw()