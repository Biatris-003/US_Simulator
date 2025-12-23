from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        sim_group = QGroupBox("Simulation Parameters")
        grid = QGridLayout()
        
        # 1. Frequency
        grid.addWidget(QLabel("Frequency (MHz):"), 0, 0)
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(20, 60) # 2.0 - 6.0
        self.freq_slider.setValue(35)
        grid.addWidget(self.freq_slider, 0, 1)
        self.freq_lbl = QLabel("3.5 MHz")
        grid.addWidget(self.freq_lbl, 0, 2)
        
        # 2. Nonlinear Coeff
        grid.addWidget(QLabel("Nonlinear Coeff:"), 1, 0)
        self.nl_slider = QSlider(Qt.Horizontal)
        self.nl_slider.setRange(10, 80)
        self.nl_slider.setValue(40)
        grid.addWidget(self.nl_slider, 1, 1)
        self.nl_lbl = QLabel("0.40")
        grid.addWidget(self.nl_lbl, 1, 2)
        
        # 3. Pulse Inversion
        self.pi_check = QCheckBox("Pulse Inversion (Clean Harmonics)")
        self.pi_check.setChecked(False)
        self.pi_check.setToolTip("Enables Summation Gain (2x Signal, 1.4x Noise)")
        grid.addWidget(self.pi_check, 2, 0, 1, 2)
        
        sim_group.setLayout(grid)
        layout.addWidget(sim_group)
        
        self.status = QLabel("Ready")
        self.status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status)
        
        self.setLayout(layout)
        
        # Connections
        self.freq_slider.valueChanged.connect(lambda v: self.freq_lbl.setText(f"{v/10:.1f} MHz"))
        self.nl_slider.valueChanged.connect(lambda v: self.nl_lbl.setText(f"{v/100:.2f}"))