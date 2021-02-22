# coding: utf8

import os
import sys
import time
import json
import _thread
import hashlib
import pyperclip
import urllib.parse
import urllib.request
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QLabel, QGridLayout, QRadioButton, QButtonGroup, QPushButton

ICIBA_URL = 'http://fy.iciba.com/ajax.php?a=fy'
YOUDAO_URL = 'http://fanyi.youdao.com/translate?&doctype=json&type=AUTO&i={}'
translatemap = {}
# 保存软件运行期间的重复性 cache 内容，减少 api 请求
cacher = {}

class Container(QWidget):

    def __init__(self):
        super().__init__()
        self.tipLabel = QLabel('------------------------------------------------------------', self)
        self.resultLabel = QLabel('文本显示区', self)
        self.checkBox = QCheckBox('开启监听剪切板变化', self)
        self.copyButton = QPushButton('点击以拷贝音标到系统剪切板', self)
        self.label = QLabel('选中后监听系统剪切板，单词翻译后显示在最下方，当前剪切板内容：', self)

        self.radioGroup = QButtonGroup(self)
        self.resultLayout = QGridLayout()
        self.initUI()

        self.hiddenText = ""


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


        self.resultLayout.setSpacing(8)
        self.resultLayout.addWidget(self.label, 1, 0)
        self.resultLayout.addWidget(self.checkBox, 2, 0)
        self.resultLayout.addWidget(self.copyButton, 3, 0)
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
        text = '[{}]'.format(self.en)
        clipboard.setText(text)
        print("复制到剪切板成功：", self.en)
        self.label.setText('选中后监听系统剪切板，单词翻译后显示在最下方，当前剪切板内容：\n\t{}\n'.format(text))
        self.label.setWordWrap(True)

    def run(self):
        while True:
            time.sleep(3)
            raw = str(pyperclip.paste())
            if "[" in raw and "]" in raw:
                continue
            self.label.setText('选中后监听系统剪切板，单词翻译后显示在最下方，当前剪切板内容：{}\n'.format(raw))
            self.label.setWordWrap(True)
            raw = raw.strip(" ").strip("[").strip("]").strip("\n").strip("")
            # print("系统剪切板内容为：", raw)
            # 判断是否应该进行翻译
            if raw == "":
                continue
            # if len(raw.split(" ")) != 1:
            #     continue
            if not self.checkBox.isChecked():
                continue
            if _is_Chinese(raw):
                # continue 支持中英互译处理
                pass


            # 将翻译结果输出到界面上
            transdata = _translate(raw)
            print("raw=[{}], result=[{}]".format(raw, transdata))
            self.resultLabel.setText(transdata)



def _translate(raw):
    result = "抱歉，未能成功翻译\n(。・＿・。)ﾉI’m sorry~"
    if str(raw) == "" or len(raw) <=0:
        return

    # 软件生命周期内，已经缓存过的翻译记录重用
    key = md5(raw)
    if key in cacher.keys():
        return cacher.get(key)

    try:
        # python3 以后将 urlencode 更新成了 quote_plus
        data = urllib.parse.quote_plus(raw)
        reader = urllib.request.urlopen(YOUDAO_URL.format(data))
        print("请求源：", YOUDAO_URL.format(data))
        content = reader.read()
        res = json.loads(content)
        print(res)
        if "translateResult" in res.keys() and len(res["translateResult"]) >= 1 and len(res["translateResult"][0])>=1:
            tgt = str(res["translateResult"][0][0]["tgt"]).lstrip("b'").rstrip("'")
            result = "翻译结果：\n\t{}".format(tgt)
            cacher[key] = result
    except Exception as e:
        result = e
        pass
    # 输出最终翻译结果
    return result

def _is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def md5(raw):
    return hashlib.md5(str(raw).encode()).hexdigest()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    iconPath = os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'AppIcon.icns')
    app.setWindowIcon(QIcon(iconPath))
    container = Container()
    _thread.start_new_thread(container.run, ())
    sys.exit(app.exec_())
    # result = _translate("hello")
    # print(result)
