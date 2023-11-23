import socket
import sys

MAX_SIZE = 4194304
CURSOR = "㉿$q!>>"
EXIT_COMMAND = "나가기."
HELP_COMMAND = "도움말."
RUN_MESSAGE = """
KorSQL 터미널에 오신 것을 환영합니다.

Copyright (c) 구자현.
여러 RDBMS의 SQL언어들은 영어로만 이루어져 있으며 외워야 하는 문법 또한 많아서
사용하기 쉽지 않기에 한글로 데이터베이스를 조작할 수 있는 SQL언어를 개발하였습니다.

도움말을 보려면 '도움말.'를 입력합니다.
"""


class Server:
    def __init__(self, server_ip: str, server_port: int):
        self.ip = server_ip
        self.port = server_port
        self.address = (self.ip, self.port)


class KorSqlClient:
    def __init__(self, connect_server: Server):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = connect_server
        self.cursor = CURSOR
        self.max_size = MAX_SIZE
        self.socket.connect(self.server.address)

    def run(self):
        while True:
            command = input(self.cursor).strip()
            if command != '':
                if command == EXIT_COMMAND:
                    sys.exit()
                if command == HELP_COMMAND:
                    print("""[HELP]
                    - ㉿$q!>> 데이터베이스 목록 조회하기 : 데이터베이스 목록을 조회하는 명령어
                    - ㉿$q!>> {데이터베이스명} 데이터베이스 생성하기 : 데이터베이스를 생성하는 명령어
                    - ㉿$q!>> {데이터베이스명} 데이터베이스 사용하기 : 데이터베이스를 선택하여 사용하는 명령어
                    - ㉿$q!>> {데이터베이스명} 데이터베이스 삭제하기 : 데이터베이스를 삭제하는 명령어
                    - ㉿$q!>> 테이블 목록 조회하기 : 테이블 목록을 조회하는 명령어
                    - ㉿$q!>> {테이블명} 테이블 삭제하기 : 테이블을 삭제하는 명령어
                    - ㉿$q!>> {테이블명} 테이블 속성 조회하기 : 테이블 속성을 조회하는 명령어
                    - ㉿$q!>> {테이블명} 테이블 생성하기 [속성1:자료형1,속성2:자료형2…]  : 테이블을 생성하는 명령어
                    - ㉿$q!>> {테이블명} 테이블 값 추가하기 [속성1:값1,속성2:값2…] : 테이블에 값을 추가하는 명령어
                    - ㉿$q!>> {테이블명} 테이블 값 조회하기 [속성1,속성2…] [조건1,조건2…] : 테이블 값을 조회하는 명령어""")
                self.socket.send(bytes(command.encode()))
                receive = self.socket.recv(self.max_size).decode()
                if receive == "":
                    print("없음.")
                else:
                    print(receive)


ip, port = input("server: ").split(":")
client = KorSqlClient(Server(ip, int(port)))
print(RUN_MESSAGE)
client.run()