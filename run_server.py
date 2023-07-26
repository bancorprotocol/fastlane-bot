__VERSION__ = "2.0"
__DATE__ = "18/May/2023"

from flask import Flask, Response
import json

app = Flask(__name__)
@app.route('/')
def monitor():
    return f"""
    <h1>Monitoring Server</h1>
    v{__VERSION__} [{__DATE__}]
    <br/>
    <ul>
        <li><a href='/latest'>Latest</a></li> 
        <li><a href='/bypair'>By Pair</a></li>
        <li><a href='/long'>Long</a></li>
        <li><a href='/all'>All</a></li>
        <li><a href='/json'>JSON</a></li>
    </ul>
    """

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

INNERHTML = """
<a id="{title}"></a>
<h2>{title}</h2>
<pre>
{text}
</pre>
<hr/>
"""
HTML = """
{menu}
{inner}
"""
@app.route('/bypair')
def monitor_bypair():
    with open("./monitoring.json", "r") as f:
        data = json.loads(f.read())
    out_by_pair = data['out_by_pair']
    inner = "\n".join([
        INNERHTML.format(text=txt, title=pair)
        for pair, txt in out_by_pair.items()
    ])
    menu = "\n".join([
        "<li><a href='#{pair}'>{pair}</a></li>".format(pair=pair)
        for pair, txt in out_by_pair.items()
    ])
    menu = "<ul>\n{}\n</ul>\n<hr/>\n".format(menu)
    html = HTML.format(menu=menu, inner=inner)
    return Response(html, mimetype='text/html')

@app.route('/json')
def monitor_json():
    with open("./monitoring.json", "r") as f:
        data = json.loads(f.read()) 
    return data

@app.route('/long')
def monitor_long():
    with open("./monitoring.latest.log", "r") as f:
        text = f.read()
    return Response(text, mimetype='text/plain')  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
