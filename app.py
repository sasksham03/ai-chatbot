from flask import Flask, jsonify, render_template, request

from chatbot import ChatBot

app = Flask(__name__)
bot = ChatBot()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", ""))[:500]
    return jsonify(bot.get_response(message))


if __name__ == "__main__":
    app.run(debug=True)
