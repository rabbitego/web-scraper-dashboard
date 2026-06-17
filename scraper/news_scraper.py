import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import csv
from pathlib import Path


@dataclass
class Article:
    title: str
    source: str
    url: str
    scraped_at: str


class NewsScraper:
    """Scrapes top headlines from Hacker News."""

    BASE_URL = "https://news.ycombinator.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (educational project - web scraper dashboard)"
    }

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def scrape(self, max_articles: int = 30) -> list[Article]:
        response = requests.get(self.BASE_URL, headers=self.HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        articles = []

        rows = soup.select(".titleline > a")
        for link in rows[:max_articles]:
            title = link.get_text(strip=True)
            url = link.get("href", "")

            if url.startswith("item?"):
                url = f"{self.BASE_URL}/{url}"

            source = self._extract_domain(url)

            articles.append(Article(
                title=title,
                source=source,
                url=url,
                scraped_at=datetime.now(timezone.utc).isoformat(),
            ))

        return articles

    def _extract_domain(self, url: str) -> str:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            return domain if domain else "news.ycombinator.com"
        except Exception:
            return "unknown"

    def save_to_csv(self, articles: list[Article], filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"articles_{timestamp}.csv"

        filepath = self.data_dir / filename
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "source", "url", "scraped_at"])
            writer.writeheader()
            for article in articles:
                writer.writerow(asdict(article))

        return str(filepath)

    def save_to_json(self, articles: list[Article], filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"articles_{timestamp}.json"

        filepath = self.data_dir / filename
        data = [asdict(a) for a in articles]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return str(filepath)


def main():
    scraper = NewsScraper()
    print("Scraping Hacker News...")

    articles = scraper.scrape(max_articles=30)
    print(f"Found {len(articles)} articles")

    csv_path = scraper.save_to_csv(articles)
    json_path = scraper.save_to_json(articles)

    print(f"Saved to: {csv_path}")
    print(f"Saved to: {json_path}")

    print("\nTop 5 headlines:")
    for i, article in enumerate(articles[:5], 1):
        print(f"  {i}. {article.title} ({article.source})")


if __name__ == "__main__":
    main()
