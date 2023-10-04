from flask import Flask, request

app = Flask(__name__)

@app.route('/update', methods=['POST'])
def receive_post_data():
    if request.method == 'POST':
        data = request.get_json()
        print(f"Получены данные: {data}")
        return "Данные успешно приняты", 200

def run_server():
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    run_server()