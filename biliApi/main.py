import os
from flask import Flask, jsonify, render_template, request, url_for, send_from_directory
import requests as rq
from werkzeug.utils import secure_filename
from werkzeug.urls import url_encode

IS_SERVERLESS = bool(os.environ.get('SERVERLESS'))
print(IS_SERVERLESS)

app = Flask(__name__)

@app.route("/playurl", methods=["GET"])
def proxyGet():
    host = "https://api.bilibili.com/pgc/player/web/playurl"
    res = rq.get(f"{host}?{url_encode(request.args)}")
    return res.content

# 启动服务，监听 9000 端口，监听地址为 0.0.0.0
app.run(debug=IS_SERVERLESS != True, port=9000, host='0.0.0.0')