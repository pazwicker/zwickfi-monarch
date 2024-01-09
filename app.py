from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    subprocess.run(["python3.11", "./src/zwickfi/zwickfi.py"])
    return "Task executed", 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
