"""Browser automation and research."""
import requests
from bs4 import BeautifulSoup
class BrowserSkill:
    """Playwright Edge automation plus lightweight HTTP research helpers."""
    def search_url(self, query): """Return a Bing search URL for Edge."""; return 'https://www.bing.com/search?q='+requests.utils.quote(query)
    def summarize_page_text(self, url, limit=2000): """Fetch visible page text for LLM summarization."""; html=requests.get(url,timeout=15,headers={"User-Agent":"Mozilla/5.0"}).text; return BeautifulSoup(html,'html.parser').get_text(' ',strip=True)[:limit]
    def open_edge_and_search(self, query: str) -> None:
        """Open Microsoft Edge and search using Playwright."""
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=False)
            page = browser.new_page()
            page.goto(self.search_url(query))
            page.wait_for_timeout(3000)
            browser.contexts[0].pages[0]
    def research_and_save(self, query: str, output_path: str, brain) -> str:
        """Search, scrape top 3 results, summarize with LLM, save as .docx."""
        from docx import Document
        urls = self._get_search_urls(query, limit=3)
        combined = ""
        for url in urls:
            try:
                combined += self.summarize_page_text(url, limit=1500) + "\n\n"
            except Exception:
                pass
        summary = brain.ask(f"Write a structured research report on '{query}' using this source material:\n{combined[:4000]}")
        doc = Document(); doc.add_heading(query, 0)
        for para in summary.split("\n"):
            if para.strip(): doc.add_paragraph(para)
        doc.save(output_path); return output_path
    def _get_search_urls(self, query: str, limit: int = 3) -> list[str]:
        """Return top result URLs from Bing search."""
        html = requests.get(self.search_url(query), timeout=10, headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "html.parser")
        return [a["href"] for a in soup.select("li.b_algo h2 a") if a.get("href")][:limit]
