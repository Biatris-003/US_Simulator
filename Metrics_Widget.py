from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MetricsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Quantitative Metrics"))
        
        self.table = QTableWidget(4, 3)
        self.table.setHorizontalHeaderLabels(["Metric", "Fundamental", "Harmonic"])
        self.table.setVerticalHeaderLabels(["Resolution (FWHM)", "Side-Lobes", "CNR", "Improvement"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
            
        # Res
        f_res, h_res = m['fund_fwhm_mm'], m['harm_fwhm_mm']
        set_item(0, 0, "FWHM (mm)")
        set_item(0, 1, f"{f_res:.2f}")
        set_item(0, 2, f"{h_res:.2f}", QColor(200,255,200) if h_res < f_res else None)
        
        # Sidelobes
        f_sl, h_sl = m['fund_sidelobe_db'], m['harm_sidelobe_db']
        set_item(1, 0, "Side Lobes (dB)")
        set_item(1, 1, f"{f_sl:.1f}")
        set_item(1, 2, f"{h_sl:.1f}", QColor(200,255,200) if h_sl < f_sl else None)
        
        # CNR
        f_cnr, h_cnr = m['fund_cnr'], m['harm_cnr']
        set_item(2, 0, "CNR")
        set_item(2, 1, f"{f_cnr:.2f}")
        set_item(2, 2, f"{h_cnr:.2f}", QColor(200,255,200) if h_cnr > f_cnr else None)
        
        # Improvement
        imp = ((f_res - h_res)/f_res)*100 if f_res > 0 else 0
        set_item(3, 0, "Resolution Gain")
        set_item(3, 1, "-")
        set_item(3, 2, f"+{imp:.1f}%")