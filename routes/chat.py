"""chat.py — Chatbot page route."""
from flask import Blueprint, render_template
chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/")
def chat_page():
    return render_template("chatbot.html")
