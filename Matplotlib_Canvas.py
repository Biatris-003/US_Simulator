from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MatplotlibCanvas(FigureCanvas):  #for displaying images
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        self.current_image = None
        self.initialized = False  
        
    def plot_image(self, image, title="", cmap='gray', vmin=-60, vmax=0, aspect='auto', interpolation='bilinear'):
        if image is None:
            return
            
        #1st time setup only
        if not self.initialized:
            self.ax.clear()
            self.current_image = self.ax.imshow(
                image, cmap=cmap, vmin=vmin, vmax=vmax, 
                aspect=aspect, interpolation=interpolation
            )
            self.ax.set_title(title, fontsize=10, fontweight='bold')
            self.ax.set_xlabel('Lateral Position [pixels]')
            self.ax.set_ylabel('Axial Position [pixels]')
            self.cbar = self.fig.colorbar(self.current_image, ax=self.ax, shrink=0.8)
            self.cbar.set_label('Intensity', rotation=270, labelpad=15)
            self.fig.tight_layout()
            self.initialized = True
        else:
            #update data, don't recreate anything
            self.current_image.set_data(image)
            self.current_image.set_clim(vmin=vmin, vmax=vmax)
            self.ax.set_title(title, fontsize=10, fontweight='bold')
        
        self.draw()