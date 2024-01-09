from flask import Flask

from src.zwickfi import zwickfi

app = Flask(__name__)

@app.route('/')
def index():
    zwickfi()
    return "Task executed", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
