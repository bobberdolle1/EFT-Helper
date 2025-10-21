"""Service for fetching Escape from Tarkov news."""
import logging
import aiohttp
import feedparser
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching and formatting EFT news."""
    
    # Official Escape from Tarkov RSS feed
    RSS_FEED_URL = "https://www.escapefromtarkov.com/news/rss"
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get_latest_news(self, lang: str = "ru", limit: int = 5) -> List[Dict]:
        """
        Get latest Escape from Tarkov news.
        
        Args:
            lang: Language (ru/en)
            limit: Maximum number of news items to return
            
        Returns:
            List of news items with title, description, link, date
        """
        try:
            session = await self._get_session()
            
            # Fetch RSS feed
            async with session.get(self.RSS_FEED_URL, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch news: HTTP {response.status}")
                    return []
                
                content = await response.text()
            
            # Parse RSS feed
            feed = feedparser.parse(content)
            
            if not feed.entries:
                logger.warning("No news entries found in RSS feed")
                return []
            
            # Format news items
            news_items = []
            for entry in feed.entries[:limit]:
                news_item = {
                    "title": entry.get("title", "No title"),
                    "description": self._clean_description(entry.get("summary", "")),
                    "link": entry.get("link", ""),
                    "date": self._parse_date(entry.get("published", ""))
                }
                news_items.append(news_item)
            
            logger.info(f"Fetched {len(news_items)} news items")
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}", exc_info=True)
            return []
    
    def _clean_description(self, description: str) -> str:
        """Clean HTML tags from description."""
        import re
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', description)
        # Remove extra whitespace
        clean_text = ' '.join(clean_text.split())
        # Limit length
        if len(clean_text) > 200:
            clean_text = clean_text[:197] + "..."
        return clean_text
    
    def _parse_date(self, date_str: str) -> str:
        """Parse and format date string."""
        try:
            from dateutil import parser
            dt = parser.parse(date_str)
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return date_str
    
    def format_news_message(self, news_items: List[Dict], language: str = "ru") -> str:
        """
        Format news items into a message.
        
        Args:
            news_items: List of news items
            language: Language (ru/en)
            
        Returns:
            Formatted message string
        """
        if not news_items:
            if language == "ru":
                return "❌ Не удалось загрузить новости Escape from Tarkov."
            else:
                return "❌ Failed to load Escape from Tarkov news."
        
        if language == "ru":
            header = "📰 **Последние новости Escape from Tarkov:**\n\n"
        else:
            header = "📰 **Latest Escape from Tarkov News:**\n\n"
        
        message = header
        
        for idx, item in enumerate(news_items, 1):
            message += f"{idx}. **{item['title']}**\n"
            if item['description']:
                message += f"   _{item['description']}_\n"
            if item['date']:
                message += f"   🕒 {item['date']}\n"
            message += f"   🔗 [Читать полностью]({item['link']})\n\n"
        
        return message
