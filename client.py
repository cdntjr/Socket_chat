import socket
import select
import sys
import msvcrt
import os, time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 8000)) # localhost

name = None
key_check = False
user_check = False
other_public_key = ""
other_user_name = ""


def generate_keys(): # 공개키와 개인키 만들기
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def encrypt_message(public_key, message): # 암호화
    rsa_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(rsa_key) # cipher 변수에는 암호화 객체 저장
    encrypted_message = cipher.encrypt(message.encode())
    return encrypted_message

def decrypt_message(private_key, encrypted_message):
    rsa_key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    decrypted_message = cipher.decrypt(encrypted_message).decode()
    return decrypted_message

private_key, public_key = generate_keys()

while True:
    read, write, fail = select.select((s, ), (), (), 1)
    if msvcrt.kbhit(): read.append(sys.stdin)

    for desc in read: 
        if desc == s: # 서버에서 온 메세지일 때
            data = s.recv(4096)

            if name is None: # 최초 접속일 때
                name = data.decode()
                s.send(public_key)
                print("키 받는 중...")
            
            else:
                if key_check == False: # 상대방 공개키 받기
                    other_public_key = data
                    print("키 받기 완료.\n\n")
                    key_check = True
                    print("유저 이름 받는 중...")
                    s.send("usernameaccess".encode())

                elif user_check == False: # 상대방 이름 받기
                    other_user_name = data.decode()
                    user_check = True
                    print("상대방의 이름을 받아왔습니다.\n\n")
                    time.sleep(0.5)
                    print("잠시 후에 화면이 리셋됩니다...\n\n")
                    time.sleep(3)
                    os.system('cls')
                    print("-------------------------------------------")
                    print(f'Your name is {name}')
                    print(f"{other_user_name} is connected!")
                    print("-------------------------------------------")
                        

                else: # 메세지 개인키로 해독
                    decrypted_message = decrypt_message(private_key, data)
                    print(decrypted_message)

        else: # 사용자가 입력했을 때 (메세지 전송)
            if key_check == True:
                msg = desc.readline()
                msg = msg.replace("\n", '')
                message = str(name) + " : " + str(msg)
                encrypted_message = encrypt_message(other_public_key, message)
                s.send(encrypted_message)

    