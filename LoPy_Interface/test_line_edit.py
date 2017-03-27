#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QWidget, QApplication,  QLabel

class Example(QWidget):

    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def initUI(self):
        
        ## Customization
        lbl1 = QLabel('Zetcode', self)
        lbl1.move(15, 10)
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Absolute')    
        self.show()        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())