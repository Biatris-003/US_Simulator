from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("Simulation Parameters")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        layout.addWidget(title)
        
        sim_group = QGroupBox()
        sim_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #ffffff;
                padding: 15px;
            }
        """)
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setContentsMargins(15, 20, 15, 15)
        
        # 1. Frequency - Vertical Slider
        freq_container = QVBoxLayout()
        freq_container.setSpacing(8)
        
        freq_label = QLabel("Frequency (MHz):")
        freq_label.setStyleSheet("QLabel { font-weight: 600; color: #34495e; font-size: 13px; }")
        freq_label.setAlignment(Qt.AlignCenter)
        freq_container.addWidget(freq_label)
        
        self.freq_lbl = QLabel("3.5 MHz")
        self.freq_lbl.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #3498db;
                font-size: 13px;
                min-width: 70px;
                padding: 5px;
                background: #ebf5fb;
                border-radius: 4px;
                qproperty-alignment: AlignCenter;
            }
        """)
        freq_container.addWidget(self.freq_lbl)
        
        self.freq_slider = QSlider(Qt.Vertical)
        self.freq_slider.setRange(20, 60) # 2.0 - 6.0
        self.freq_slider.setValue(35)
        self.freq_slider.setMinimumHeight(180)
        self.freq_slider.setInvertedAppearance(False)  
        self.freq_slider.setInvertedControls(True) 
        self.freq_slider.setStyleSheet("""
            QSlider::groove:vertical {
                border: 1px solid #bdc3c7;
                width: 8px;
                background: #ecf0f1;
                border-radius: 4px;
            }
            QSlider::handle:vertical {
                background: #3498db;
                border: 2px solid #2980b9;
                height: 18px;
                margin: 0 -6px;
                border-radius: 9px;
            }
            QSlider::handle:vertical:hover {
                background: #5dade2;
            }
        """)
        freq_container.addWidget(self.freq_slider, 0, Qt.AlignCenter)
        
        grid.addLayout(freq_container, 0, 0)
        
        # 2. Nonlinear Coeff - Vertical Slider
        nl_container = QVBoxLayout()
        nl_container.setSpacing(8)
        
        nl_label = QLabel("Nonlinear Coeff:")
        nl_label.setStyleSheet("QLabel { font-weight: 600; color: #34495e; font-size: 13px; }")
        nl_label.setAlignment(Qt.AlignCenter)
        nl_container.addWidget(nl_label)
        
        self.nl_lbl = QLabel("0.40")
        self.nl_lbl.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #e74c3c;
                font-size: 13px;
                min-width: 70px;
                padding: 5px;
                background: #fadbd8;
                border-radius: 4px;
                qproperty-alignment: AlignCenter;
            }
        """)
        nl_container.addWidget(self.nl_lbl)
        
        self.nl_slider = QSlider(Qt.Vertical)
        self.nl_slider.setRange(10, 80) #0.01 - 0.08
        self.nl_slider.setValue(40)
        self.nl_slider.setMinimumHeight(180)
        self.nl_slider.setInvertedAppearance(False)  
        self.nl_slider.setInvertedControls(True)  
        self.nl_slider.setStyleSheet("""
            QSlider::groove:vertical {
                border: 1px solid #bdc3c7;
                width: 8px;
                background: #ecf0f1;
                border-radius: 4px;
            }
            QSlider::handle:vertical {
                background: #e74c3c;
                border: 2px solid #c0392b;
                height: 18px;
                margin: 0 -6px;
                border-radius: 9px;
            }
            QSlider::handle:vertical:hover {
                background: #ec7063;
            }
        """)
        nl_container.addWidget(self.nl_slider, 0, Qt.AlignCenter)
        
        grid.addLayout(nl_container, 0, 1)
        
        # 3. Pulse Inversion
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout()
        checkbox_layout.setContentsMargins(0, 10, 0, 0)
        
        self.pi_check = QCheckBox("Pulse Inversion\n(Clean Harmonics)")
        self.pi_check.setChecked(False)
        self.pi_check.setToolTip("Enables Summation Gain (2x Signal, 1.4x Noise)")
        self.pi_check.setStyleSheet("""
            QCheckBox {
                font-weight: 600;
                color: #2c3e50;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #7f8c8d;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #27ae60;
                border: 2px solid #229954;
                image: url(none);
            }
            QCheckBox::indicator:checked:after {
                content: "✓";
            }
        """)
        checkbox_layout.addWidget(self.pi_check, 0, Qt.AlignCenter)
        checkbox_container.setLayout(checkbox_layout)
        grid.addWidget(checkbox_container, 1, 0, 1, 2)
        
        sim_group.setLayout(grid)
        layout.addWidget(sim_group)
        
        #status
        self.status = QLabel("Ready")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: 600;
                color: #27ae60;
                padding: 10px;
                background: #d5f4e6;
                border-radius: 6px;
                border: 1px solid #27ae60;
            }
        """)
        layout.addWidget(self.status)
        
        layout.addStretch()
        self.setLayout(layout)
        
        #sliders connect
        self.freq_slider.valueChanged.connect(lambda v: self.freq_lbl.setText(f"{v/10:.1f} MHz"))
        self.nl_slider.valueChanged.connect(lambda v: self.nl_lbl.setText(f"{v/100:.2f}"))
        
    def setStatusUpdating(self):
        self.status.setText("Updating...")
        self.status.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: 600;
                color: #f39c12;
                padding: 10px;
                background: #fef5e7;
                border-radius: 6px;
                border: 1px solid #f39c12;
            }
        """)
    
    def setStatusReady(self):
        self.status.setText("Ready")
        self.status.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: 600;
                color: #27ae60;
                padding: 10px;
                background: #d5f4e6;
                border-radius: 6px;
                border: 1px solid #27ae60;
            }
        """)