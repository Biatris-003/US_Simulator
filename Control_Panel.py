
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ControlPanel(QWidget): #to simulate&change parameters
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        sim_group = QGroupBox("Simulation Parameters")
        sim_layout = QGridLayout()
        
        #1.freq
        sim_layout.addWidget(QLabel("Fundamental Frequency:"), 0, 0)
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(10, 100)  # 1-10 MHz
        self.freq_slider.setValue(35)  # 3.5 MHz scaled
        self.freq_slider.setTickPosition(QSlider.TicksBelow)
        self.freq_slider.setTickInterval(1)
        sim_layout.addWidget(self.freq_slider, 0, 1)
        self.freq_label = QLabel("3.5 MHz")
        sim_layout.addWidget(self.freq_label, 0, 2)
        
        #2.bw
        sim_layout.addWidget(QLabel("Transmit Bandwidth:"), 1, 0)
        self.bw_slider = QSlider(Qt.Horizontal)
        self.bw_slider.setRange(20, 80)  # 20-80%
        self.bw_slider.setValue(60)
        sim_layout.addWidget(self.bw_slider, 1, 1)
        self.bw_label = QLabel("60%")
        sim_layout.addWidget(self.bw_label, 1, 2)
        
        #3. nl
        sim_layout.addWidget(QLabel("Nonlinear Coefficient:"), 2, 0)
        self.nl_slider = QSlider(Qt.Horizontal)
        self.nl_slider.setRange(20, 80)  # 0.2-0.8
        self.nl_slider.setValue(35)   #0.35
        sim_layout.addWidget(self.nl_slider, 2, 1)
        self.nl_label = QLabel("0.35")
        sim_layout.addWidget(self.nl_label, 2, 2)
        
        # #phantom_cysts
        sim_layout.addWidget(QLabel("Number of Cysts:"), 3, 0)
        self.cysts_slider = QSlider(Qt.Horizontal)
        self.cysts_slider.setRange(1, 5)
        self.cysts_slider.setValue(3)
        sim_layout.addWidget(self.cysts_slider, 3, 1)
        self.cysts_label = QLabel("3")
        sim_layout.addWidget(self.cysts_label, 3, 2)
        
        sim_group.setLayout(sim_layout)
        layout.addWidget(sim_group)
        
        button_layout = QHBoxLayout()
        self.simulate_btn = QPushButton("Run Simulation")
        self.simulate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        button_layout.addWidget(self.simulate_btn)
        layout.addLayout(button_layout)
        
        #progrss bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
        #updating labels based on sliderss
        self.freq_slider.valueChanged.connect(self.update_freq_label)
        self.bw_slider.valueChanged.connect(self.update_bw_label)
        self.nl_slider.valueChanged.connect(self.update_nl_label)
        self.cysts_slider.valueChanged.connect(self.update_cysts_label)
        
    def update_freq_label(self, value):
        freq = value / 10.0
        self.freq_label.setText(f"{freq:.1f} MHz")
        
    def update_bw_label(self, value):
        self.bw_label.setText(f"{value}%")
        
    def update_nl_label(self, value):
        nl_value = value / 100.0  
        self.nl_label.setText(f"{nl_value:.2f}")
         
    def update_cysts_label(self, value):
        self.cysts_label.setText(f"{value}")