from http.server import BaseHTTPRequestHandler
import json
import google.generativeai as genai
import os

# Configure API key once
API_KEY = os.getenv('GEMINI_API_KEY')
if API_KEY:
    genai.configure(api_key=API_KEY)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Check API key
            if not API_KEY:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "API key not configured"}).encode())
                return
            
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_message = data.get('message', '').strip()
            if not user_message:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Message cannot be empty"}).encode())
                return
            
            # Initialize model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
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
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response_data = json.dumps({"response": response.text}, ensure_ascii=False)
            self.wfile.write(response_data.encode('utf-8'))
            
        except Exception as e:
            # Error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_msg = json.dumps({"error": f"Server error: {str(e)}"})
            self.wfile.write(error_msg.encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()