import json
from datetime import datetime
import os

class NewsCache:
    def __init__(self):
        self.cache_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'news_cache.json')
        self.cache_duration = 3600  # 1 hour in seconds

    def get_cached_news(self):
        """Get cached news if it exists and is not expired"""
        try:
            if not os.path.exists(self.cache_file):
                return None

            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)

            # Check if cache is expired
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if (datetime.now() - cached_time).total_seconds() > self.cache_duration:
                return None

            return cache_data['articles']

        except Exception:
            return None

    def cache_news(self, articles):
        """Cache the news articles"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'articles': articles
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)

        except Exception as e:
            print(f"Error caching news: {e}") 