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
        
        # 1. Patient Type
        grid.addWidget(QLabel("Patient Type:"), 0, 0)
        self.patient_combo = QComboBox()
        self.patient_combo.addItems(["Standard Patient", "Obese (High BMI)"])
        grid.addWidget(self.patient_combo, 0, 1, 1, 2)
        
        # 2. Frequency
        grid.addWidget(QLabel("Frequency (MHz):"), 1, 0)
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(20, 60) # 2.0 - 6.0
        self.freq_slider.setValue(35)
        grid.addWidget(self.freq_slider, 1, 1)
        self.freq_lbl = QLabel("3.5 MHz")
        grid.addWidget(self.freq_lbl, 1, 2)
        
        # 3. Nonlinear Coeff
        grid.addWidget(QLabel("Nonlinear Coeff:"), 2, 0)
        self.nl_slider = QSlider(Qt.Horizontal)
        self.nl_slider.setRange(10, 80)
        self.nl_slider.setValue(40)
        grid.addWidget(self.nl_slider, 2, 1)
        self.nl_lbl = QLabel("0.40")
        grid.addWidget(self.nl_lbl, 2, 2)
        
        # 4. Cysts
        grid.addWidget(QLabel("Num Cysts:"), 3, 0)
        self.cysts_slider = QSlider(Qt.Horizontal)
        self.cysts_slider.setRange(1, 5)
        self.cysts_slider.setValue(3)
        grid.addWidget(self.cysts_slider, 3, 1)
        self.cysts_lbl = QLabel("3")
        grid.addWidget(self.cysts_lbl, 3, 2)
        
        # 5. Pulse Inversion
        self.pi_check = QCheckBox("Pulse Inversion (Clean Harmonics)")
        self.pi_check.setChecked(False)
        grid.addWidget(self.pi_check, 4, 0, 1, 2)
        
        sim_group.setLayout(grid)
        layout.addWidget(sim_group)
        
        self.status = QLabel("Ready")
        self.status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status)
        
        self.setLayout(layout)
        
        # Label Connections
        self.freq_slider.valueChanged.connect(lambda v: self.freq_lbl.setText(f"{v/10:.1f} MHz"))
        self.nl_slider.valueChanged.connect(lambda v: self.nl_lbl.setText(f"{v/100:.2f}"))
        self.cysts_slider.valueChanged.connect(lambda v: self.cysts_lbl.setText(str(v)))