import argparse
import datetime
import logging
import json
import api
import re

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from websocket import WebSocket
from cmd_type import CHZZK_CHAT_CMD

from pythonui import Ui_MainWindow
import random

class Popup(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vote Result")
        self.setFixedSize(500,200)
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 500, 200)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(50)
        self.label.setFont(font)

    def setText(self, text):
        self.label.setText(text)


class QTWindow(QMainWindow):
    statusbarLog = 'connecting...'
    chatLog = ''
    canVote = False
    m_UserList = []
    clickIndex = 0
    
    def __init__(self, streamer, cookies, logger):
        super().__init__()
        self.pop = Popup()
        self.initUI()
        self.statusBar().showMessage(self.statusbarLog)
        self.timer = QTimer(self)
        self.timer.start(100)
        self.timer.timeout.connect(self.timeout)
        self.chat = ChzzkChat(streamer,cookies,logger)
        self.chat.start()
        self.statusbarLog = 'connected'
            
    def timeout(self):
        self.statusBar().showMessage(self.statusbarLog)
        self.main_ui.Chatbox.setText(self.chatLog)
        

    def initUI(self):
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self)
        self.move(300,300)

        self.main_ui.addbt.clicked.connect(self.clkAddList)

        self.main_ui.votebt.clicked.connect(self.clkVoteBT)

        self.main_ui.startbt.clicked.connect(self.clkVoteStart)
        self.main_ui.stopbt.clicked.connect(self.clkVoteEnd)
        self.main_ui.stopbt.setEnabled(False)

        self.main_ui.listWidget.clicked.connect(self.clkList)
        
    def clkAddList(self):
        if self.canVote == True:
            return
        result = self.main_ui.addVotelist.toPlainText().replace(" ", "")
        if not result:
            self.main_ui.addVotelist.setPlainText('')
            return
        if self.main_ui.listWidget.count()+1 == 10:
            return
        listAdd = str(self.main_ui.listWidget.count()+1)
        listAdd += '. ' + self.main_ui.addVotelist.toPlainText()
        self.main_ui.listWidget.addItem(listAdd)
        self.main_ui.addVotelist.setPlainText('')

    def clkVoteStart(self):
        self.canVote = True
        self.main_ui.startbt.setEnabled(False)
        self.main_ui.stopbt.setEnabled(True)

    def clkVoteEnd(self):
        self.canVote = False
        self.main_ui.stopbt.setEnabled(False)
        self.main_ui.startbt.setEnabled(True)

    def clkVoteBT(self):
        if self.canVote == True:
            return
        a = self.main_ui.UserList.currentRow()
        if a == 0:
            return
        
        if len(self.m_UserList) == 0:
            return
        
        data_list = []
        for (index, username, value) in self.m_UserList:
            if str(index) == str(self.clickIndex):
                data_list.append((username,value))

        temp = 0
        for (username, value) in data_list:
            if int(value) > int(temp):
                temp = value

        for (username, value) in data_list:
            if str(value) == str(temp):
                self.m_UserList.remove((str(self.clickIndex), str(username), str(value)))
                self.pop.setText(str(username))
                self.pop.show()
                break

    def clkList(self):
        if self.canVote == True:
            return
        self.clickIndex = self.main_ui.listWidget.currentRow() + 1
        self.main_ui.UserList.clear()
        for (index, username, value) in self.m_UserList:
            if int(index) == int(self.clickIndex):
                self.main_ui.UserList.insertItem(0, username)


    def AddUser(self, username, index):
        _uname = username
        for (_index, _username, _value) in self.m_UserList:
            if str(index) == str(_index):
                print(_index)
                if str(username) == str(_username):
                    print(_username)
                    return
            else:
                if str(username) == str(_username):
                    self.m_UserList.remove((str(_index), str(_username), str(_value)))
        self.m_UserList.append((str(index), str(_uname), str(random.randrange(0,100))))


class ChzzkChat(QThread):

    def __init__(self, streamer, cookies, logger):
        super().__init__()

        self.streamer = streamer
        self.cookies  = cookies
        self.logger   = logger

        self.sid           = None
        self.userIdHash    = api.fetch_userIdHash(self.cookies)
        self.chatChannelId = api.fetch_chatChannelId(self.streamer)
        self.channelName   = api.fetch_channelName(self.streamer)
        self.accessToken, self.extraToken = api.fetch_accessToken(self.chatChannelId, self.cookies)

        self.connect()


    def connect(self):

        self.chatChannelId = api.fetch_chatChannelId(self.streamer)
        self.accessToken, self.extraToken = api.fetch_accessToken(self.chatChannelId, self.cookies)

        sock = WebSocket()
        sock.connect('wss://kr-ss1.chat.naver.com/chat')
        print(f'{self.channelName} 채팅창에 연결 중 .', end="")
        QTWindow.statusbarLog = 'connecting...'

        default_dict = {  
            "ver"   : "2",
            "svcid" : "game",
            "cid"   : self.chatChannelId,
        }

        send_dict = {
            "cmd"   : CHZZK_CHAT_CMD['connect'],
            "tid"   : 1,
            "bdy"   : {
                "uid"     : self.userIdHash,
                "devType" : 2001,
                "accTkn"  : self.accessToken,
                "auth"    : "SEND"
            }
        }

        sock.send(json.dumps(dict(send_dict, **default_dict)))
        sock_response = json.loads(sock.recv())
        self.sid = sock_response['bdy']['sid']
        print(f'\r{self.channelName} 채팅창에 연결 중 ..', end="")
        QTWindow.statusbarLog = 'connecting...'

        send_dict = {
            "cmd"   : CHZZK_CHAT_CMD['request_recent_chat'],
            "tid"   : 2,
            
            "sid"   : self.sid,
            "bdy"   : {
                "recentMessageCount" : 50
            }
        }

        sock.send(json.dumps(dict(send_dict, **default_dict)))
        sock.recv()
        print(f'\r{self.channelName} 채팅창에 연결 중 ...')
        QTWindow.statusbarLog = 'connecting...'

        self.sock = sock
        if self.sock.connected:
            print('연결 완료')
            QTWindow.statusbarLog = 'connected'
        else:
            raise ValueError('오류 발생')
        

    def send(self, message:str):

        default_dict = {  
            "ver"   : 2,
            "svcid" : "game",
            "cid"   : self.chatChannelId,
        }

        extras = {
            "chatType"          : "STREAMING",
            "emojis"            : "",
            "osType"            : "PC",
            "extraToken"        : self.extraToken,
            "streamingChannelId": self.chatChannelId
        }

        send_dict = {
            "tid"   : 3,
            "cmd"   : CHZZK_CHAT_CMD['send_chat'],
            "retry" : False,
            "sid"   : self.sid,
            "bdy"   : {
                "msg"           : message,
                "msgTypeCode"   : 1,
                "extras"        : json.dumps(extras),
                "msgTime"       : int(datetime.datetime.now().timestamp())
            }
        }

        self.sock.send(json.dumps(dict(send_dict, **default_dict)))


    def run(self):

        while True:
            try:
        
                try:
                    raw_message = self.sock.recv()

                except KeyboardInterrupt:
                    break 

                except:
                    self.connect()
                    raw_message = self.sock.recv()

                raw_message = json.loads(raw_message)
                chat_cmd    = raw_message['cmd']
                
                if chat_cmd == CHZZK_CHAT_CMD['ping']:

                    self.sock.send(
                        json.dumps({
                            "ver" : "2",
                            "cmd" : CHZZK_CHAT_CMD['pong']
                        })
                    )

                    if self.chatChannelId != api.fetch_chatChannelId(self.streamer): # 방송 시작시 chatChannelId가 달라지는 문제
                        self.connect()

                    continue
                
                if chat_cmd == CHZZK_CHAT_CMD['chat']:
                    chat_type = '채팅'

                elif chat_cmd == CHZZK_CHAT_CMD['donation']:
                    chat_type = '후원'

                else:
                    continue

                for chat_data in raw_message['bdy']:
                    
                    if chat_data['uid'] == 'anonymous':
                        nickname = '익명의 후원자'

                    else:
                        
                        try:
                            profile_data = json.loads(chat_data['profile'])
                            nickname = profile_data["nickname"]

                            if 'msg' not in chat_data:
                                continue

                        except:
                            continue

                    now = datetime.datetime.fromtimestamp(chat_data['msgTime']/1000)
                    now = datetime.datetime.strftime(now, '%Y-%m-%d %H:%M:%S')

                    self.logger.info(f'[{now}][{chat_type}] {nickname} : {chat_data["msg"]}')
                    QTWindow.chatLog += f'{nickname} : {chat_data["msg"]}' + '\n'
                    voteUsermsg = f'{chat_data["msg"]}'
                    a = voteUsermsg.find('!투표')
                    if a==0:
                        numbers = re.findall(r'\d+', voteUsermsg)
                        QTWindow.AddUser(QTWindow,f'{nickname}', numbers[0])
                
            except:
                pass
            

def get_logger():

    formatter = logging.Formatter('%(message)s')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler('chat.log', mode = "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--streamer_id', type=str, default='a3f9b654ff36bb29ab53eb38c25faab9')
    args = parser.parse_args()

    with open('d:\\workspace\\ChzzkChat\\ChzzkVotePy\\cookies.json') as f:
        cookies = json.load(f)

    logger = get_logger()
    app = QApplication(sys.argv)
    QTw = QTWindow(args.streamer_id, cookies, logger)
    QTw.show()
    app.exec_()
    #chzzkchat = ChzzkChat(args.streamer_id, cookies, logger)

    # 채팅창으로 메세지 보내기
    # mesaage = ' '
    # chzzkchat.send(message=mesaage)

    # 채팅 크롤링
    #chzzkchat.run()