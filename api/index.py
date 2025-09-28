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
            # Debug info
            content_length = int(self.headers.get('Content-Length', 0))
            
            # API key check
            API_KEY = os.getenv('GEMINI_API_KEY')
            if not API_KEY:
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {
                    'error': 'API key not configured',
                    'debug': 'GEMINI_API_KEY environment variable not found'
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return
            
            # Import and configure genai
            try:
                import google.generativeai as genai
                genai.configure(api_key=API_KEY)
                model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as import_error:
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {
                    'error': 'Failed to configure AI model',
                    'debug': str(import_error)
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return
            
            # Read and parse request body
            try:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                user_message = data.get('message', '')
            except Exception as parse_error:
                self.send_response(400)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {
                    'error': 'Failed to parse request',
                    'debug': str(parse_error)
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return
            
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
            try:
                full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
                response = model.generate_content(full_prompt)
                
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'response': response.text}).encode('utf-8'))
                return
            except Exception as ai_error:
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {
                    'error': 'AI generation failed',
                    'debug': str(ai_error)
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return
            
        except Exception as general_error:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                'error': 'General server error',
                'debug': str(general_error)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
            return