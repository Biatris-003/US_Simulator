from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *


class ProfilePlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.figure = Figure(figsize=(5, 4.5), facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_profiles(self, depth, fund, harm):
        self.ax.clear()
        
        self.ax.set_facecolor('#f8f9fa')
        self.figure.patch.set_facecolor('#ffffff')
        
        self.ax.plot(depth, fund, color='#3498db', linewidth=2.5, label='Fundamental', alpha=0.9)
        self.ax.plot(depth, harm, color='#e74c3c', linewidth=2.5, label='Harmonics', alpha=0.9)
        
        self.ax.axvline(3, color='#7f8c8d', linestyle='--', linewidth=1.5, alpha=0.7)
        
        self.ax.set_xlabel('Distance [cm]', fontsize=11, fontweight='600', color='#2c3e50')
        self.ax.set_ylabel('Signal Strength', fontsize=11, fontweight='600', color='#2c3e50')
        self.ax.set_title('Fundamental vs Harmonic Signal vs Depth', 
                         fontweight='bold', fontsize=12, color='#2c3e50', pad=15)
        
        legend = self.ax.legend(loc='upper right', frameon=True, shadow=True, 
                               fancybox=True, fontsize=10)
        legend.get_frame().set_facecolor('#ffffff')
        legend.get_frame().set_edgecolor('#bdc3c7')
        legend.get_frame().set_linewidth(1.5)
        
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#95a5a6', linewidth=0.8)
        
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#bdc3c7')
            spine.set_linewidth(1.5)
        
        self.ax.tick_params(colors='#34495e', labelsize=9)
        
        self.figure.tight_layout()
        self.canvas.draw()