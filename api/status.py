from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response_data = {
            "status": "online",
            "message": "TEOL AI Assistant Status API",
            "version": "1.0.0"
        }
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return