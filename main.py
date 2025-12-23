import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

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
        self.setWindowTitle("Task 12: Harmonic vs Fundamental")
        self.setGeometry(100, 100, 1400, 900)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # --- LEFT (Controls) ---
        left = QVBoxLayout()
        self.controls = ControlPanel()
        left.addWidget(self.controls)
        self.metrics = MetricsWidget()
        left.addWidget(self.metrics)
        
        left_cont = QWidget()
        left_cont.setLayout(left)
        left_cont.setMaximumWidth(400)
        main_layout.addWidget(left_cont)
        
        # --- RIGHT (Plots) ---
        right = QVBoxLayout()
        
        self.canvas_compare = MatplotlibCanvas(self)
        right.addWidget(self.canvas_compare, stretch=2)
        
        self.plot_profile = ProfilePlotWidget()
        right.addWidget(self.plot_profile, stretch=1)
        
        right_cont = QWidget()
        right_cont.setLayout(right)
        main_layout.addWidget(right_cont)
        
        # --- CONNECTIONS ---
        self.controls.freq_slider.valueChanged.connect(self.schedule_update)
        self.controls.nl_slider.valueChanged.connect(self.schedule_update)
        self.controls.pi_check.stateChanged.connect(self.schedule_update)

    def schedule_update(self):
        self.controls.status.setText("Updating...")
        self.update_graphs()
        self.timer.start()
        
    def update_graphs(self):
        f = (self.controls.freq_slider.value() / 10.0) * 1e6
        nl = self.controls.nl_slider.value() / 100.0
        
        z, fund, harm = self.simulator.get_profiles(f, nl)
        self.plot_profile.plot_profiles(z, fund, harm)

    def run_simulation(self):
        freq = (self.controls.freq_slider.value() / 10.0) * 1e6
        nl_coeff = self.controls.nl_slider.value() / 100.0
        pi = self.controls.pi_check.isChecked()
        
        # Create Phantom
        self.simulator.create_phantom()
        
        # Run Physics
        fund_img = self.simulator.run_imaging('fundamental', freq, nl_coeff, pi)
        harm_img = self.simulator.run_imaging('harmonic', freq, nl_coeff, pi)
        
        # Update Displays
        self.canvas_compare.plot_comparison(fund_img, harm_img)
        self.update_graphs()
        
        # Metrics
        stats = self.simulator.get_metrics()
        self.metrics.update_metrics(stats)
        
        self.controls.status.setText("Ready")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()