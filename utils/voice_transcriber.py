"""Voice transcription service using OpenAI Whisper."""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceTranscriber:
    """Transcribes voice messages using Whisper."""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize voice transcriber.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self._model = None
    
    def _load_model(self):
        """Load Whisper model lazily."""
        if self._model is None:
            try:
                import whisper
                logger.info(f"Loading Whisper model: {self.model_size}")
                self._model = whisper.load_model(self.model_size)
                logger.info("Whisper model loaded successfully")
            except ImportError:
                logger.error("Whisper not installed. Install with: pip install openai-whisper")
                raise
            except Exception as e:
                logger.error(f"Error loading Whisper model: {e}")
                raise
    
    async def transcribe(self, audio_file_path: str, language: str = "ru") -> Optional[str]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to audio file
            language: Expected language (ru/en)
            
        Returns:
            Transcribed text or None if transcription failed
        """
        try:
            # Load model if not loaded
            if self._model is None:
                self._load_model()
            
            if not os.path.exists(audio_file_path):
                logger.error(f"Audio file not found: {audio_file_path}")
                return None
            
            logger.info(f"Transcribing audio file: {audio_file_path}")
            
            # Map language codes
            whisper_lang = "ru" if language == "ru" else "en"
            
            # Transcribe
            result = self._model.transcribe(
                audio_file_path,
                language=whisper_lang,
                fp16=False  # Use FP32 for CPU compatibility
            )
            
            transcribed_text = result.get("text", "").strip()
            
            if transcribed_text:
                logger.info(f"Transcription successful: {transcribed_text[:50]}...")
                return transcribed_text
            else:
                logger.warning("Transcription returned empty text")
                return None
        
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}", exc_info=True)
            return None
    
    def is_available(self) -> bool:
        """Check if Whisper is available."""
        try:
            import whisper
            return True
        except ImportError:
            return False
