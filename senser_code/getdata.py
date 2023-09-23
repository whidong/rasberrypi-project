import mysql.connector
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# MySQL 연결 설정
db_config = {
    'host': '',
    'port': '',
    'user': '',
    'password': '',
    'database': ''
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    # MySQL 데이터베이스에 연결
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 데이터 쿼리
    query = "SELECT date, value FROM your_table"
    cursor.execute(query)
    data = cursor.fetchall()

    # 데이터베이스 연결 종료
    cursor.close()
    conn.close()

    # 데이터를 JSON 형식으로 반환
    data_list = [{"date": str(row[0]), "value": row[1]} for row in data]
    return jsonify(data_list)

if __name__ == '__main__':
    app.run()
