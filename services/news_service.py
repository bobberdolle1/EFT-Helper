"""Service for fetching Escape from Tarkov news."""
import logging
import aiohttp
import feedparser
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching and formatting EFT news."""
    
    # Twitter/X via Nitter RSS (fallback instances)
    NITTER_INSTANCES = [
        "https://nitter.poast.org",
        "https://nitter.privacydev.net",
        "https://nitter.net",
    ]
    TWITTER_ACCOUNT = "tarkov"
    
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
        Get latest Escape from Tarkov news from Twitter via Nitter.
        
        Args:
            lang: Language (ru/en)
            limit: Maximum number of news items to return
            
        Returns:
            List of news items from Twitter
        """
        # Try to fetch from Twitter via Nitter
        twitter_news = await self._fetch_twitter_news(limit)
        if twitter_news:
            logger.info(f"Fetched {len(twitter_news)} news items from Twitter")
            return twitter_news
        
        # Fallback to official sources
        logger.warning("Twitter fetch failed, using fallback sources")
        return self._get_fallback_news(lang)
    
    async def _fetch_twitter_news(self, limit: int) -> List[Dict]:
        """Fetch latest tweets from @tarkov via Nitter RSS."""
        session = await self._get_session()
        
        # Try each Nitter instance until one works
        for instance in self.NITTER_INSTANCES:
            try:
                rss_url = f"{instance}/{self.TWITTER_ACCOUNT}/rss"
                logger.info(f"Trying Nitter instance: {instance}")
                
                async with session.get(
                    rss_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Nitter instance {instance} returned {response.status}")
                        continue
                    
                    content = await response.text()
                    
                    # Parse RSS feed
                    feed = feedparser.parse(content)
                    
                    if not feed.entries:
                        logger.warning(f"No entries in RSS from {instance}")
                        continue
                    
                    # Format news items from tweets
                    news_items = []
                    for entry in feed.entries[:limit]:
                        # Clean tweet text
                        title = entry.get("title", "No title")
                        description = self._clean_description(entry.get("description", entry.get("summary", "")))
                        
                        news_item = {
                            "title": title[:100] + "..." if len(title) > 100 else title,
                            "description": description,
                            "link": entry.get("link", "").replace(instance, "https://x.com"),  # Convert to x.com link
                            "date": self._parse_date(entry.get("published", ""))
                        }
                        news_items.append(news_item)
                    
                    logger.info(f"Successfully fetched {len(news_items)} tweets from {instance}")
                    return news_items
                    
            except Exception as e:
                logger.error(f"Error fetching from {instance}: {e}")
                continue
        
        # All instances failed
        logger.error("All Nitter instances failed")
        return []
    
    
    def _get_fallback_news(self, lang: str) -> List[Dict]:
        """Return hardcoded fallback news sources."""
        if lang == "ru":
            return [{
                "title": "Новости Escape from Tarkov",
                "description": "Последние новости и обновления об игре Escape from Tarkov",
                "link": "https://www.escapefromtarkov.com/news",
                "date": ""
            }, {
                "title": "Telegram канал (RU)",
                "description": "Официальный Telegram канал на русском языке",
                "link": "https://t.me/escapefromtarkovRU",
                "date": ""
            }, {
                "title": "Discord сервер",
                "description": "Официальный Discord сервер EFT",
                "link": "https://discord.gg/eft-official-rus",
                "date": ""
            }]
        else:
            return [{
                "title": "Escape from Tarkov News",
                "description": "Latest news and updates about Escape from Tarkov",
                "link": "https://www.escapefromtarkov.com/news",
                "date": ""
            }, {
                "title": "Telegram channel (EN)",
                "description": "Official Telegram channel in English",
                "link": "https://t.me/escapefromtarkovEN",
                "date": ""
            }, {
                "title": "Discord server",
                "description": "Official EFT Discord server",
                "link": "https://discord.gg/eft-official-rus",
                "date": ""
            }]
    
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
    
    def _format_reddit_date(self, timestamp: float) -> str:
        """Format Reddit timestamp to readable date."""
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return ""
    
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
