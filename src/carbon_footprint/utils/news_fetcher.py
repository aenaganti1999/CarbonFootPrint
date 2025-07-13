import requests
from typing import List, Dict
import openai
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from .news_cache import NewsCache

load_dotenv()

class NewsFetcher:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.base_url = "https://www.iqair.com/newsroom"
        self.cache = NewsCache()

    def fetch_sustainability_news(self, days: int = 1) -> List[Dict]:
        """
        Fetch sustainability news articles with caching
        """
        # Check cache first
        cached_news = self.cache.get_cached_news()
        if cached_news:
            return cached_news

        # If no cache or expired, fetch new articles
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Make API request
            params = {
                'q': 'sustainability OR climate change OR renewable energy',
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'language': 'en',
                'sortBy': 'relevancy',
                'apiKey': self.news_api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            articles = response.json().get('articles', [])[:5]  # Get top 5 articles
            processed_articles = self.process_articles(articles)
            
            # Cache the results
            self.cache.cache_news(processed_articles)
            
            return processed_articles
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def summarize_article(self, article: Dict) -> str:
        """
        Use OpenAI to generate a concise summary of the article
        """
        try:
            prompt = f"""
            Summarize this news article in 2-3 sentences, focusing on key sustainability initiatives:
            Title: {article['title']}
            Content: {article['description']}
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a sustainability news expert. Summarize key initiatives and impacts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error summarizing article: {e}")
            return "Unable to generate summary."

    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Process and summarize each article
        """
        processed_articles = []
        
        for article in articles:
            summary = self.summarize_article(article)
            processed_articles.append({
                'title': article['title'],
                'summary': summary,
                'url': article['url'],
                'published_at': article['publishedAt'],
                'source': article['source']['name']
            })
        
        return processed_articles 