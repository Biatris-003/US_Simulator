
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class MetricsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Image Quality Metrics")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        #read-only table
        self.table = QTableWidget(4, 3)
        self.table.setHorizontalHeaderLabels(["Metric", "Fundamental", "Harmonic"])
        self.table.setVerticalHeaderLabels(["Resolution (mm)", "Side-lobes (dB)", "CNR", "Improvement"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)
        self.setLayout(layout)
        
    def update_metrics(self, metrics):
        if not metrics:
            return
            
        #1.res
        self.table.setItem(0, 0, QTableWidgetItem("FWHM"))
        self.table.setItem(0, 1, QTableWidgetItem(f"{metrics.get('fund_fwhm_mm', 0):.2f} mm"))
        self.table.setItem(0, 2, QTableWidgetItem(f"{metrics.get('harm_fwhm_mm', 0):.2f} mm"))
        
        #2.side-lobes
        self.table.setItem(1, 0, QTableWidgetItem("Side-lobe Level"))
        self.table.setItem(1, 1, QTableWidgetItem(f"{metrics.get('fund_sidelobe_db', 0):.1f} dB"))
        self.table.setItem(1, 2, QTableWidgetItem(f"{metrics.get('harm_sidelobe_db', 0):.1f} dB"))
        
        #3.CNR
        self.table.setItem(2, 0, QTableWidgetItem("CNR"))
        self.table.setItem(2, 1, QTableWidgetItem(f"{metrics.get('fund_cnr', 0):.2f}"))
        self.table.setItem(2, 2, QTableWidgetItem(f"{metrics.get('harm_cnr', 0):.2f}"))
        
        #4.total imp
        fund_fwhm = metrics.get('fund_fwhm_mm', 1)
        harm_fwhm = metrics.get('harm_fwhm_mm', 1)
        res_improvement = ((fund_fwhm - harm_fwhm) / fund_fwhm * 100) if fund_fwhm > 0 else 0
        fund_cnr = metrics.get('fund_cnr', 1)
        harm_cnr = metrics.get('harm_cnr', 1)
        cnr_improvement = ((harm_cnr - fund_cnr) / fund_cnr * 100) if fund_cnr > 0 else 0
        improvement_text = f"Res: {res_improvement:.1f}%, CNR: {cnr_improvement:.1f}%"
        self.table.setItem(3, 0, QTableWidgetItem("Improvement"))
        self.table.setItem(3, 1, QTableWidgetItem(""))
        self.table.setItem(3, 2, QTableWidgetItem(improvement_text))
        
        #improvements showing through color coding
        for row in range(3):
            fund_val = float(self.table.item(row, 1).text().split()[0])
            harm_val = float(self.table.item(row, 2).text().split()[0])
            
            if row == 0 or row == 1:  #low is good in resolution & side-lobes
                if harm_val < fund_val:
                    self.table.item(row, 2).setBackground(QColor(200, 255, 200))
                else:
                    self.table.item(row, 2).setBackground(QColor(255, 200, 200))
            else:  #high is good in CNR
                if harm_val > fund_val:
                    self.table.item(row, 2).setBackground(QColor(200, 255, 200))
                else:
                    self.table.item(row, 2).setBackground(QColor(255, 200, 200))
