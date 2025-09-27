from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = json.dumps({
            "status": "healthy", 
            "message": "TEOL AI Assistant API is running",
            "model": "gemini-1.5-flash",
            "version": "1.0.0"
        }, ensure_ascii=False)
        
        self.wfile.write(response_data.encode('utf-8'))