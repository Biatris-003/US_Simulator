from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class MetricsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
    
        title = QLabel("Quantitative Metrics")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        layout.addWidget(title)
        

        self.table = QTableWidget(4, 2) 
        self.table.setHorizontalHeaderLabels(["Fundamental", "Harmonic"])
        
        self.table.setVerticalHeaderLabels([
            "Lateral Res (mm)", 
            "Side-Lobes (dB)", 
            "CNR", 
            "SNR"
        ])
        

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #dee2e6;
                border: 2px solid #3498db;
                border-radius: 8px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #d6eaf8;
                color: #1a5490;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QHeaderView::section:horizontal {
                border-right: 1px solid #2980b9;
            }
            QHeaderView::section:vertical {
                border-bottom: 1px solid #2980b9;
                background-color: #5dade2;
            }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers) 
        layout.addWidget(self.table)
        self.setLayout(layout)
        
    def update_metrics(self, m):
        if not m: return
        
        def set_item(r, c, txt, color=None):
            it = QTableWidgetItem(txt)
            it.setTextAlignment(Qt.AlignCenter)
            
            # Default font
            font = QFont()
            font.setPointSize(12)
            font.setWeight(QFont.Bold)
            it.setFont(font)
            
            if color:
                it.setBackground(color)
                it.setForeground(QColor(27, 94, 32)) 
            else:
                it.setForeground(QColor(52, 73, 94)) 
                
            self.table.setItem(r, c, it)
            
        # 1. Resolution (Lower is better)
        f_res, h_res = m['fund_fwhm'], m['harm_fwhm']
        set_item(0, 0, f"{f_res:.2f}")
        set_item(0, 1, f"{h_res:.2f}", QColor(165, 214, 167) if h_res < f_res else None)
        
        # 2. Side Lobes (Lower is better)
        f_sl, h_sl = m['fund_sl'], m['harm_sl']
        set_item(1, 0, f"{f_sl:.1f}")
        set_item(1, 1, f"{h_sl:.1f}", QColor(165, 214, 167) if h_sl < f_sl else None)
        
        # 3. CNR (Higher is better)
        f_cnr, h_cnr = m['fund_cnr'], m['harm_cnr']
        set_item(2, 0, f"{f_cnr:.2f}")
        set_item(2, 1, f"{h_cnr:.2f}", QColor(165, 214, 167) if h_cnr > f_cnr else None)
        
        # 4. SNR (Higher is better)
        f_snr, h_snr = m['fund_snr'], m['harm_snr']
        set_item(3, 0, f"{f_snr:.2f}")
        set_item(3, 1, f"{h_snr:.2f}", QColor(165, 214, 167) if h_snr > f_snr else None)