from twisted.internet import protocol, reactor
import names
import time


COLORS = [
    '\033[31m',
    '\033[32m',
    '\033[33m',
    '\033[34m',
    '\033[35m',
    '\033[36m',
    '\033[37m',
    '\033[4m'
]

transports = []
users = []
colors = []
public_key = {}
get_public_key = False
user_name_access_provided = False


def send_public_key():
    transports[0].write(public_key[2])
    transports[1].write(public_key[1])

def send_user_name():
    transports[0].write(colors[1].encode() + users[1].encode() + "\033[0m".encode())
    transports[1].write(colors[0].encode() + users[0].encode() + "\033[0m".encode())


class Chat(protocol.Protocol):
    def connectionMade(self): # 사용자가 서버에 접속했을 때
        name = names.get_first_name()
        color = COLORS[len(users) % len(COLORS)] # 색깔 돌려쓰기
        colors.append(color)
        users.append(name)
        transports.append(self.transport)

        self.transport.write(f'{color}{name}\033[0m'.encode())

    def dataReceived(self, data): # 사용자가 서버에 메세지를 보냈을 때
        global get_public_key
        global user_name_access_provided
        for t in transports:
            if self.transport is not t: # 자신이 아닐때
                if get_public_key == True and user_name_access_provided == True and data.decode(encoding='latin-1') != "usernameaccess":
                    t.write(data)
            
            else: # 자신일때 (공개키와 유저 이름을 보내기)
                if get_public_key == False:
                    if public_key.get(1) == None:
                        public_key[1] = data
                    else:
                        public_key[2] = data
                        if len(public_key) == 2:
                            get_public_key = True
                            send_public_key()
                
                if user_name_access_provided == False and get_public_key == True and data.decode(encoding='latin-1') == "usernameaccess":
                    send_user_name()
                    user_name_access_provided = True
                    
                



class ChatFactory(protocol.Factory): # 통신 프로토콜 정의
    def buildProtocol(self, addr):
        return Chat()
    

print("server started!")
reactor.listenTCP(8000, ChatFactory()) # 8000번 포트 Listen
reactor.run()