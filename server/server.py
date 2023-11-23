import socket
import sys, os
import pymysql
import pandas
from tabulate import tabulate

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

DATABASE_HOST = 'localhost'
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'rnwkgus'

TABLE_TYPE = {
    "숫자": "INT",
    "문자": "VARCHAR(255)"
}

PORT = 6060

class KorSqlServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = PORT
        self.address = (self.ip, self.port)
        self.database = 'information_schema'

    def run(self):
        print(f"※STARTING※\nserver is starting......\n")
        self.server.bind(self.address)
        self.server.listen()
        print(f"※LISTENING※\nserver is listening on {self.ip}:{self.port}\n")
        conn, addr = self.server.accept()
        print(f"※NEW CONNECTION※\n{str(addr)} connected.\n")
        while True:
            receive = conn.recv(1024).decode()
            print(f"[RECEIVE] {receive}")
            data = self.parser(receive)
            if data == "":
                data = "없음."
            conn.send(bytes(data.encode()))

    def sql_handler(self, database: str, sql: str):
        connection = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PASSWORD, database=database)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql[1:])
                result = cursor.fetchall()
                cursor.close()
                result = pandas.DataFrame(result)
                # return tabulate(result, headers='keys', tablefmt='fancy_grid', showindex=True)  # excel table view
                return tabulate(result, headers='keys', tablefmt='psql', showindex=True) # mysql select window view
        except Exception as e:
            print(f'[ERROR] SQL 쿼리문 실행 실패. 에러: {str(e)}')
        finally:
            print(f"database: {database}, sql: {sql[1:]}")
            connection.commit()
            connection.close()
    def parser(self, command):
        command = command.split()
        for i in range(0, 7):
            command.append("")
        if command[0] == "데이터베이스" or command[1] == "데이터베이스":
            return self.database_command_parser(command)
        if command[0] == "테이블" or command[1] == "테이블":
            return self.table_command_parser(command)
        else:
            return "[ERROR] 명령어가 올바르지 않습니다."

    def database_command_parser(self, command):
        if command[2] == "조회하기": # 데이터베이스 목록 조회하기
            return self.sql_handler("information_schema", "/SHOW DATABASES;")
        elif command[2] == "생성하기": # {name} 데이터베이스 생성하기
            self.sql_handler(self.database, f"/CREATE DATABASE {command[0]};")
            return f"{command[0]} 데이터베이스가 생성되었습니다."
        elif command[2] == "사용하기": # {name} 데이터베이스 사용하기
            self.database = command[0]
            return f"{command[0]} 데이터베이스로 변경되었습니다."
        elif command[2] == "삭제하기": # {name} 데이터베이스 삭제하기
            self.sql_handler(self.database, f'/DROP DATABASE {command[0]};')
            self.database = 'information_schema'
            return f"{command[0]} 데이터베이스가 삭제되었습니다."
        else:
            return "[ERROR] 명령어가 올바르지 않습니다."

    def table_command_parser(self, command):
        if command[2] == "조회하기": # 테이블 목록 조회하기
            return self.sql_handler(self.database, "/SHOW TABLES;")
        if command[2] == "삭제하기": # {name} 테이블 삭제하기
            self.sql_handler(self.database, f"/DROP TABLE {command[0]};")
            return f"{command[0]} 테이블이 삭제되었습니다."
        if command[3] == "조회하기" and command[2] == "속성": # {name} 테이블 속성 조회하기
            return self.sql_handler(self.database, f"/DESC {command[0]};")
        if command[2] == "생성하기": # {name} 테이블 생성하기 [{속성1}:{자료형1},{속성2}:{자료형2}...]
            return self.create_table(command[3][1:-1].split(","), command[0])
        if command[3] == "삭제하기": # {name} 테이블 값 삭제하기 [{조건1},{조건2}...]
            self.sql_handler(self.database, f"/DELETE FROM {command[0]} WHERE {command[4][1:-1]};")
            return f"{command[0]} 테이블이 삭제되었습니다."
        if command[3] == "추가하기":  # {name} 테이블 값 추가하기 [{속성1}:{값1},{속성2}:{값2}...]
            return self.insert_value(command[4][1:-1].split(","), command[0])
        if command[3] == "조회하기" and command[2] == "값": # {name} 테이블 값 조회하기 [{속성1},{속성2}...] [{조건1},{조건2}...]
            if command[5][1:-1] == "":
                return self.sql_handler(self.database,f"/SELECT {command[4][1:-1]} FROM {command[0]};")
            return self.sql_handler(self.database, f"/SELECT {command[4][1:-1]} FROM {command[0]} WHERE {command[5][1:-1]};")
        # TODO: 수정하기 기능 추가
        else:
            return "[ERROR] 명령어가 올바르지 않습니다."

    def insert_value(self, command, table_name):
        items = [item.split(":") for item in command]
        if not items:
            return "[ERROR] 추가할 값이 없습니다."
        columns = [item[0] for item in items]
        values = [item[1] for item in items]
        self.sql_handler(self.database, f"/INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});")
        return f"{table_name} 테이블에 값이 추가되었습니다."

    def create_table(self, columns, table_name):
        column_definitions = []
        for column in columns:
            parts = column.split(":")
            if len(parts) == 2:
                column_name = parts[0].strip()
                data_type = parts[1].strip()
                if data_type in TABLE_TYPE:
                    data_type = TABLE_TYPE[data_type]
                column_definition = f"{column_name} {data_type}"
                column_definitions.append(column_definition)
        column_definitions.append("id INT AUTO_INCREMENT PRIMARY KEY")
        self.sql_handler(self.database, f"/CREATE TABLE {table_name} ({', '.join(column_definitions)});")
        return f"{table_name} 테이블이 생성되었습니다."

server = KorSqlServer()
server.run()