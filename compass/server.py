from flask import Flask, request, Response
from flask import send_file

import sys

app = Flask(__name__)


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/save", methods=["POST"])
def save():
    print(request.content_type)
    json = request.json
    text = "".join(f"{','.join(map(str,row))}\n" for row in json)
    with open("data/" + sys.argv[1], "a") as f:
        f.write(text)
    print(text)

    return Response()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
