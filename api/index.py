from http.server import BaseHTTPRequestHandler
import json
import google.generativeai as genai
import os

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
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
            "message": "TEOL AI Assistant API is running",
            "version": "1.0.0"
        }
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return
    
    def do_POST(self):
        try:
            # Configure Gemini AI
            API_KEY = os.getenv('GEMINI_API_KEY')
            if not API_KEY:
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'API key not configured'}).encode('utf-8'))
                return
            
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Get message from request
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_message = data.get('message', '')
            
            if not user_message:
                self.send_response(400)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Message cannot be empty'}).encode('utf-8'))
                return
            
            # System prompt for TEOL
            system_prompt = """You are the AI assistant for TEOL Language Schools. TEOL was selected as Turkey and Europe's highest quality language school in 2013 and 2014, and won the title of world's best language school in 2014.

Information about TEOL:
- 14 branches in Turkey: Adana, Ankara, Bursa, Bodrum, Eskişehir, Erzurum, Fethiye, Giresun, İzmir, İzmit, İstanbul Europe, İstanbul Anatolia, Mersin, Rize, Sakarya, Samsun, Trabzon
- 1 branch in England
- Modern teaching methods
- Student-centered approach
- Personalized learning process
- Strong teaching staff
- Innovative teaching materials

You are a friendly, helpful and professional assistant. You provide information about language learning, courses, and TEOL services. You speak English and communicate naturally. Be polite and professional in your responses."""
            
            # Generate response
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
            response = model.generate_content(full_prompt)
            
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'response': response.text}).encode('utf-8'))
            return
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'Server error: {str(e)}'}).encode('utf-8'))
            return