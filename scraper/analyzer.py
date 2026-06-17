import pandas as pd
from pathlib import Path
from collections import Counter
import json


class ArticleAnalyzer:
    """Analyzes scraped article data and produces statistics."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

    def load_latest_csv(self) -> pd.DataFrame:
        csv_files = sorted(self.data_dir.glob("articles_*.csv"), reverse=True)
        if not csv_files:
            raise FileNotFoundError("No article CSV files found in data directory")
        return pd.read_csv(csv_files[0])

    def load_all_csvs(self) -> pd.DataFrame:
        csv_files = list(self.data_dir.glob("articles_*.csv"))
        if not csv_files:
            raise FileNotFoundError("No article CSV files found in data directory")

        frames = [pd.read_csv(f) for f in csv_files]
        return pd.concat(frames, ignore_index=True).drop_duplicates(subset=["url"])

    def get_source_distribution(self, df: pd.DataFrame) -> dict[str, int]:
        return dict(df["source"].value_counts().head(15))

    def get_title_word_frequency(self, df: pd.DataFrame, top_n: int = 20) -> dict[str, int]:
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "is", "it", "as", "from", "that",
            "this", "are", "was", "be", "have", "has", "not", "you", "your",
            "how", "what", "why", "when", "can", "will", "do", "its", "my",
            "i", "we", "they", "he", "she", "us", "new", "about",
        }

        words = []
        for title in df["title"].dropna():
            for word in title.lower().split():
                cleaned = word.strip(".,!?()[]{}\"':-/")
                if cleaned and len(cleaned) > 2 and cleaned not in stop_words:
                    words.append(cleaned)

        return dict(Counter(words).most_common(top_n))

    def get_summary(self, df: pd.DataFrame) -> dict:
        return {
            "total_articles": len(df),
            "unique_sources": df["source"].nunique(),
            "top_source": df["source"].value_counts().index[0] if len(df) > 0 else "N/A",
            "avg_title_length": round(df["title"].str.len().mean(), 1),
            "source_distribution": self.get_source_distribution(df),
            "trending_words": self.get_title_word_frequency(df),
        }

    def export_summary(self, filename: str = "analysis_summary.json") -> str:
        df = self.load_all_csvs()
        summary = self.get_summary(df)

        filepath = self.data_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return str(filepath)


def main():
    analyzer = ArticleAnalyzer()

    try:
        df = analyzer.load_all_csvs()
    except FileNotFoundError:
        print("No data found. Run the scraper first: python -m scraper.news_scraper")
        return

    summary = analyzer.get_summary(df)
    print(f"\n--- Article Analysis ---")
    print(f"Total articles: {summary['total_articles']}")
    print(f"Unique sources: {summary['unique_sources']}")
    print(f"Top source: {summary['top_source']}")
    print(f"Avg title length: {summary['avg_title_length']} chars")

    print(f"\nTop 10 sources:")
    for source, count in list(summary["source_distribution"].items())[:10]:
        print(f"  {source}: {count}")

    print(f"\nTrending words:")
    for word, count in list(summary["trending_words"].items())[:10]:
        print(f"  {word}: {count}")

    path = analyzer.export_summary()
    print(f"\nFull summary saved to: {path}")


if __name__ == "__main__":
    main()
