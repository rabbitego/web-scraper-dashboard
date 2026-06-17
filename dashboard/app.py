from flask import Flask, render_template_string
from scraper.analyzer import ArticleAnalyzer
from scraper.news_scraper import NewsScraper
import plotly.graph_objects as go
import plotly.utils
import json

app = Flask(__name__)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>News Scraper Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; }
        .header { background: #1e293b; padding: 24px; text-align: center; border-bottom: 2px solid #3b82f6; }
        .header h1 { font-size: 28px; color: #60a5fa; }
        .header p { color: #94a3b8; margin-top: 4px; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; padding: 24px; max-width: 1200px; margin: 0 auto; }
        .stat-card { background: #1e293b; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #334155; }
        .stat-card .number { font-size: 36px; font-weight: bold; color: #60a5fa; }
        .stat-card .label { color: #94a3b8; margin-top: 4px; }
        .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; padding: 0 24px 24px; max-width: 1200px; margin: 0 auto; }
        .chart-card { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
        .chart-card h3 { color: #60a5fa; margin-bottom: 12px; }
        .articles { max-width: 1200px; margin: 0 auto; padding: 0 24px 24px; }
        .articles h3 { color: #60a5fa; margin-bottom: 12px; font-size: 20px; }
        .article-item { background: #1e293b; padding: 14px 18px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #334155; }
        .article-item a { color: #e2e8f0; text-decoration: none; }
        .article-item a:hover { color: #60a5fa; }
        .article-item .source { color: #64748b; font-size: 13px; margin-top: 4px; }
        @media (max-width: 768px) { .stats-grid, .charts { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>News Scraper Dashboard</h1>
        <p>Live analysis of Hacker News headlines</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="number">{{ summary.total_articles }}</div>
            <div class="label">Total Articles</div>
        </div>
        <div class="stat-card">
            <div class="number">{{ summary.unique_sources }}</div>
            <div class="label">Unique Sources</div>
        </div>
        <div class="stat-card">
            <div class="number">{{ summary.top_source }}</div>
            <div class="label">Top Source</div>
        </div>
        <div class="stat-card">
            <div class="number">{{ summary.avg_title_length }}</div>
            <div class="label">Avg Title Length</div>
        </div>
    </div>

    <div class="charts">
        <div class="chart-card">
            <h3>Articles by Source</h3>
            <div id="source-chart"></div>
        </div>
        <div class="chart-card">
            <h3>Trending Words in Titles</h3>
            <div id="words-chart"></div>
        </div>
    </div>

    <div class="articles">
        <h3>Latest Headlines</h3>
        {% for article in articles[:20] %}
        <div class="article-item">
            <a href="{{ article.url }}" target="_blank">{{ article.title }}</a>
            <div class="source">{{ article.source }}</div>
        </div>
        {% endfor %}
    </div>

    <script>
        var sourceChart = {{ source_chart | safe }};
        Plotly.newPlot('source-chart', sourceChart.data, sourceChart.layout);

        var wordsChart = {{ words_chart | safe }};
        Plotly.newPlot('words-chart', wordsChart.data, wordsChart.layout);
    </script>
</body>
</html>
"""


def build_source_chart(source_dist: dict) -> str:
    sources = list(source_dist.keys())[:10]
    counts = list(source_dist.values())[:10]

    fig = go.Figure(data=[go.Bar(
        x=counts[::-1],
        y=sources[::-1],
        orientation="h",
        marker_color="#3b82f6",
    )])
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        margin=dict(l=10, r=10, t=10, b=10),
        height=350,
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def build_words_chart(words: dict) -> str:
    top_words = list(words.keys())[:12]
    counts = list(words.values())[:12]

    fig = go.Figure(data=[go.Bar(
        x=top_words,
        y=counts,
        marker_color="#8b5cf6",
    )])
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        margin=dict(l=10, r=10, t=10, b=10),
        height=350,
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


@app.route("/")
def index():
    scraper = NewsScraper()
    articles = scraper.scrape(max_articles=30)
    scraper.save_to_csv(articles)

    analyzer = ArticleAnalyzer()
    try:
        df = analyzer.load_all_csvs()
        summary = analyzer.get_summary(df)
    except FileNotFoundError:
        summary = {
            "total_articles": 0,
            "unique_sources": 0,
            "top_source": "N/A",
            "avg_title_length": 0,
            "source_distribution": {},
            "trending_words": {},
        }

    source_chart = build_source_chart(summary["source_distribution"])
    words_chart = build_words_chart(summary["trending_words"])

    article_dicts = [{"title": a.title, "source": a.source, "url": a.url} for a in articles]

    return render_template_string(
        DASHBOARD_HTML,
        summary=summary,
        articles=article_dicts,
        source_chart=source_chart,
        words_chart=words_chart,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
