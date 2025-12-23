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
        
        # 1. Init Logic
        self.simulator = UltrasoundSimulator()
        
        # 2. Timer for Debouncing (Prevents freezing)
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(100) # 100ms delay
        self.timer.timeout.connect(self.run_simulation)
        
        self.init_ui()
        
        # 3. Trigger Initial Sim
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
        self.tabs = QTabWidget()
        
        self.canvas_phantom = MatplotlibCanvas(self)
        self.tabs.addTab(self.canvas_phantom, "Phantom")
        
        self.canvas_compare = MatplotlibCanvas(self)
        self.tabs.addTab(self.canvas_compare, "Comparison")
        
        right.addWidget(self.tabs, stretch=2)
        
        self.plot_profile = ProfilePlotWidget()
        right.addWidget(self.plot_profile, stretch=1)
        
        right_cont = QWidget()
        right_cont.setLayout(right)
        main_layout.addWidget(right_cont)
        
        # --- CONNECTIONS ---
        # Any slider change restarts the timer
        self.controls.freq_slider.valueChanged.connect(self.schedule_update)
        self.controls.nl_slider.valueChanged.connect(self.schedule_update)
        self.controls.cysts_slider.valueChanged.connect(self.schedule_update)
        self.controls.pi_check.stateChanged.connect(self.schedule_update)
        self.controls.patient_combo.currentIndexChanged.connect(self.schedule_update)

    def schedule_update(self):
        self.controls.status.setText("Updating...")
        # Update line graph immediately (it's fast)
        self.update_graphs()
        # Delay image generation (it's slow)
        self.timer.start()
        
    def update_graphs(self):
        # Read UI
        f = (self.controls.freq_slider.value() / 10.0) * 1e6
        nl = self.controls.nl_slider.value() / 100.0
        obese = (self.controls.patient_combo.currentIndex() == 1)
        
        # Get Data
        z, fund, harm = self.simulator.get_profiles(f, nl, obese)
        self.plot_profile.plot_profiles(z, fund, harm)

    def run_simulation(self):
        # 1. Gather all Parameters
        freq = (self.controls.freq_slider.value() / 10.0) * 1e6
        nl_coeff = self.controls.nl_slider.value() / 100.0
        n_cysts = self.controls.cysts_slider.value()
        pi = self.controls.pi_check.isChecked()
        is_obese = (self.controls.patient_combo.currentIndex() == 1)
        
        # 2. Update Phantom (only if needed, but fast enough to just do it)
        phantom = self.simulator.create_phantom(n_cysts)
        if self.tabs.currentIndex() == 0:
            self.canvas_phantom.plot_image(phantom, "Acoustic Phantom", vmin=0, vmax=2)
        
        # 3. Run Physics Engine
        fund_img = self.simulator.run_imaging('fundamental', freq, nl_coeff, pi, is_obese)
        harm_img = self.simulator.run_imaging('harmonic', freq, nl_coeff, pi, is_obese)
        
        # 4. Update Displays
        self.canvas_compare.plot_comparison(fund_img, harm_img)
        self.update_graphs()
        
        # 5. Metrics
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