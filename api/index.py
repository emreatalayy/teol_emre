import json
import google.generativeai as genai
import os

def handler(request):
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    if request.method == 'GET':
        # Status endpoint
        return (json.dumps({
            "status": "online",
            "message": "TEOL AI Assistant API is running",
            "version": "1.0.0"
        }), 200, headers)
    
    if request.method == 'POST':
        try:
            # Configure Gemini AI
            API_KEY = os.getenv('GEMINI_API_KEY')
            if not API_KEY:
                return (json.dumps({'error': 'API key not configured'}), 500, headers)
            
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Get message from request
            data = request.get_json()
            user_message = data.get('message', '') if data else ''
            
            if not user_message:
                return (json.dumps({'error': 'Message cannot be empty'}), 400, headers)
            
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
            
            return (json.dumps({'response': response.text}), 200, headers)
            
        except Exception as e:
            return (json.dumps({'error': f'Server error: {str(e)}'}), 500, headers)
    
    return (json.dumps({'error': 'Method not allowed'}), 405, headers)