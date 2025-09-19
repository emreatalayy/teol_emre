# 🎬 Avatar Video Dosyası

## 📋 Gereksinimler

**Dosya Konumu**: `static/ai-avatar.mp4`
**Format**: MP4 Video
**Önerilen Özellikler**:
- Boyut: 200x200 px (kare format)
- FPS: 24-30 
- Codec: H.264
- Süre: 2-5 saniye (loop)
- Ses: Yok (muted)

## 🔄 Çalışma Mantığı

1. **Varsayılan**: Video gizli
2. **TTS Başlar**: Video görünür + oynat
3. **TTS Biter**: Video durdur + gizle

## 📝 Notlar

- Video loop modunda çalışır
- Border-radius ile yuvarlak görünür
- Object-fit: cover ile kare formatta gösterilir
- Hover efekti ile büyür (scale 1.05)

## 🎯 Test

1. TTS mesaj yaz
2. "Oku" butonuna tıkla
3. Avatar videosu başlamalı
4. TTS bitince video durmalı
