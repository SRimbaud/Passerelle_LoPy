import sys
from PyQt5.QtCore import (pyqtSignal,  QObject,  Qt)
from PyQt5.QtWidgets import (QWidget, QTextEdit,  QLineEdit,  QApplication,  QVBoxLayout)
from PyQt5.QtGui import (QTextCursor, QColor, QPalette)

class ShellSignals(QObject):
    
    shellExec = pyqtSignal()
    #Signal used when user press enter in integrated Shell.
    shellCmd = pyqtSignal( str)
    
class ShellPromptLine(QLineEdit):
    def __init__(self,  parent):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        
        print("Création shellprompt")
        #signal
        
        self.sigShell = ShellSignals()
        
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        #Checking if enter key is pressed
        #When enter key is pressed automticly move cursor to end of line.
        #allow to select text enter by user.
        #It looks like there is a bug Qt.Key_Enter is 16777221 strange.
        if event.key() == Qt.Key_Enter or event.key()==16777220:

            self.sigShell.shellCmd.emit(self.displayText())
            self.clear()
        
class IntegratedShell(QWidget):
    
    commandMode = 1 #Mode set if user can enter a command
    executingMode = 0 #MOde set if user is waiting for execution of a command.
    def __init__(self):
        super().__init__()
        self.initShell()
        
    def initShell(self):
        
        ## Customization
        self.m_edit = QTextEdit( "##Welcome in Shell## ",  self)
        self.m_edit.setReadOnly(True)
        self.m_lineEdit = ShellPromptLine(self)
        self.m_layout = QVBoxLayout(self)
        self.m_layout.addWidget(self.m_edit)
        self.m_layout.addWidget(self.m_lineEdit)
        self.setLayout(self.m_layout)
        
        self.m_bgColor = QColor(26, 26, 26)
        self.m_bgPalette = QPalette(self.m_bgColor)
        #Color for Background Shell
        self.m_inColor = QColor(160, 160, 255)
        #Color for input User line
        self.m_outColor = QColor(255, 170,  0)
        #Color for shell return
        self.m_errorColor = QColor(234, 0, 0)
        #Color for error returns.
        
        ##setting colors :
        self.m_bgPalette.setColor(QPalette.Window, self.m_bgColor)
        self.m_edit.setAutoFillBackground(True)
        self.m_lineEdit.setAutoFillBackground(True)
        self.m_edit.setPalette(self.m_bgPalette)
        self.m_lineEdit.setPalette(self.m_bgPalette)
        
        ## Data :
        
        self.m_cursor = self.m_edit.textCursor()
        self.m_edit.moveCursor(QTextCursor.EndOfLine)
        #When we move cursor it moves anchor.
        #Cursor is after >>>
        self.m_mode = IntegratedShell.commandMode
        ##Signals :
        
        self.sigShell = ShellSignals()
        self.m_lineEdit.sigShell.shellCmd.connect(self.rcvCmdSlot)
 
        
        ##Connection
        
        self.sigShell.shellExec.connect(self.escapeKeySlot)
        self.m_edit.cursorPositionChanged.connect(self.checkCursorPosSlot)

        
    def getSigTextChanged(self):
        return(self.m_edit.testChanged)
    
    
    
    def getCommand(self):
        """Return Command enter by user. Return QString"""
        #It uses the anchor. This fucntion is called
        #by keyPressEvent.
        return(self.m_cursor.selectedText())
        
    ##Slots :
    def checkCursorPosSlot(self):
        """Slot used to check where the cursor is and if is not in the >>> line."""
        if self.m_cursor.position() < self.m_cursor.anchor() :
            self.m_cursor.setPosition(self.m_cursor.anchor(), mode=QTextCursor.KeepAnchor)
    
    
    def escapeKeySlot(self):
        """Define an action to do when entre key is pressed"""
        if( self.m_mode is IntegratedShell.commandMode):
            self.sigShell.emit(self.getCommand())
        else :
            return
            
    
    def rcvCmdSlot(self, text):
        """Used to receive and print text in the shell"""
        chaine = "<FONT color = #A0A0FF><br/>>>> "
        chaine += text 
        chaine += "</FONT>"
        self.m_edit.insertHtml(chaine);
      
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = IntegratedShell()
    ex.show()
    sys.exit(app.exec_())
    
    
    
