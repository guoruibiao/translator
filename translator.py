# coding: utf8

import os
import sys
import time
import json
import _thread
import pyperclip
import urllib.parse
import urllib.request
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QLabel, QGridLayout, QRadioButton, QButtonGroup, QPushButton

ICIBA_URL = 'http://fy.iciba.com/ajax.php?a=fy'
translatemap = {}


class Container(QWidget):

    def __init__(self):
        super().__init__()
        self.tipLabel = QLabel('------------------------------------------------------------', self)
        self.resultLabel = QLabel('文本显示区', self)
        self.checkBox = QCheckBox('开启监听剪切板变化', self)
        self.copyButton = QPushButton('点击以拷贝音标到系统剪切板', self)
        self.enRadio = QRadioButton('英音', self)
        self.amRadio = QRadioButton('美音', self)
        self.label = QLabel('选中后监听系统剪切板，单词翻译后显示在最下方，当前剪切板内容：', self)

        self.radioGroup = QButtonGroup(self)
        self.resultLayout = QGridLayout()
        self.initUI()

        self.hiddenText = ""
        self.en = ""
        self.am = ""

    def initUI(self):
        """
                self.label.move(7, 3)
                self.checkBox.move(28, 28)
                # self.checkBox.toggle()
                self.checkBox.stateChanged.connect(self.changeTitle)

                self.showDialog.move(28, 50)
                self.showDialog.toggle()
                self.showDialog.stateChanged.connect(self.showMessageBox)

                self.tipLabel.move(7, 80)

                self.resultLabel.resize(250, 250)
                self.resultLabel.move(10, 100)
                self.resultLabel.setWordWrap(True)
                self.resultLabel.adjustSize()

                self.setGeometry(300, 300, 300, 150)

                self.setLayout(self.resultLayout)
                self.show()
        """
        self.resize(360, 200)
        self.setWindowTitle("🍒嘎嘣专用翻译小助手😜")
        self.checkBox.setCheckState(Qt.Unchecked)
        # self.setFixedSize(self.width(), self.height())
        # 将 APP 置于窗口最上层
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setMaximumHeight(450)

        self.checkBox.stateChanged.connect(self.changeTitle)
        self.copyButton.clicked.connect(self.copyToClipboard)

        self.resultLabel.setMinimumHeight(46)

        self.enRadio.setChecked(True)
        self.radioGroup.addButton(self.enRadio)
        self.radioGroup.addButton(self.amRadio)
        self.resultLayout.setSpacing(8)
        self.resultLayout.addWidget(self.label, 1, 0)
        self.resultLayout.addWidget(self.checkBox, 2, 0)
        self.resultLayout.addWidget(self.copyButton, 3, 0)
        self.resultLayout.addWidget(self.enRadio, 4, 0)
        self.resultLayout.addWidget(self.amRadio, 4, 1, 1, 1)
        self.resultLayout.addWidget(self.tipLabel, 5, 0)
        self.resultLayout.addWidget(self.resultLabel, 6, 0)
        self.setLayout(self.resultLayout)
        self.show()

    def changeTitle(self, state):
        if state == Qt.Checked:
            self.setWindowTitle("🍒嘎嘣专用翻译小助手😜 监听中...")
        else:
            self.setWindowTitle("🍒嘎嘣专用翻译小助手😜 未监听")

    def copyToClipboard(self):
        clipboard = QtGui.QGuiApplication.clipboard()
        if self.enRadio.isChecked() and self.en:
            text = '[{}]'.format(self.en)
            clipboard.setText(text)
            print("复制到剪切板成功：", self.en)
            self.label.setText('选中后监听系统剪切板，单词翻译后显示在最下方，当前剪切板内容：{}\n'.format(text))
        elif self.amRadio.isChecked() and self.am:
            text = '[{}]'.format(self.am)
            clipboard.setText(text)
            print("复制到剪切板成功：", self.am)
            self.label.setText('选中后监听系统剪切板，单词翻译后显示在最下方，当前剪切板内容：{}\n'.format(text))

    def run(self):
        while True:
            time.sleep(3)
            raw = str(pyperclip.paste())
            if "[" in raw and "]" in raw:
                continue
            self.label.setText('选中后监听系统剪切板，单词翻译后显示在最下方，当前剪切板内容：{}\n'.format(raw))
            raw = raw.strip(" ").strip("[").strip("]").strip("\n").strip("")
            # print("系统剪切板内容为：", raw)
            # 判断是否应该进行翻译
            if raw == "":
                continue
            if len(raw.split(" ")) != 1:
                continue
            if not self.checkBox.isChecked():
                continue
            if str(raw) == str(self.en) or str(raw) == str(self.am):
                continue
            if _is_Chinese(raw):
                continue
            print("[{}]".format(raw))

            # 弹出一个新的 dialog 框体; 监测系统剪切板是否有变化
            transdata = _translate(raw) if raw not in translatemap.keys() else translatemap[raw]
            self.en, self.am = '{}'.format(transdata["ph_en"]), '{}'.format(transdata["ph_am"])
            self.resultLabel.setWordWrap(True)
            self.resultLabel.adjustSize()
            mean = "英音音标：[{}]、美音音标：[{}]\n".format(self.en, self.am)
            word_mean = "、".join(transdata["word_mean"])
            mean = mean + word_mean

            self.resultLabel.setText(mean)



def _translate(raw):
    if str(raw) == "" or len(raw) <=0:
        return
    global translatemap
    data = {
        'f': 'auto',
        't': 'auto',
        'w': raw
    }
    data = urllib.parse.urlencode(data).encode("utf8")
    wy = urllib.request.urlopen(ICIBA_URL, data)
    html = wy.read()
    ta = json.loads(html)
    print(ta)
    result = {"ph_en": "未找到", "ph_am": "未找到", "word_mean":"未找到"}
    if ta is not {} and "status" in ta.keys() and ta["status"] == 0 and "content" in ta.keys():
        result = ta["content"]
    translatemap[raw] = result
    return result

def _is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    iconPath = os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'AppIcon.icns')
    app.setWindowIcon(QIcon(iconPath))
    container = Container()
    _thread.start_new_thread(container.run, ())
    sys.exit(app.exec_())
    # result = _translate("hello")
    # print(result)
