class ChatBot {
    constructor() {
        this.initializeElements();
        this.initializeSpeechRecognition();
        this.initializeSpeechSynthesis();
        this.setupEventListeners();
        this.isRecording = false;
        this.isTyping = false;
        this.currentUtterance = null;
        
        // Gemini API ayarları
        this.apiKey = null;
        this.apiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';
        this.conversationHistory = [];
        
        // API anahtarını kontrol et
        this.checkApiKey();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.micButton = document.getElementById('micButton');
        this.speakButton = document.getElementById('speakButton');
        this.stopSpeakButton = document.getElementById('stopSpeakButton');
        this.recordingIndicator = document.getElementById('recordingIndicator');
        this.stopRecording = document.getElementById('stopRecording');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.settingsButton = document.getElementById('settingsButton');
        this.settingsPanel = document.getElementById('settingsPanel');
        this.closeSettings = document.getElementById('closeSettings');
        this.voiceSelect = document.getElementById('voiceSelect');
        this.speechRate = document.getElementById('speechRate');
        this.speechPitch = document.getElementById('speechPitch');
        this.rateValue = document.getElementById('rateValue');
        this.pitchValue = document.getElementById('pitchValue');
        this.apiKeyInput = document.getElementById('apiKeyInput');
        this.saveApiKey = document.getElementById('saveApiKey');
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'tr-TR';
            
            this.recognition.onstart = () => {
                this.isRecording = true;
                this.micButton.classList.add('recording');
                this.recordingIndicator.classList.add('show');
                this.updateStatus('Dinliyorum...', '#ef4444');
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.messageInput.value = transcript;
                this.sendMessage();
            };

            this.recognition.onerror = (event) => {
                console.error('Ses tanıma hatası:', event.error);
                this.stopRecordingAnimation();
                this.updateStatus('Ses tanıma hatası', '#ef4444');
                setTimeout(() => this.updateStatus('Hazır', '#4ade80'), 2000);
            };

            this.recognition.onend = () => {
                this.stopRecordingAnimation();
            };
        } else {
            console.warn('Tarayıcınız ses tanıma özelliğini desteklemiyor');
            this.micButton.style.display = 'none';
        }
    }

    initializeSpeechSynthesis() {
        if ('speechSynthesis' in window) {
            this.synthesis = window.speechSynthesis;
            this.loadVoices();
            
            // Sesler yüklendiğinde tekrar kontrol et
            this.synthesis.onvoiceschanged = () => {
                this.loadVoices();
            };
        } else {
            console.warn('Tarayıcınız sesli okuma özelliğini desteklemiyor');
            this.speakButton.style.display = 'none';
            this.stopSpeakButton.style.display = 'none';
        }
    }

    loadVoices() {
        const voices = this.synthesis.getVoices();
        this.voiceSelect.innerHTML = '';
        
        // Türkçe sesleri öncelik ver
        const turkishVoices = voices.filter(voice => voice.lang.startsWith('tr'));
        const otherVoices = voices.filter(voice => !voice.lang.startsWith('tr'));
        
        [...turkishVoices, ...otherVoices].forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = `${voice.name} (${voice.lang})`;
            if (voice.lang.startsWith('tr') && !this.voiceSelect.value) {
                option.selected = true;
            }
            this.voiceSelect.appendChild(option);
        });
    }

    checkApiKey() {
        // Çevre değişkenlerinden API anahtarını al
        if (typeof GEMINI_API_KEY !== 'undefined') {
            this.apiKey = GEMINI_API_KEY;
        } else if (localStorage.getItem('gemini_api_key')) {
            this.apiKey = localStorage.getItem('gemini_api_key');
        } else {
            // API anahtarı yoksa kullanıcıdan iste
            this.promptForApiKey();
        }
        
        if (this.apiKey) {
            this.updateStatus('Gemini AI Bağlandı', '#4ade80');
        }
    }

    promptForApiKey() {
        const apiKey = prompt('Gemini API anahtarınızı girin (İsteğe bağlı - boş bırakırsanız demo modu çalışır):');
        if (apiKey && apiKey.trim()) {
            this.apiKey = apiKey.trim();
            localStorage.setItem('gemini_api_key', this.apiKey);
            this.updateStatus('Gemini AI Bağlandı', '#4ade80');
        } else {
            this.updateStatus('Demo Modu', '#f59e0b');
        }
    }

    async callGeminiAPI(message) {
        if (!this.apiKey) {
            return this.getFallbackResponse(message);
        }

        try {
            this.updateStatus('Gemini AI düşünüyor...', '#3b82f6');
            
            // Konuşma geçmişini ekle
            this.conversationHistory.push({
                role: 'user',
                content: message
            });

            const requestBody = {
                contents: [{
                    parts: [{
                        text: `Sen yardımsever bir AI asistanısın. Türkçe konuş ve doğal bir şekilde yanıt ver. Kullanıcı mesajı: "${message}"`
                    }]
                }],
                generationConfig: {
                    temperature: 0.7,
                    maxOutputTokens: 1000,
                }
            };

            const response = await fetch(`${this.apiUrl}?key=${this.apiKey}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`API Hatası: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.candidates && data.candidates[0] && data.candidates[0].content) {
                const aiResponse = data.candidates[0].content.parts[0].text;
                
                // Konuşma geçmişine AI yanıtını ekle
                this.conversationHistory.push({
                    role: 'assistant',
                    content: aiResponse
                });

                this.updateStatus('Gemini AI Bağlandı', '#4ade80');
                return aiResponse;
            } else {
                throw new Error('Beklenmeyen API yanıtı');
            }

        } catch (error) {
            console.error('Gemini API Hatası:', error);
            this.updateStatus('API Hatası - Demo Modu', '#ef4444');
            
            // Hata durumunda demo yanıt ver
            return this.getFallbackResponse(message);
        }
    }

    getFallbackResponse(message) {
        // Demo yanıtları
        const responses = [
            "Bu çok ilginç bir soru! Size nasıl yardımcı olabilirim?",
            "Anlıyorum. Bu konuda size daha fazla bilgi verebilirim.",
            "Harika! Başka hangi konularda yardıma ihtiyacınız var?",
            "Bu gerçekten önemli bir konu. Detaylarına inmek ister misiniz?",
            "Mükemmel soru! Bu konuda elimde birkaç öneri var.",
            "Kesinlikle! Size bu konuda yardımcı olmaktan mutluluk duyarım.",
            "İyi düşünmüşsünüz. Bu yaklaşım gerçekten faydalı olabilir.",
            "Elbette! Bu konuda size rehberlik edebilirim."
        ];

        const lowerMessage = message.toLowerCase();
        
        if (lowerMessage.includes('merhaba') || lowerMessage.includes('selam') || lowerMessage.includes('hello')) {
            return "Merhaba! Size nasıl yardımcı olabilirim? Herhangi bir sorunuz varsa çekinmeden sorabilirsiniz.";
        }
        
        if (lowerMessage.includes('nasılsın') || lowerMessage.includes('naber')) {
            return "Ben bir AI asistanıyım, bu yüzden her zaman iyiyim! Peki siz nasılsınız? Size nasıl yardımcı olabilirim?";
        }
        
        if (lowerMessage.includes('isim') || lowerMessage.includes('kim')) {
            return "Ben Gemini AI tabanlı asistanınızım! Sizinle hem yazılı hem de sesli olarak iletişim kurabiliyorum. Hangi konularda yardıma ihtiyacınız var?";
        }
        
        if (lowerMessage.includes('teşekkür') || lowerMessage.includes('sağol') || lowerMessage.includes('thanks')) {
            return "Rica ederim! Size yardımcı olabildiğim için mutluyum. Başka ihtiyacınız olursa her zaman buradayım.";
        }
        
        if (lowerMessage.includes('görüşürüz') || lowerMessage.includes('bye') || lowerMessage.includes('hoşça kal')) {
            return "Görüşürüz! İyi günler dilerim. İhtiyacınız olduğunda tekrar buradayım!";
        }
        
        return responses[Math.floor(Math.random() * responses.length)];
    }

    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.micButton.addEventListener('click', () => this.toggleRecording());
        this.speakButton.addEventListener('click', () => this.speakLastMessage());
        this.stopSpeakButton.addEventListener('click', () => this.stopSpeaking());
        this.stopRecording.addEventListener('click', () => this.stopRecordingManually());
        this.settingsButton.addEventListener('click', () => this.toggleSettings());
        this.closeSettings.addEventListener('click', () => this.closeSettingsPanel());
        this.saveApiKey.addEventListener('click', () => this.saveApiKeyFromInput());
        
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });

        this.speechRate.addEventListener('input', (e) => {
            this.rateValue.textContent = e.target.value;
        });

        this.speechPitch.addEventListener('input', (e) => {
            this.pitchValue.textContent = e.target.value;
        });

        // Dışarıya tıklandığında ayarlar panelini kapat
        document.addEventListener('click', (e) => {
            if (!this.settingsPanel.contains(e.target) && 
                !this.settingsButton.contains(e.target) && 
                this.settingsPanel.classList.contains('show')) {
                this.closeSettingsPanel();
            }
        });
    }

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.autoResizeTextarea();
        
        // Bot yanıtını al
        this.simulateBotTyping();
        try {
            const response = await this.callGeminiAPI(message);
            this.addMessage(response, 'bot');
        } catch (error) {
            console.error('Mesaj gönderme hatası:', error);
            this.addMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'bot');
        } finally {
            this.stopTyping();
        }
    }

    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const currentTime = new Date().toLocaleTimeString('tr-TR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="message-content">
                <p>${content}</p>
                <span class="message-time">${currentTime}</span>
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    simulateBotTyping() {
        this.isTyping = true;
        this.updateStatus('Yazıyor...', '#f59e0b');
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    stopTyping() {
        this.isTyping = false;
        this.updateStatus('Hazır', '#4ade80');
        
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    toggleRecording() {
        if (this.isRecording) {
            this.stopRecordingManually();
        } else {
            this.startRecording();
        }
    }

    startRecording() {
        if (this.recognition) {
            try {
                this.recognition.start();
            } catch (error) {
                console.error('Ses tanıma başlatılamadı:', error);
            }
        }
    }

    stopRecordingManually() {
        if (this.recognition && this.isRecording) {
            this.recognition.stop();
        }
        this.stopRecordingAnimation();
    }

    stopRecordingAnimation() {
        this.isRecording = false;
        this.micButton.classList.remove('recording');
        this.recordingIndicator.classList.remove('show');
        this.updateStatus('Hazır', '#4ade80');
    }

    speakLastMessage() {
        const lastBotMessage = this.chatMessages.querySelector('.bot-message:last-of-type .message-content p');
        if (lastBotMessage && this.synthesis) {
            this.speakText(lastBotMessage.textContent);
        }
    }

    speakText(text) {
        if (!this.synthesis) return;
        
        // Önceki konuşmayı durdur
        this.synthesis.cancel();
        
        this.currentUtterance = new SpeechSynthesisUtterance(text);
        
        // Ayarları uygula
        const selectedVoice = this.synthesis.getVoices().find(voice => 
            voice.name === this.voiceSelect.value
        );
        if (selectedVoice) {
            this.currentUtterance.voice = selectedVoice;
        }
        
        this.currentUtterance.rate = parseFloat(this.speechRate.value);
        this.currentUtterance.pitch = parseFloat(this.speechPitch.value);
        
        this.currentUtterance.onstart = () => {
            this.speakButton.classList.add('active');
            this.updateStatus('Konuşuyor...', '#4ade80');
        };
        
        this.currentUtterance.onend = () => {
            this.speakButton.classList.remove('active');
            this.updateStatus('Hazır', '#4ade80');
        };
        
        this.synthesis.speak(this.currentUtterance);
    }

    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel();
            this.speakButton.classList.remove('active');
            this.updateStatus('Hazır', '#4ade80');
        }
    }

    toggleSettings() {
        this.settingsPanel.classList.toggle('show');
        // API anahtarını input'a yükle
        if (this.apiKey) {
            this.apiKeyInput.value = this.apiKey;
        }
    }

    saveApiKeyFromInput() {
        const newApiKey = this.apiKeyInput.value.trim();
        if (newApiKey) {
            this.apiKey = newApiKey;
            localStorage.setItem('gemini_api_key', this.apiKey);
            this.updateStatus('API Anahtarı Kaydedildi', '#4ade80');
            setTimeout(() => {
                this.updateStatus('Gemini AI Bağlandı', '#4ade80');
            }, 2000);
        } else {
            this.apiKey = null;
            localStorage.removeItem('gemini_api_key');
            this.updateStatus('Demo Modu', '#f59e0b');
        }
    }

    closeSettingsPanel() {
        this.settingsPanel.classList.remove('show');
    }

    updateStatus(text, color) {
        this.statusText.textContent = text;
        this.statusDot.style.background = color;
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Bot'u başlat
document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});

// Ses izinlerini kontrol et ve iste
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(() => {
        console.log('Mikrofon izni verildi');
    })
    .catch((error) => {
        console.warn('Mikrofon izni verilmedi:', error);
    });
