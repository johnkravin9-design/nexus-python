from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "🚀 Nexus Test Server is Working!"

if __name__ == '__main__':
    print("Testing basic Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
