import os
import asyncio
import edge_tts
import pygame
import time

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'audio')

if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

class VoiceEngine:
    def __init__(self):
        pygame.mixer.init()

    async def _generate_audio(self, text, voice, rate, pitch, filepath):
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(filepath)

    def speak(self, text, voice_config=None, filename="briefing.mp3"):
        """Converts text to speech using Edge TTS with custom rate and pitch."""
        filepath = os.path.join(AUDIO_DIR, filename)
        
        # Default fallback
        if voice_config is None:
            voice_config = {"base": "ko-KR-SunHiNeural", "rate": "+0%", "pitch": "+0Hz"}
        
        voice = voice_config.get("base", "ko-KR-SunHiNeural")
        rate = voice_config.get("rate", "+0%")
        pitch = voice_config.get("pitch", "+0Hz")
        
        # 1. Synthesis (Async to Sync)
        print(f"🎙️ Synthesizing voice: {voice} | Rate: {rate} | Pitch: {pitch}")
        asyncio.run(self._generate_audio(text, voice, rate, pitch, filepath))
        
        # 2. Playback
        print(f"🎙️ Playing voice: {filename}")
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ Playback error: {e}")
            os.system(f"start {filepath}")
        
        return filepath

if __name__ == "__main__":
    # Multi-Vocal Test Run
    engine = VoiceEngine()
    
    # 1. HanSu (Authoritative)
    engine.speak("데이터는 거짓말을 하지 않죠. 강한수입니다.", 
                 voice_config={"base": "ko-KR-InJoonNeural", "rate": "+5%", "pitch": "-5Hz"}, 
                 filename="test_hansu.mp3")
    
    # 2. Haena (Energetic)
    engine.speak("자, 마법을 부려볼까요? 그로스 스나이퍼 박해나입니다! ✨", 
                 voice_config={"base": "ko-KR-SunHiNeural", "rate": "+15%", "pitch": "+15Hz"}, 
                 filename="test_haena.mp3")
    
    # 3. JaeHyan (Deep & Conservative)
    engine.speak("비용 통제는 생존의 핵심입니다. 한재현입니다.", 
                 voice_config={"base": "ko-KR-HyunsuMultilingualNeural", "rate": "-10%", "pitch": "-20Hz"}, 
                 filename="test_jaehyun.mp3")
