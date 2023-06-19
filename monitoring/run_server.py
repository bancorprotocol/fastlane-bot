__VERSION__ = "2.1"
__DATE__ = "20/May/2023"

from flask import Flask, Response
import json
import os
import subprocess
from flask import jsonify
import click


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if error:
        raise Exception(f"Error occurred while running command: {error}")
    return output


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
        <li><a href='/notif'>notifications</a></li>
    </ul>
    """

@app.route('/all')
def monitor_all():
    filename = "Analysis_015.out"
    command = f"databricks fs cp dbfs:/FileStore/tables/carbonbot/logs/{filename} ."
    run_command(command)
    if not os.path.exists(filename):
        return Response("No log file found.", mimetype='text/plain')
    with open(filename, "r") as f:
        text = f.read()
    return Response(text, mimetype='text/plain')

@app.route('/latest')
def monitor_latest():
    filename = "Analysis_015.latest.out"
    command = f"databricks fs cp dbfs:/FileStore/tables/carbonbot/logs/{filename} ."
    run_command(command)
    if not os.path.exists(filename):
        return Response("No log file found.", mimetype='text/plain')
    with open(filename, "r") as f:
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
    filename = "Analysis_015.latest.json"
    command = f"databricks fs cp dbfs:/FileStore/tables/carbonbot/logs/{filename} ."
    run_command(command)
    if not os.path.exists(filename):
        return Response("No log file found.", mimetype='text/plain')
    with open(filename, "r") as f:
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
    filename = "Analysis_015.latest.json"
    command = f"databricks fs cp dbfs:/FileStore/tables/carbonbot/logs/{filename} ."
    run_command(command)
    if not os.path.exists(filename):
        return Response("No log file found.", mimetype='text/plain')
    with open(filename, "r") as f:
        data = json.loads(f.read())
    return jsonify(data)

@app.route('/notif')
def monitor_notif():
    filename = "Analysis_015.notifications"
    command = f"databricks fs cp dbfs:/FileStore/tables/carbonbot/logs/{filename} ."
    run_command(command)
    if not os.path.exists(filename):
        return Response("No log file found.", mimetype='text/plain')
    with open(filename, "r") as f:
        text = f.read()
    return Response(text, mimetype='text/plain')  

@app.route('/long')
def monitor_long():
    filename = "Analysis_015.latest.log"
    command = f"databricks fs cp dbfs:/FileStore/tables/carbonbot/logs/{filename} ."
    run_command(command)
    if not os.path.exists(filename):
        return Response("No log file found.", mimetype='text/plain')
    with open(filename, "r") as f:
        text = f.read()
    return Response(text, mimetype='text/plain')

@click.command()
@click.option('--host', default='https://<your-databricks-workspace-url>', help='Databricks host.')
@click.option('--token', default='<your-databricks-token>', help='Databricks token.')
def main(host, token):

    if 'DATABRICKS_HOST' not in os.environ:
        os.environ["DATABRICKS_HOST"] = host
        os.environ["DATABRICKS_TOKEN"] = token

    command = f"echo -e \"{host}\n{token}\" | databricks configure --token"
    run_command(command)
    app.run(host='0.0.0.0', port=80, debug=False)

if __name__ == '__main__':
    main()
