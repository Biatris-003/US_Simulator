import numpy as np
from scipy.signal import convolve2d

class UltrasoundSimulator:
    def __init__(self, grid_size=256):
        self.grid_size = grid_size
        self.width_m = 40e-3
        self.depth_m = 60e-3
        
        self.x = np.linspace(-self.width_m/2, self.width_m/2, grid_size)
        self.z = np.linspace(0, self.depth_m, grid_size)
        self.X, self.Z = np.meshgrid(self.x, self.z)
        
        self.fundamental_img = None
        self.harmonic_img = None
        self.phantom = None
        self.cyst_masks = []
        self.inner_cyst_masks = []
        
        # Target depth for resolution measurement
        self.wire_depth_m = 25e-3 

    def create_phantom(self):
        np.random.seed(42)
        
        # 1. Background Tissue (Standard Rayleigh Speckle)
        self.phantom = np.abs(np.random.normal(0, 1.0, (self.grid_size, self.grid_size)))
        
        # 2. Cysts (Perfectly Empty / Anechoic)
        configs = [
            (0, 30e-3, 6e-3),       # Center Large
            (-12e-3, 45e-3, 4e-3),  # Deep Left
            (12e-3, 15e-3, 3e-3)    # Shallow Right
        ]
        
        self.cyst_masks = []
        self.inner_cyst_masks = []
        
        for cx, cz, r in configs:
            mask = (self.X - cx)**2 + (self.Z - cz)**2 < r**2
            self.phantom[mask] = 0.0 
            self.cyst_masks.append(mask)
            
            # Inner mask (50% radius) for accurate stats
            inner = (self.X - cx)**2 + (self.Z - cz)**2 < (r * 0.5)**2
            self.inner_cyst_masks.append(inner)

        # 3. Wire Targets
        wire_depths = [10e-3, self.wire_depth_m, 40e-3, 55e-3]
        for d in wire_depths:
            z_idx = np.argmin(np.abs(self.z - d))
            x_idx = np.argmin(np.abs(self.x - 0))
            self.phantom[z_idx:z_idx+2, x_idx:x_idx+2] = 50.0 
            
        return self.phantom

    def get_psf(self, mode, freq_hz, nonlinear_coeff):
        k_size = 41
        xk = np.linspace(-6, 6, k_size)
        zk = np.linspace(-3, 3, k_size)
        Xk, Zk = np.meshgrid(xk, zk)
        r = np.sqrt(Xk**2)
        freq_scale = (3.5e6 / freq_hz)

        if mode == 'fundamental':
            # Standard Beam
            width = 0.85 * freq_scale 
            sl_amp = 0.20 
            beam = np.sinc(r / width) + sl_amp * np.exp(-(r - 3)**2) * np.cos(2*np.pi*r)
        else:
            # Harmonic beam: Square law narrowing
            width = 0.85 * freq_scale 
            sl_amp = 0.20 
            base = np.sinc(r / width) + sl_amp * np.exp(-(r - 3)**2) * np.cos(2*np.pi*r)
            
            # Stronger nonlinearity = Tighter beam focus power
            power_factor = 2.0 + (nonlinear_coeff * 0.5) 
            beam = np.sign(base) * (np.abs(base) ** power_factor)

        # Normalize energy
        beam /= (np.sum(np.abs(beam)) + 1e-9)
        
        # Axial pulse
        pulse = np.exp(-Zk**2 / (0.8 * freq_scale)) * np.cos(2*np.pi*Zk)
        return beam * pulse

    def run_imaging(self, mode, freq_hz, nonlinear_coeff, pulse_inv):
        psf = self.get_psf(mode, freq_hz, nonlinear_coeff)
        transmit_gain = 250.0
        rf = convolve2d(self.phantom, psf, mode="same") * transmit_gain

        # Nonlinear gain logic
        # Increasing nonlinear_coeff (beta) increases Harmonic signal strength
        if mode == "harmonic":
            # Growth with depth (z)
            depth_gain = 1.0 + (nonlinear_coeff * 2.0) * (self.Z / self.depth_m)
            # Overall brightness boost from coefficient
            amp_scale = 1.0 + (nonlinear_coeff * 3.0) 
        else:
            depth_gain = 1.0
            amp_scale = 1.0

        rf *= depth_gain * amp_scale

        # Noise floor (Static seed for stability)
        rng_state = np.random.RandomState(999)
        noise_std = 0.6 
        rf += rng_state.normal(0, noise_std, rf.shape)

        envelope = np.abs(rf)

        # Pulse inversion logic
        if mode == "harmonic":
            if pulse_inv:
                # PI boosts signal (x2) vs noise (sqrt2) -> Net SNR gain
                envelope *= 1.414 
            else:
                # Without PI, fundamental leaks in (clutter)
                fund_psf = self.get_psf("fundamental", freq_hz, nonlinear_coeff)
                fund_psf /= np.sum(np.abs(fund_psf)) + 1e-9
                leakage = convolve2d(self.phantom, fund_psf, mode="same") * transmit_gain
                
                # Leakage is reduced if nonlinearity is high (better conversion)
                leak_factor = 0.3 * (1.0 - (nonlinear_coeff * 0.5))
                envelope += leak_factor * np.abs(leakage)

        # Log compression
        # Fixed reference max prevents signal brightness jumping around arbitrarily
        ref_max = np.max(envelope) if np.max(envelope) > 1e-9 else 1e-9
        
        img_db = 20 * np.log10(envelope / ref_max + 1e-6)
        img_db = np.clip(img_db, -60, 0)

        if mode == "fundamental":
            self.fundamental_img = img_db
        else:
            self.harmonic_img = img_db
        return img_db

    def get_profiles(self, freq_hz, nonlinear_coeff):
        """
        Generates depth profiles for graphs.
        Fixed Relationship: Increasing nonlinear_coeff INCREASES Harmonic amplitude.
        """
        z = np.linspace(0, 6, 200)  # depth in cm
        f_MHz = freq_hz / 1e6
        alpha = 0.5  # Attenuation coeff

        # --- Fundamental (Standard Decay) ---
        fund = np.exp(-(2 * alpha * f_MHz * z) / 8.686)
        fund /= np.max(fund) # Normalize Fundamental to 1.0 for comparison

        # --- Harmonic Generation Physics ---
        # 1. Growth: Proportional to Beta (nonlinear_coeff) and Frequency^2 and Depth
        # nonlinear_coeff ranges ~0.1 to 0.8. 
        beta_effect = nonlinear_coeff * 2.0 # Scale factor for visibility
        growth = beta_effect * (f_MHz * 0.5) * z
        
        # 2. Decay: Higher frequency attenuates faster
        decay = np.exp(-(2 * alpha * (2 * f_MHz) * z) / 8.686)

        harm = growth * decay
        
        # Normalize relative to a fixed visual standard so the slider effect is visible
        # (Do NOT normalize by self-max, or the slider won't change height!)
        
        # We scale it so at max coeff it is slightly higher than fundamental, 
        # and at min coeff it is very weak.
        harm_scale_factor = 0.6 + (nonlinear_coeff * 0.8)
        
        # Normalize shape then apply scale
        if np.max(harm) > 0:
            harm = (harm / np.max(harm)) * harm_scale_factor
        
        return z, fund, harm

    def get_metrics(self):
        metrics = {}
        
        center_x = self.grid_size // 2
        true_z_px = int((self.wire_depth_m / self.depth_m) * self.grid_size)
        
        # --- 1. Analyze Wire Target (Sub-pixel Resolution) ---
        def analyze_wire(img):
            # Find peak near expected depth
            search_window = img[true_z_px-15:true_z_px+15, center_x]
            peak_idx = np.argmax(search_window)
            detected_z_px = (true_z_px - 15) + peak_idx
            
            # Get lateral profile
            row_db = img[detected_z_px, :]
            row_lin = 10**(row_db/20)
            row_lin /= np.max(row_lin)
            
            # Sub-pixel FWHM Calculation
            peak_x = np.argmax(row_lin)
            
            # Find left crossing
            left_idx = 0
            for i in range(peak_x, 0, -1):
                if row_lin[i] < 0.5:
                    left_idx = i
                    break
            
            if left_idx < peak_x:
                y1 = row_lin[left_idx]
                y2 = row_lin[left_idx+1]
                exact_left = left_idx + (0.5 - y1) / (y2 - y1 + 1e-9)
            else:
                exact_left = peak_x - 0.5

            # Find right crossing
            right_idx = len(row_lin) - 1
            for i in range(peak_x, len(row_lin)):
                if row_lin[i] < 0.5:
                    right_idx = i
                    break
            
            if right_idx > peak_x:
                y1 = row_lin[right_idx-1]
                y2 = row_lin[right_idx]
                exact_right = (right_idx-1) + (0.5 - y1) / (y2 - y1 + 1e-9)
            else:
                exact_right = peak_x + 0.5
                
            width_px = exact_right - exact_left
            width_mm = width_px * ((self.width_m * 1000) / self.grid_size)
            
            # Side Lobe Level
            mask = np.ones(self.grid_size, dtype=bool)
            mask[center_x-12:center_x+12] = False 
            sl = np.max(img[detected_z_px, mask])
            if sl < -55: sl = -60
            
            return width_mm, sl

        f_res, f_sl = analyze_wire(self.fundamental_img)
        h_res, h_sl = analyze_wire(self.harmonic_img)
        
        metrics['fund_fwhm'] = f_res
        metrics['harm_fwhm'] = h_res
        metrics['fund_sl'] = f_sl
        metrics['harm_sl'] = h_sl
        
        # --- 2. CNR & SNR ---
        if self.inner_cyst_masks:
            c_mask = self.inner_cyst_masks[0]
            
            b_mask = np.zeros((self.grid_size, self.grid_size), dtype=bool)
            margin = 30
            b_mask[margin:-margin, margin:-margin] = True
            center_col = self.grid_size // 2
            b_mask[:, center_col-15:center_col+15] = False 
            
            all_cysts = np.zeros((self.grid_size, self.grid_size), dtype=bool)
            for m in self.cyst_masks:
                all_cysts = np.logical_or(all_cysts, m)
            b_mask = np.logical_and(b_mask, ~all_cysts)

            def calc_stats(img_db):
                img_lin = 10**(img_db/20)
                
                mu_c = np.mean(img_lin[c_mask])
                mu_b = np.mean(img_lin[b_mask])
                sig_c = np.std(img_lin[c_mask])
                sig_b = np.std(img_lin[b_mask])
                
                # CNR
                denom = np.sqrt(sig_c**2 + sig_b**2)
                cnr_val = np.abs(mu_b - mu_c) / (denom + 1e-9)
                
                # SNR (Tissue Mean / Background Noise)
                snr_val = mu_b / (sig_b + 1e-9)
                
                return cnr_val, snr_val
            
            f_cnr, f_snr = calc_stats(self.fundamental_img)
            h_cnr, h_snr = calc_stats(self.harmonic_img)
            
            metrics['fund_cnr'] = f_cnr
            metrics['harm_cnr'] = h_cnr
            metrics['fund_snr'] = f_snr
            metrics['harm_snr'] = h_snr
            
        return metrics