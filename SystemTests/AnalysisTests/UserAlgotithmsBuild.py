import stresstesting
import sys

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
        import subprocess
        retcode = subprocess.call(["C:\\MantidInstall\\UserAlgorithms\\build.bat","--quiet"])
        if retcode == 0:
          self.build_success = True
        else:
          self.build_success = False        
                
    def validate(self):
        return self.build_success
