import sys
from PyQt5.QtCore import (pyqtSignal,  QObject,  Qt)
from PyQt5.QtWidgets import (QWidget, QTextEdit,  QLineEdit,  QApplication,  QVBoxLayout)
from PyQt5.QtGui import (QTextCursor, QColor, QPalette)

class ShellSignals(QObject):
    
    shellExec = pyqtSignal()
    #Signal used when user press enter in integrated Shell.
    shellCmd = pyqtSignal( str)
    
class ShellPromptLine(QLineEdit):
    """Prompt line used for custom integrated shell"""
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
    
    ##Static
    def convertIntoHex(convertible):
        if(type(convertible) is int) :
            return(hex(convertible))
        elif(type(convertible) is QColor):
            r = checkLenght(hex(convertible.red()))
            g = checkLenght(hex(convertible.green()))
            b = checkLenght(hex(convertible.blue()))
            print(r, g, b)
            return("#"+r+g+b)
    
    def buildHtmlFontBalist(color):
        chaine = "<FONT color =  "
        chaine += IntegratedShell.convertIntoHex(color)
        chaine +=">"
        return(chaine)
    
    def __init__(self):
        super().__init__()
        self.initShell()
        
    def initShell(self):
        
        ## Customization
        self.m_bgColor = QColor(26, 26, 26)
        self.m_bgPalette = QPalette(self.m_bgColor)
        #Color for Background Shell
        self.m_inColor = QColor(255, 170,  0)
        #Color for input User line
        self.m_outColor = QColor(0,  215, 0)
        #Color for shell return
        self.m_errorColor = QColor(234, 0, 0)
        #Color for error returns.
        
        self.m_shellInfoColor = QColor(255, 255, 255)
        self.m_edit = QTextEdit(self)
        self.displayInfoSlot( "##Welcome in Shell## ")
        self.m_edit.setReadOnly(True)
        
        self.m_lineEdit = ShellPromptLine(self)
        
        self.m_layout = QVBoxLayout(self)
        self.m_layout.addWidget(self.m_edit)
        self.m_layout.addWidget(self.m_lineEdit)
        self.setLayout(self.m_layout)
        
        
        
        
        ##setting colors :
        self.m_bgPalette.setColor(QPalette.Window, self.m_bgColor)
        self.m_edit.setAutoFillBackground(True)
        self.m_lineEdit.setAutoFillBackground(True)
        self.m_edit.setPalette(self.m_bgPalette)
        self.m_lineEdit.setPalette(self.m_bgPalette)
        
        ## Data :

        ##Signals :
        
        self.sigShell = ShellSignals()

 
        
        ##Connection
        self.m_lineEdit.sigShell.shellCmd.connect(self.rcvCmdSlot)



        
    def getSigTextChanged(self):
        return(self.m_edit.testChanged)
    

    ##Slots
    
    def displayInfoSlot(self,  text):
        """Print information about shell"""
        chaine = IntegratedShell.buildHtmlFontBalist(self.m_shellInfoColor)
        chaine += text
        chaine += "</FONT><br/>"
        self.m_edit.insertHtml(chaine)
        
    def rcvCmdSlot(self, text):
        """Used to receive and print text in the shell"""
        chaine = IntegratedShell.buildHtmlFontBalist(self.m_inColor)
        chaine += "<br/>>>> "
        chaine += text 
        chaine += "</FONT>"
        self.m_edit.insertHtml(chaine);

    def rcvOutSlot(self, text):
        """Used to receive and print text in the shell"""
        chaine = IntegratedShell.buildHtmlFontBalist(self.m_outColor)
        chaine += "<br/>"
        chaine += text 
        chaine += "</FONT>"
        self.m_edit.insertHtml(chaine);
        
    def rcvErrorSlot(self, text):
        """Used to receive and print text in the shell"""
        chaine = IntegratedShell.buildHtmlFontBalist(self.m_errorColor)
        chaine += "<br/>"
        chaine += text 
        chaine += "</FONT>"
        self.m_edit.insertHtml(chaine);
        

def checkLenght(data,  size = 2):
    """Force data having lenght size. Need to be used on hexa numbers.
    remove the Ox identifiers and force hexa being <= 255"""
    print(data)
    data = data[2:]
    print(data)
    if(len(data)< size):
        for i in range (0, size - len(data)):
            data = "0" + data
        return(data)
    elif(len(data) > size):
        return(data[:size])
    else :
        return(data)
    
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = IntegratedShell()
    ex.show()
    sys.exit(app.exec_())
    
    
    
