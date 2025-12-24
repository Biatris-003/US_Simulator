import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Matplotlib_Canvas import MatplotlibCanvas
from Metrics_Widget import MetricsWidget
from Control_Panel import ControlPanel
from Profile_Plot_Widget import ProfilePlotWidget
from Ultrasound_Simulator import UltrasoundSimulator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.simulator = UltrasoundSimulator()
        
        # Timer
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(100) 
        self.timer.timeout.connect(self.run_simulation)
        
        self.init_ui()
        self.run_simulation()
        
    def init_ui(self):
        self.setWindowTitle("Task 12: Harmonic vs Fundamental US Simulator")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QWidget {
                background-color: #ecf0f1;
            }
        """)
        
        self.showFullScreen()
    
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        #left (controls + metrics)
        left = QVBoxLayout()
        left.setSpacing(15)
        
        self.controls = ControlPanel()
        left.addWidget(self.controls)
        
        self.metrics = MetricsWidget()
        left.addWidget(self.metrics)
        
        left_cont = QWidget()
        left_cont.setLayout(left)
        left_cont.setMaximumWidth(450)
        left_cont.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
            }
        """)
        main_layout.addWidget(left_cont, stretch=1)
        
        #right(plots)
        right = QVBoxLayout()
        right.setSpacing(15)
        

        compare_header = QLabel("Ultrasound Image Comparison")
        compare_header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
        """)
        compare_header.setAlignment(Qt.AlignCenter)
        right.addWidget(compare_header)
        
        canvas_container = QWidget()
        canvas_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
        """)
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(10, 10, 10, 10)
        self.canvas_compare = MatplotlibCanvas(self)
        canvas_layout.addWidget(self.canvas_compare)
        right.addWidget(canvas_container, stretch=3)
        

        profile_header = QLabel("Signal Depth Profile")
        profile_header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
        """)
        profile_header.setAlignment(Qt.AlignCenter)
        right.addWidget(profile_header)
        
        profile_container = QWidget()
        profile_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
        """)
        profile_layout = QVBoxLayout(profile_container)
        profile_layout.setContentsMargins(10, 10, 10, 10)
        self.plot_profile = ProfilePlotWidget()
        profile_layout.addWidget(self.plot_profile)
        right.addWidget(profile_container, stretch=2)
        
        right_cont = QWidget()
        right_cont.setLayout(right)
        right_cont.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
            }
        """)
        main_layout.addWidget(right_cont, stretch=2)
        
        #connecting sliders
        self.controls.freq_slider.valueChanged.connect(self.schedule_update)
        self.controls.nl_slider.valueChanged.connect(self.schedule_update)
        self.controls.pi_check.stateChanged.connect(self.schedule_update)

    def schedule_update(self): #calling update_graphs&timer
        self.controls.setStatusUpdating()
        self.update_graphs()
        self.timer.start()
        
    def update_graphs(self): #slider values + get_profiles --> re-plot profiles
        freq = (self.controls.freq_slider.value() / 10.0) * 1e6
        nl_coeff = self.controls.nl_slider.value() / 100.0
        
        z, fund, harm = self.simulator.get_profiles(freq, nl_coeff) #z here refers to depth
        self.plot_profile.plot_profiles(z, fund, harm)

    def run_simulation(self): #slider values + pi  --> create phantoms & graphs & metrics
        freq = (self.controls.freq_slider.value() / 10.0) * 1e6
        nl_coeff = self.controls.nl_slider.value() / 100.0
        pi = self.controls.pi_check.isChecked() #pi here refers to pulse inversion
        
        #Phantom
        self.simulator.create_phantom()
        
        #img Physics
        fund_img = self.simulator.run_imaging('fundamental', freq, nl_coeff, pi) #img to be plotted
        harm_img = self.simulator.run_imaging('harmonic', freq, nl_coeff, pi) #img to be plotted
        
        #Graphs
        self.canvas_compare.plot_comparison(fund_img, harm_img)
        self.update_graphs()
        
        #Metrics
        stats = self.simulator.get_metrics()
        self.metrics.update_metrics(stats)
        
        self.controls.setStatusReady()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    #color palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(236, 240, 241))
    palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(248, 249, 250))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(44, 62, 80))
    palette.setColor(QPalette.Text, QColor(44, 62, 80))
    palette.setColor(QPalette.Button, QColor(52, 152, 219))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(231, 76, 60))
    palette.setColor(QPalette.Link, QColor(52, 152, 219))
    palette.setColor(QPalette.Highlight, QColor(52, 152, 219))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()