from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MetricsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Quantitative Metrics"))
        
        # 4 Rows (Metrics), 2 Columns (Modes)
        self.table = QTableWidget(4, 2) 
        self.table.setHorizontalHeaderLabels(["Fundamental", "Harmonic"])
        
        self.table.setVerticalHeaderLabels([
            "Lateral Res (mm)", 
            "Side-Lobes (dB)", 
            "CNR", 
            "SNR"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.setLayout(layout)
        
    def update_metrics(self, m):
        if not m: return
        
        def set_item(r, c, txt, color=None):
            it = QTableWidgetItem(txt)
            it.setTextAlignment(Qt.AlignCenter)
            if color: it.setBackground(color)
            self.table.setItem(r, c, it)
            
        # 1. Resolution (Lower is better)
        f_res, h_res = m['fund_fwhm'], m['harm_fwhm']
        set_item(0, 0, f"{f_res:.2f}")
        set_item(0, 1, f"{h_res:.2f}", QColor(200,255,200) if h_res < f_res else None)
        
        # 2. Side Lobes (Lower is better)
        f_sl, h_sl = m['fund_sl'], m['harm_sl']
        set_item(1, 0, f"{f_sl:.1f}")
        set_item(1, 1, f"{h_sl:.1f}", QColor(200,255,200) if h_sl < f_sl else None)
        
        # 3. CNR (Higher is better)
        f_cnr, h_cnr = m['fund_cnr'], m['harm_cnr']
        set_item(2, 0, f"{f_cnr:.2f}")
        set_item(2, 1, f"{h_cnr:.2f}", QColor(200,255,200) if h_cnr > f_cnr else None)
        
        # 4. SNR (Higher is better)
        f_snr, h_snr = m['fund_snr'], m['harm_snr']
        set_item(3, 0, f"{f_snr:.2f}")
        set_item(3, 1, f"{h_snr:.2f}", QColor(200,255,200) if h_snr > f_snr else None)