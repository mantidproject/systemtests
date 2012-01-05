from stresstesting import MantidStressTest
import DirectEnergyConversion as reduction
from MantidFramework import mtd
import os

class DirectInelasticDiagnostic(MantidStressTest):
    
    def runTest(self):
        white = 'MAP17186.raw'
        sample = 'MAP17269.raw'
        
        # Libisis values to check against
        tiny=1e-10
        huge=1e10

        v_out_lo = 0.01
        v_out_hi = 100.

        vv_lo = 0.1
        vv_hi = 2.0
        vv_sig = 0.0
        
        sv_sig = 3.3
        sv_hi = 1.5
        sv_lo = 0.0
        s_zero = False
        
        reducer = reduction.setup_reducer('MAPS')
        diag_mask = reducer.diagnose(white, sample=sample, tiny=tiny, huge=huge, 
                                     van_out_lo=v_out_lo, van_out_hi=v_out_hi,
                                     van_lo=vv_lo, van_hi=vv_hi, van_sig=vv_sig,
                                     samp_lo=sv_lo, samp_hi=sv_hi, samp_sig=sv_sig, samp_zero=s_zero)

        
        # Save the masked spectra nmubers to a simple ASCII file for comparison
        self.saved_diag_file = os.path.join(mtd.settings['defaultsave.directory'], 'CurrentDirectInelasticDiag.txt')
        handle = file(self.saved_diag_file, 'w')
        for index in range(diag_mask.getNumberHistograms()):
            if diag_mask.getDetector(index).isMasked():
                spec_no = diag_mask.getSpectrum(index).getSpectrumNo()
                handle.write(str(spec_no) + '\n')
        handle.close
        
    def cleanup(self):
        if os.path.exists(self.saved_diag_file):
            if self.succeeded():
                os.remove(self.saved_diag_file)
            else:
                os.rename(self.saved_diag_file, os.path.join(mtd.settings['defaultsave.directory'], 'DirectInelasticDiag-Mismatch.txt'))
        
    def validateMethod(self):
        return 'validateASCII'
        
    def validate(self):
        return self.saved_diag_file, \
            os.path.join(os.path.dirname(__file__), 'ReferenceResults','DirectInelasticDiagnostic.txt')
