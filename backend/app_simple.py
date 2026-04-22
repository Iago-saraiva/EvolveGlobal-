from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/teste', methods=['GET'])
def teste():
    return jsonify({'message': 'API funcionando!'}), 200

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello World!'}), 200

if __name__ == '__main__':
    print("🚀 Servidor de teste iniciando...")
    print("📱 Acesse: http://localhost:5000/api/teste")
    app.run(debug=True, host='0.0.0.0', port=5000)