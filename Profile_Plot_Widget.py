from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *


class ProfilePlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.figure = Figure(figsize=(5, 4.5))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_profiles(self, depth, fund, harm):
        self.ax.clear()
        self.ax.set_facecolor('#fafafa')
        self.figure.patch.set_facecolor('#ffffff')
        self.ax.plot(depth, fund, 'b', linewidth=3, label='Fundamental')
        self.ax.plot(depth, harm, 'r', linewidth=3, label='Harmonics')
        self.ax.axvline(3, color='k', linestyle='--', linewidth=1)
        self.ax.set_xlabel('Distance [cm]', fontsize=10)
        self.ax.set_ylabel('Signal Strength', fontsize=10)
        self.ax.set_title('Fundamental vs Harmonic Signal vs Depth', fontweight='bold')
        self.ax.legend()
        self.ax.grid(True, linestyle='--', alpha=0.4)
        self.canvas.draw()