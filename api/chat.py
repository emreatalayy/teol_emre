from http.server import BaseHTTPRequestHandler
import json
import google.generativeai as genai
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Configure Gemini AI
            API_KEY = os.getenv('GEMINI_API_KEY')
            if not API_KEY:
                self.send_error(500, "API key not configured")
                return
            
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_message = data.get('message', '')
            if not user_message:
                self.send_error(400, "Message cannot be empty")
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
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response_data = json.dumps({"response": response.text}, ensure_ascii=False)
            self.wfile.write(response_data.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()