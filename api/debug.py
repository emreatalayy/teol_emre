from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        # Test environment variables
        api_key = os.getenv('GEMINI_API_KEY')
        
        response_data = {
            "status": "debug_test",
            "api_key_exists": bool(api_key),
            "api_key_length": len(api_key) if api_key else 0,
            "api_key_prefix": api_key[:10] if api_key else "None",
            "environment_vars": list(os.environ.keys())[:5]  # İlk 5 env var
        }
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return