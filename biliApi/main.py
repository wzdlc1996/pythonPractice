import os
from flask import Flask, jsonify, render_template, request, url_for, send_from_directory, Response
import requests as rq
from werkzeug.utils import secure_filename
from werkzeug.urls import url_encode
import json

IS_SERVERLESS = bool(os.environ.get('SERVERLESS'))
print(IS_SERVERLESS)

app = Flask(__name__)

@app.route("/playurl")
def proxyGet():
    host = "https://api.bilibili.com/pgc/player/web/playurl"
    preHeaders = dict(request.headers)

    exclude_in_headers = ["host", "Host", "X-Forwarded-For", "x-forwarded-for"]
    in_head = {k: v for k, v in preHeaders.items() if k not in exclude_in_headers}
    in_head["Referer"] = "https://api.bilibili.com"
    r = rq.request(request.method, url=f"{host}?{url_encode(request.args)}", headers=in_head)

    exclude_out_headers = []
    postHeaders = r.raw.headers.items()
    out_headers = {k: v for k, v in postHeaders if k not in exclude_out_headers}
    res = Response(r.content, status=r.status_code, headers=out_headers)
    return res

# 启动服务，监听 9000 端口，监听地址为 0.0.0.0
app.run(debug=IS_SERVERLESS != True, port=9000, host='0.0.0.0')