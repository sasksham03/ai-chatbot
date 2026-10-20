"""CodeBuddy - NLP chatbot engine.

How it works:
1. All example sentences ("patterns") from intents.json are converted to
   TF-IDF vectors (word + character n-grams, so small typos still match).
2. The user's message is converted to the same vector space.
3. Cosine similarity finds the closest pattern; its intent supplies the reply.
4. If similarity is below THRESHOLD, a fallback reply is used.
"""

import ast
import json
import operator
import random
import re
from datetime import datetime
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack

BASE_DIR = Path(__file__).parent
THRESHOLD = 0.30

# ---------- safe calculator ----------
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("exponent too large")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")


def safe_calculate(expression: str):
    tree = ast.parse(expression, mode="eval")
    return _eval(tree.body)


def clean(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s'+\-*/%.^()]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


class ChatBot:
    def __init__(self, intents_file: str = "intents.json"):
        with open(BASE_DIR / intents_file, encoding="utf-8") as f:
            data = json.load(f)

        self.intents = {i["tag"]: i for i in data["intents"]}
        self.fallback = data["fallback"]

        self.patterns, self.tags = [], []
        for intent in data["intents"]:
            for p in intent["patterns"]:
                self.patterns.append(clean(p))
                self.tags.append(intent["tag"])

        self.word_vec = TfidfVectorizer(ngram_range=(1, 2))
        self.char_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
        word_m = self.word_vec.fit_transform(self.patterns)
        char_m = self.char_vec.fit_transform(self.patterns)
        self.matrix = hstack([word_m, char_m]).tocsr()

        self.user_name = None  # simple conversation memory

    # ---------- public API ----------
    def get_response(self, message: str) -> dict:
        message = (message or "").strip()
        if not message:
            return self._reply("Please type something and I'll try to help! 🙂", 1.0, "empty")

        # 1. remember the user's name
        m = re.search(r"\b(?:my name is|i am called|call me)\s+([A-Za-z]+)", message, re.I)
        if m:
            self.user_name = m.group(1).capitalize()
            return self._reply(f"Nice to meet you, {self.user_name}! 😊 How can I help?", 1.0, "name")

        if re.search(r"\b(what is my name|do you know my name|who am i)\b", message, re.I):
            if self.user_name:
                return self._reply(f"Your name is {self.user_name}!", 1.0, "name")
            return self._reply("I don't know your name yet. Tell me: 'my name is ...'", 1.0, "name")

        # 2. calculator
        m = re.search(r"(?:calculate|calc|solve|compute|what is|what's)?\s*([\d\s+\-*/%.^()]+)$", message.lower())
        if m and re.search(r"\d", m.group(1)) and re.search(r"[+\-*/%^]", m.group(1)):
            expr = m.group(1).replace("^", "**").strip()
            try:
                result = safe_calculate(expr)
                if isinstance(result, float):
                    result = round(result, 6)
                return self._reply(f"🧮 {m.group(1).strip()} = {result}", 1.0, "calculator")
            except Exception:
                return self._reply("I couldn't calculate that. Try something like 'calculate 12*8'.", 1.0, "calculator")

        # 3. NLP intent matching
        text = clean(message)
        vec = hstack([self.word_vec.transform([text]), self.char_vec.transform([text])]).tocsr()
        scores = cosine_similarity(vec, self.matrix)[0]
        best = int(scores.argmax())
        score = float(scores[best])

        if score < THRESHOLD:
            return self._reply(random.choice(self.fallback), score, "fallback")

        tag = self.tags[best]
        intent = self.intents[tag]
        reply = random.choice(intent["responses"])

        action = intent.get("action")
        if action == "time":
            reply = reply.format(time="🕒 It's " + datetime.now().strftime("%I:%M %p") + ".")
        elif action == "date":
            reply = reply.format(date="📅 Today is " + datetime.now().strftime("%A, %d %B %Y") + ".")

        if tag in ("greeting",) and self.user_name:
            reply = f"Hello again, {self.user_name}! 👋 What would you like to know?"

        return self._reply(reply, score, tag)

    @staticmethod
    def _reply(text, score, intent):
        return {"reply": text, "confidence": round(score, 2), "intent": intent}


if __name__ == "__main__":
    bot = ChatBot()
    print("CodeBuddy (type 'quit' to exit)")
    while True:
        user = input("You: ")
        if user.strip().lower() in {"quit", "exit"}:
            print("Bot: Goodbye!")
            break
        print("Bot:", bot.get_response(user)["reply"])
