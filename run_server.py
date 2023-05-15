from flask import Flask, Response
app = Flask(__name__)
@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/all')
def monitor_all():
    with open("./monitoring.out", "r") as f:
        text = f.read()
    return Response(text, mimetype='text/plain')

@app.route('/latest')
def monitor_latest():
    with open("./monitoring.latest.out", "r") as f:
        text = f.read()
    return Response(text, mimetype='text/plain')   

@app.route('/long')
def monitor_long():
    with open("./monitoring.latest.log", "r") as f:
        text = f.read()
    return Response(text, mimetype='text/plain')  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
