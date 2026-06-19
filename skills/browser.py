"""Browser automation and research."""
import requests
from bs4 import BeautifulSoup
class BrowserSkill:
    """Playwright-ready browser and lightweight HTTP research helpers."""
    def search_url(self, query): """Return a Bing search URL for Edge."""; return 'https://www.bing.com/search?q='+requests.utils.quote(query)
    def summarize_page_text(self, url, limit=2000): """Fetch visible page text for LLM summarization."""; html=requests.get(url,timeout=15).text; return BeautifulSoup(html,'html.parser').get_text(' ',strip=True)[:limit]
