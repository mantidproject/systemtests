import stresstesting
import sys
import os

class UserAlgorithmsBuild(stresstesting.MantidStressTest):

    build_success = False

    def skipTests(self):
        " We skip this test if the system is not Windows."
        if sys.platform.startswith('win'):
          return False
        else:
          return True

    def runTest(self):
        """
            System test for testing that the UserAlgorithm build script works
        """
        # Before we start remove the old build files as they seem to
        # cause random failures on Win7
        install_dir = r'C:\MantidInstall\plugins'
        lib_name = 'UserAlgorithms'
        exts = ['.dll', '.exp', '.lib']
        for ext in exts:
            try:
                os.remove(os.path.join(install_dir, lib_name + ext))
            except OSError:
                pass
        # Run the build
        import subprocess
        retcode = subprocess.call(["C:\\MantidInstall\\UserAlgorithms\\build.bat","--quiet"])
        if retcode == 0:
          self.build_success = True
        else:
          self.build_success = False        
                
    def validate(self):
        return self.build_success
