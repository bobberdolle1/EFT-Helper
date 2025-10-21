"""Voice transcription service using Whisper via Ollama."""
import logging
import os
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceTranscriber:
    """Transcribes voice messages using Whisper via Ollama."""
    
    def __init__(self, model_size: str = "tiny", ollama_url: str = "http://localhost:11434"):
        """
        Initialize voice transcriber.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            ollama_url: URL of Ollama server
        """
        self.model_size = model_size
        self.ollama_url = ollama_url
        self.model_name = f"dimavz/whisper-{model_size}"
        self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def transcribe(self, audio_file_path: str, language: str = "ru") -> Optional[str]:
        """
        Transcribe audio file to text using Ollama.
        
        Args:
            audio_file_path: Path to audio file
            language: Expected language (ru/en)
            
        Returns:
            Transcribed text or None if transcription failed
        """
        try:
            if not os.path.exists(audio_file_path):
                logger.error(f"Audio file not found: {audio_file_path}")
                return None
            
            logger.info(f"Transcribing audio file via Ollama: {audio_file_path}")
            
            # Read audio file as base64
            import base64
            with open(audio_file_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode("utf-8")
            
            # Call Ollama API
            session = await self._get_session()
            
            payload = {
                "model": self.model_name,
                "prompt": audio_data,
                "stream": False
            }
            
            async with session.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    logger.error(f"Ollama API error: {response.status}")
                    return None
                
                result = await response.json()
                transcribed_text = result.get("response", "").strip()
            
            if transcribed_text:
                logger.info(f"Transcription successful: {transcribed_text[:50]}...")
                return transcribed_text
            else:
                logger.warning("Transcription returned empty text")
                return None
        
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}", exc_info=True)
            return None
    
    async def is_available(self) -> bool:
        """Check if Ollama Whisper is available."""
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.ollama_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    return self.model_name in models
                return False
        except Exception as e:
            logger.error(f"Error checking Ollama availability: {e}")
            return False
