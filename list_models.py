import os
import requests

API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    # try reading from app.py default
    try:
        from app import API_KEY as APP_API_KEY
        API_KEY = APP_API_KEY
    except Exception:
        pass

if not API_KEY:
    print('No API_KEY found in environment or app.py. Set GEMINI_API_KEY env var or update app.py.')
    exit(1)

url = f'https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}'
resp = requests.get(url)

if resp.status_code != 200:
    print('ListModels failed:', resp.status_code, resp.text)
    exit(1)

data = resp.json()
models = data.get('models', [])
if not models:
    print('No models returned')
    exit(0)

print('Available models and supported methods:')
for m in models:
    name = m.get('name')
    meth = m.get('supportedGenerationMethods', m.get('supportedMethods', []))
    print('-', name, 'methods:', meth)

# print full JSON if needed
#print('\nFull response:\n', data)
