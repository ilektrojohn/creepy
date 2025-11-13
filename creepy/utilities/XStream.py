import sys
from PyQt4.QtCore import QObject, pyqtSignal


class XStream(QObject):
    """
    Shamelessly copied over from
    https://stackoverflow.com/questions/24469662/how-to-redirect-logger-output-into-pyqt-text-widget
    by https://stackoverflow.com/users/2073595/dano
    """
    _stdout = None
    _stderr = None
    messageWritten = pyqtSignal(str)

    def flush(self):
        pass

    def fileno( self ):
        return -1

    def write(self, msg):
        if not self.signalsBlocked():
            self.messageWritten.emit(unicode(msg))

    @staticmethod
    def stdout():
        if not XStream._stdout:
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        if not XStream._stderr:
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr
