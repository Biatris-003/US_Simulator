import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
from Matplotlib_Canvas import MatplotlibCanvas
from Metrics_Widget import MetricsWidget
from Control_Panel import ControlPanel
from Profile_Plot_Widget import ProfilePlotWidget
from Ultrasound_Simulator import UltrasoundSimulator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.simulator = UltrasoundSimulator()
        self.current_num_cysts = 3  # Track current cyst count
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("US Harmonic vs Fundamental Imaging Simulator")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("""
        QMainWindow {
            background-color: #eef2f6;
        }

        QGroupBox {
            font-weight: 600;
            border: 1px solid #c7d0d9;
            border-radius: 8px;
            margin-top: 12px;
            padding: 8px;
            background-color: #ffffff;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 6px;
            color: #1f4e79;
        }

        QTableWidget {
            background-color: #ffffff;
            gridline-color: #dce3ea;
            font-size: 11px;
        }

        QHeaderView::section {
            background-color: #1f4e79;
            color: white;
            padding: 6px;
            border: none;
            font-weight: bold;
        }

        QPushButton {
            background-color: #1f78b4;
            color: white;
            border-radius: 6px;
            padding: 8px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #155a8a;
        }

        QPushButton:pressed {
            background-color: #0e3f63;
        }

        QSlider::groove:horizontal {
            height: 6px;
            background: #d0d7de;
            border-radius: 3px;
        }

        QSlider::handle:horizontal {
            background: #1f78b4;
            width: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }

        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        
        left_panel = QVBoxLayout() #for metrics & controls
        
        self.control_panel = ControlPanel()
        left_panel.addWidget(self.control_panel)
        
        self.metrics_widget = MetricsWidget()
        left_panel.addWidget(self.metrics_widget)
        
        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel)
        left_panel_widget.setMaximumWidth(550)
        main_layout.addWidget(left_panel_widget)
        
        right_panel = QVBoxLayout() #for plots & images
        
        self.image_tabs = QTabWidget()
        self.image_tabs.setDocumentMode(True)
        self.image_tabs.setTabPosition(QTabWidget.North)
        
        #tab 1: phantom
        self.phantom_canvas = MatplotlibCanvas(self, width=6, height=4)
        phantom_tab = QWidget()
        phantom_layout = QVBoxLayout()
        phantom_layout.addWidget(self.phantom_canvas)
        phantom_tab.setLayout(phantom_layout)
        self.image_tabs.addTab(phantom_tab, "Phantom")
        
        #tab 2: comparison
        self.comparison_canvas = MatplotlibCanvas(self, width=6, height=4)
        comp_tab = QWidget()
        comp_layout = QVBoxLayout()
        comp_layout.addWidget(self.comparison_canvas)
        comp_tab.setLayout(comp_layout)
        self.image_tabs.addTab(comp_tab, "Side-by-Side Comparison")
        right_panel.addWidget(self.image_tabs)
        
        #profile plot
        self.profile_plot = ProfilePlotWidget()
        right_panel.addWidget(self.profile_plot)
        
        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel)
        main_layout.addWidget(right_panel_widget)
        
        self.control_panel.simulate_btn.clicked.connect(self.run_simulation)
        
        # Connect sliders to update graphs in real-time (optional)
        self.control_panel.nl_slider.valueChanged.connect(self.update_profile_plot)
        
        #initial simulation
        self.run_simulation()
     
    def update_profile_plot(self):
        """Update only the profile plot when nonlinear coefficient changes"""
        nonlinear_coeff = self.control_panel.nl_slider.value() / 100.0
        depth, fund_curve, harm_curve = self.simulator.depth_signal_profiles(nonlinear_coeff)
        self.profile_plot.plot_profiles(depth, fund_curve, harm_curve)
    
    def run_simulation(self):  #actual running for US simulation
        print(f"Frequency: {self.control_panel.freq_slider.value() / 10.0} MHz")
        print(f"Bandwidth: {self.control_panel.bw_slider.value()}%")
        print(f"Nonlinear coeff: {self.control_panel.nl_slider.value() / 100.0}")
        print(f"Number of cysts: {self.control_panel.cysts_slider.value()}")

        try:
            freq = self.control_panel.freq_slider.value() / 10.0  # MHz
            bandwidth = self.control_panel.bw_slider.value() / 100.0  # 0.2-0.8
            nonlinear_coeff = self.control_panel.nl_slider.value() / 100.0  # 0.2-0.8
            num_cysts = self.control_panel.cysts_slider.value()  # 1-5
            
            # Update simulator parameters
            self.simulator.f0 = freq * 1e6  # Convert to Hz
            self.simulator.lambda_fund = self.simulator.c / self.simulator.f0
            self.simulator.lambda_harm = self.simulator.c / (2 * self.simulator.f0)
            self.simulator.nonlinear_coeff = nonlinear_coeff  # Store for metrics calculation
            
            phantom = self.simulator.create_cyst_phantom(num_cysts)
            
            self.phantom_canvas.plot_image(
                phantom,
                "Cyst Phantom",
                cmap='gray',
                vmin=0,
                vmax=2,
                aspect = 'auto',
                interpolation = 'bilinear'
            )
            
            #fundamental imaging with current parameters
            self.simulator.fundamental_img = self.simulator.simulate_imaging('fundamental', bandwidth, nonlinear_coeff)
            
            #harmonic imaging with current parameters
            self.simulator.harmonic_img = self.simulator.simulate_imaging('harmonic', bandwidth, nonlinear_coeff)
            
            #metrics calc & update display:
            metrics = self.simulator.calculate_metrics(self.simulator.fundamental_img, self.simulator.harmonic_img)
            self.metrics_widget.update_metrics(metrics)
            self.plot_comparison()
            
            #plot depth signal profiles with current nonlinear coefficient
            depth, fund_curve, harm_curve = self.simulator.depth_signal_profiles(nonlinear_coeff)
            self.profile_plot.plot_profiles(depth, fund_curve, harm_curve)
                
        except Exception as e:
            print(f"Error during simulation: {e}")
            return
            
    def plot_comparison(self):  #side-by-side
        if self.simulator.fundamental_img is None or self.simulator.harmonic_img is None:
            return
        fig = self.comparison_canvas.figure
        fig.clear()
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        
        #plotting fund. US
        im1 = ax1.imshow(self.simulator.fundamental_img, cmap='gray', vmin=-60, vmax=0, 
                        aspect='auto', interpolation='bilinear')
        ax1.set_title("Fundamental Imaging", fontsize=10, fontweight='bold')
        ax1.set_xlabel("Lateral Position [pixels]")
        ax1.set_ylabel("Axial Position [pixels]")
        
        #plotting harm. US
        im2 = ax2.imshow(self.simulator.harmonic_img, cmap='gray', vmin=-60, vmax=0,
                        aspect='auto', interpolation='bilinear')
        ax2.set_title("Harmonic Imaging", fontsize=10, fontweight='bold')
        ax2.set_xlabel("Lateral Position [pixels]")
        ax2.set_ylabel("Axial Position [pixels]")
        
        fig.colorbar(im1, ax=ax1, label='Intensity [dB]')
        fig.colorbar(im2, ax=ax2, label='Intensity [dB]')
        fig.suptitle("Fundamental vs Harmonic Imaging Comparison",fontsize=12, fontweight='bold')        
        self.comparison_canvas.draw()
        
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()