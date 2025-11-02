from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Backend is running!'})

@app.route('/api/example', methods=['GET'])
def get_example():
    return jsonify({
        'message': 'This is an example GET endpoint',
        'data': []
    })

@app.route('/api/example', methods=['POST'])
def post_example():
    data = request.get_json()
    return jsonify({
        'message': 'Data received successfully',
        'received': data
    }), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
