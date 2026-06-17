import pytest
from unittest.mock import patch, MagicMock
from scraper.news_scraper import NewsScraper, Article
from scraper.analyzer import ArticleAnalyzer
import pandas as pd
import tempfile
import os

SAMPLE_HTML = """
<html><body>
<table>
<tr><td class="title">
    <span class="titleline"><a href="https://example.com/article1">Python 3.13 Released</a>
    <span class="sitestr">example.com</span></span>
</td></tr>
<tr><td class="title">
    <span class="titleline"><a href="https://blog.rust-lang.org/post">Rust Gets Faster</a>
    <span class="sitestr">rust-lang.org</span></span>
</td></tr>
<tr><td class="title">
    <span class="titleline"><a href="item?id=12345">Ask HN: Best Python Libraries</a></span>
</td></tr>
</table>
</body></html>
"""


def test_extract_domain():
    scraper = NewsScraper()
    assert scraper._extract_domain("https://www.example.com/page") == "example.com"
    assert scraper._extract_domain("https://blog.rust-lang.org/post") == "blog.rust-lang.org"


def test_scrape_returns_articles():
    scraper = NewsScraper()
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status = MagicMock()

    with patch("requests.get", return_value=mock_response):
        articles = scraper.scrape(max_articles=10)

    assert isinstance(articles, list)
    for article in articles:
        assert isinstance(article, Article)
        assert article.title
        assert article.scraped_at


def test_save_to_csv():
    with tempfile.TemporaryDirectory() as tmpdir:
        scraper = NewsScraper(data_dir=tmpdir)
        articles = [
            Article("Test Article", "example.com", "https://example.com", "2024-01-01T00:00:00"),
            Article("Another One", "test.org", "https://test.org", "2024-01-01T00:00:00"),
        ]
        path = scraper.save_to_csv(articles, "test.csv")
        assert os.path.exists(path)

        df = pd.read_csv(path)
        assert len(df) == 2
        assert "title" in df.columns


def test_save_to_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        scraper = NewsScraper(data_dir=tmpdir)
        articles = [
            Article("Test", "example.com", "https://example.com", "2024-01-01T00:00:00"),
        ]
        path = scraper.save_to_json(articles, "test.json")
        assert os.path.exists(path)


def test_analyzer_source_distribution():
    df = pd.DataFrame({
        "title": ["A", "B", "C", "D"],
        "source": ["github.com", "github.com", "bbc.com", "github.com"],
        "url": ["u1", "u2", "u3", "u4"],
        "scraped_at": ["t1", "t2", "t3", "t4"],
    })
    analyzer = ArticleAnalyzer()
    dist = analyzer.get_source_distribution(df)
    assert dist["github.com"] == 3
    assert dist["bbc.com"] == 1


def test_analyzer_word_frequency():
    df = pd.DataFrame({
        "title": [
            "Python Machine Learning Guide",
            "Python Deep Learning Tutorial",
            "JavaScript React Framework",
        ],
        "source": ["a", "b", "c"],
        "url": ["u1", "u2", "u3"],
        "scraped_at": ["t1", "t2", "t3"],
    })
    analyzer = ArticleAnalyzer()
    words = analyzer.get_title_word_frequency(df, top_n=5)
    assert "python" in words
    assert "learning" in words


def test_analyzer_summary():
    df = pd.DataFrame({
        "title": ["Article One", "Article Two"],
        "source": ["src1", "src2"],
        "url": ["u1", "u2"],
        "scraped_at": ["t1", "t2"],
    })
    analyzer = ArticleAnalyzer()
    summary = analyzer.get_summary(df)
    assert summary["total_articles"] == 2
    assert summary["unique_sources"] == 2
