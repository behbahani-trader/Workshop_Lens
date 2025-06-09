from flask import Flask, render_template
from app import create_app
from config import Config

app = create_app(Config)

@app.route('/')
def index():
    return render_template('main/index.html')

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 
