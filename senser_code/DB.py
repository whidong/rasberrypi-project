import pymysql as pysql


class Database:
    def __init__(self):
        self.db = pysql.connect(
            host="",
            port=1,
            user="",
            password="",
            db="",
            charset="",
        )
        self.cursor = self.db.cursor()  # 커서생성
        self.check_table()

    def check_table(self):
        self.cursor.execute("SHOW TABLES LIKE 'sensor'")
        result = self.cursor.fetchall()
        if not result:
            self.create_table()

    def create_table(self):
        create_table_sql = """
            CREATE TABLE sensor (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME,
                H2 FLOAT,
                CH4 FLOAT,
                Water_temp FLOAT
            );
        """
        self.cursor.execute(create_table_sql)
        self.db.commit()
        print("Table 'sensor' created")

    def show(self):
        sql = """ SELECT * from sensor """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    def insert(self, timestamp, H2, CH4,Water_temp):
        sql = """insert into sensor (timestamp, H2, CH4,Water_temp) values (%s, %s, %s, %s)"""
        self.cursor.execute(sql, (timestamp, H2, CH4, Water_temp))
        self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()


if __name__ == "__main__":
    db = Database()
    db.show()
