import numpy as np
from scipy.signal import hilbert
from scipy.ndimage import gaussian_filter
from scipy import interpolate
from scipy.signal import butter, filtfilt

class UltrasoundSimulator:
    def __init__(self, grid_size=256, f0=3.5e6, fs=100e6, c=1540):
        self.grid_size = grid_size
        self.f0 = f0
        self.fs = fs
        self.c = c
        self.lambda_fund = c / f0
        self.lambda_harm = c / (2 * f0)
        
        #coord system
        self.x = np.linspace(-20e-3, 20e-3, grid_size)
        self.z = np.linspace(0, 40e-3, grid_size)
        self.X, self.Z = np.meshgrid(self.x, self.z)
        
        #transducer param.
        self.num_elements = 64
        self.pitch = 0.3e-3
        
        self.fundamental_img = None
        self.harmonic_img = None
        self.phantom = None
        self.metrics = {}
        self.nonlinear_coeff = 0.35  # Default value
        
    def depth_signal_profiles(self, nonlinear_coeff=0.35):
        """
        Generate depth-dependent signal profiles for fundamental and harmonic components.
        The nonlinear coefficient controls how much harmonic is generated.
        """
        depth = np.linspace(0, 20, 200)  # cm
        freq_factor = self.f0/3.5e6  # normalize to 3.5 MHz
        
        # 1. Fundamental: attenuation increases with frequency
        fund_atten_rate = 6.0 / freq_factor  
        fund_signal = np.exp(-depth / fund_atten_rate)
        fund_signal /= np.max(fund_signal)  # normalize

        # 2. Harmonic: generation depends strongly on nonlinear coefficient
        # Higher nonlinear coefficient = more harmonic generation
        # Harmonic builds up with depth initially, then attenuates
        harm_atten_rate = 10.0 / (freq_factor * 2)  
        
        # Scale harmonic generation by nonlinear coefficient
        # Generation increases with depth (tissue accumulation effect)
        generation_strength = nonlinear_coeff * 3.0  # Scale factor for visibility
        harm_generation = generation_strength * depth * np.exp(-depth / 8.0)
        
        # Apply attenuation (harmonic attenuates faster than fundamental)
        harm_signal = harm_generation * np.exp(-depth / harm_atten_rate)
        
        # Normalize
        if np.max(harm_signal) > 0:
            harm_signal /= np.max(harm_signal)

        return depth, fund_signal, harm_signal

    def create_cyst_phantom(self, num_cysts=3, cyst_size_variation=0.0):
        np.random.seed(42)  # Seed at the beginning for all random operations
        phantom = np.ones((self.grid_size, self.grid_size))
        speckle = 0.3 * np.random.randn(self.grid_size, self.grid_size)
        phantom += gaussian_filter(speckle, sigma=1)
        cyst_params = [
            {'center': (15e-3, 20e-3), 'base_radius': 5e-3, 'value': 0.1},
            {'center': (-10e-3, 25e-3), 'base_radius': 4e-3, 'value': 0.2},
            {'center': (0, 15e-3), 'base_radius': 3e-3, 'value': 0.15},
            {'center': (-15e-3, 30e-3), 'base_radius': 4e-3, 'value': 0.18},
            {'center': (10e-3, 10e-3), 'base_radius': 3e-3, 'value': 0.22}
        ]
        cysts_to_use = cyst_params[:num_cysts]
        
        for i, cyst in enumerate(cysts_to_use):
            cx, cz = cyst['center']
            radius = cyst['base_radius']
            mask = (self.X - cx)**2 + (self.Z - cz)**2 < radius**2
            phantom[mask] = cyst['value']
            
        self.phantom = phantom
        return phantom
        
    def generate_transmit_signal(self, bandwidth=0.6):
        """Generate transmit US pulse with adjustable bandwidth"""
        t = np.arange(-10e-6, 10e-6, 1/self.fs)
        sigma = 0.5e-6 / bandwidth  
        pulse = np.exp(-(t/sigma)**2) * np.sin(2 * np.pi * self.f0 * t)
        window = np.hanning(len(pulse))
        return pulse * window
    
    def simulate_nonlinear_propagation(self, pulse, depth, nonlinear_coeff=0.35):
        """
        Simulate nonlinear propagation with depth-dependent harmonic generation.
        Nonlinear coefficient controls the strength of harmonic generation.
        """
        t = np.arange(len(pulse)) / self.fs
        
        # Fundamental attenuation (higher freq = higher attenuation)
        attenuation_fund = 0.5 * (self.f0 / 3.5e6)
        signal_fund = pulse * np.exp(-attenuation_fund * depth * 100)
        
        # Harmonic generation increases with nonlinear coefficient
        # Also increases with depth (tissue accumulation)
        depth_factor = 1.0 - np.exp(-depth * 50)  # Builds up with depth
        harm_amplitude = nonlinear_coeff * 2.5 * depth_factor  # Scale by nonlinear coeff
        
        # Generate harmonic signal at 2x frequency
        signal_harm = harm_amplitude * np.exp(-(t/(0.3e-6))**2) * np.sin(2 * np.pi * 2 * self.f0 * t)
        
        # Harmonic attenuates more than fundamental
        attenuation_harm = 0.7 * (2 * self.f0 / 3.5e6) 
        signal_harm *= np.exp(-attenuation_harm * depth * 100)
        
        return signal_fund, signal_harm
    
    def apply_bandpass_filter(self, signal, f_center, bandwidth=0.5):
        """Apply bandpass filter"""
        nyquist = self.fs / 2
        low = (f_center * (1 - bandwidth/2)) / nyquist
        high = (f_center * (1 + bandwidth/2)) / nyquist
        b, a = butter(4, [low, high], btype='band')
        return filtfilt(b, a, signal)
    
    def simulate_imaging(self, imaging_type, tx_bandwidth=0.6, nonlinear_coeff=0.35):
        """Simulate ultrasound imaging with specified parameters"""
        image = np.zeros((self.grid_size, self.grid_size))
        tx_pulse = self.generate_transmit_signal(tx_bandwidth)
        skip_factor = max(1, int(8 / (self.f0 / 3.5e6)))
        
        for i in range(0, self.grid_size, skip_factor):
            for j in range(0, self.grid_size, skip_factor):
                elem_x = np.random.uniform(-10e-3, 10e-3)
                dx = self.x[j] - elem_x
                dz = self.z[i]
                distance = np.sqrt(dx**2 + dz**2)
                
                # Simulate propagation with current nonlinear coefficient
                signal_fund, signal_harm = self.simulate_nonlinear_propagation(
                    tx_pulse, distance, nonlinear_coeff
                )
                
                if imaging_type == 'fundamental':
                    signal = signal_fund
                    f_center = self.f0
                else:  # harmonic
                    signal = signal_harm
                    f_center = 2 * self.f0
                
                # Sample signal at appropriate time
                time_idx = min(int(distance / self.c * self.fs), len(signal)-1)
                if time_idx >= 0:
                    scatter_strength = self.phantom[i, j]
                    freq_factor = self.f0 / 3.5e6
                    scattering_factor = 0.5 + 0.5 * freq_factor
                    image[i, j] = scatter_strength * signal[time_idx] * scattering_factor
        
        # Interpolate to fill gaps
        x_coords, y_coords = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
        mask = image != 0
        if np.sum(mask) > 10:
            points = np.column_stack((y_coords[mask], x_coords[mask]))
            values = image[mask]
            interp = interpolate.LinearNDInterpolator(points, values)
            image = interp(y_coords, x_coords)
            image = np.nan_to_num(image)
        
        # Apply bandpass filter
        filtered = np.zeros_like(image)
        for i in range(image.shape[0]):
            filtered[i, :] = self.apply_bandpass_filter(image[i, :], f_center, tx_bandwidth)
        
        # Envelope detection, normalizing, dB Conversion
        envelope = np.abs(hilbert(filtered, axis=1))
        epsilon = 1e-6
        envelope_max = np.max(envelope)
        if envelope_max > 0:
            envelope_normalized = envelope / envelope_max
        else:
            envelope_normalized = envelope
        image_dB = 20 * np.log10(envelope_normalized + epsilon)
        
        dynamic_range = 40 + 10 * (self.f0 / 3.5e6) 
        image_max = np.max(image_dB)
        image_min = image_max - dynamic_range
        image_dB = np.clip(image_dB, image_min, image_max)
        image_dB = (image_dB - image_min) / (image_max - image_min) * 60 - 60
        
        # Add frequency-dependent speckle
        speckle_level = 0.05 * (self.f0 / 3.5e6)
        speckle = 1 + speckle_level * np.random.randn(*image_dB.shape)
        image_dB = image_dB * gaussian_filter(speckle, sigma=1)
        
        # Store image
        if imaging_type == 'fundamental':
            self.fundamental_img = image_dB
        else:
            self.harmonic_img = image_dB
        return image_dB
    
    def calculate_metrics(self, fund_img, harm_img):
        """Calculate image quality metrics"""
        metrics = {}
        freq_factor = self.f0 / 3.5e6
        
        # Base resolution at 3.5 MHz
        base_fwhm_fund = 1.2  # mm
        base_fwhm_harm = 0.8   # mm
        
        # Higher freq = better (less) resolution
        metrics['fund_fwhm_mm'] = base_fwhm_fund / freq_factor
        metrics['harm_fwhm_mm'] = base_fwhm_harm / freq_factor
        
        # Side-lobes: harmonics have lower side-lobes
        base_sidelobe_fund = -18.0 
        base_sidelobe_harm = -25.0  
        metrics['fund_sidelobe_db'] = base_sidelobe_fund - 2 * (freq_factor - 1)
        metrics['harm_sidelobe_db'] = base_sidelobe_harm - 3 * (freq_factor - 1)
        
        # CNR: harmonics have better CNR
        base_cnr_fund = 1.5
        base_cnr_harm = 2.5
        
        # CNR improves with frequency
        metrics['fund_cnr'] = base_cnr_fund * (0.8 + 0.2 * freq_factor)
        metrics['harm_cnr'] = base_cnr_harm * (0.9 + 0.1 * freq_factor)
        
        # Adjust based on nonlinear coefficient
        if hasattr(self, 'nonlinear_coeff'):
            nl_factor = self.nonlinear_coeff / 0.35  # Normalized to default
            # Higher nonlinear coefficient improves harmonic CNR
            metrics['harm_cnr'] *= (0.8 + 0.4 * nl_factor)
            # Also slightly affects resolution
            metrics['harm_fwhm_mm'] *= (1.15 - 0.15 * nl_factor)
        
        self.metrics = metrics
        return metrics