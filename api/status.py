from flask import Flask, jsonify

app = Flask(__name__)

def handler(request):
    return jsonify({
        "status": "online", 
        "message": "TEOL AI Asistan API çalışıyor",
        "model": "gemini-1.5-flash"
    })