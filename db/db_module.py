import mysql.connector
from mysql.connector import pooling

class Database:
    def __init__(self, config):
        # Collection을 utf8mb4_general_ci로 설정
        config['charset'] = 'utf8mb4'
        config['collation'] = 'utf8mb4_general_ci'

        # Connection Pool 설정
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,
            **config
        )
    
    def execute_query(self, query, params=None):
        try:
            # Connection Pool에서 연결 가져오기
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()

            # 쿼리 실행
            cursor.execute(query, params)

            # 결과 가져오기 (선택사항: SELECT일 경우)
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
            else:
                connection.commit()
                result = None
            
            # 커서 및 연결 닫기
            cursor.close()
            connection.close()

            return result
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None