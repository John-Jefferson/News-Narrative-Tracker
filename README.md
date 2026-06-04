# 📰 News Narrative Tracker

A data-driven web application that scrapes and analyzes Philippine news articles to reveal how a topic or public figure is covered over time. It combines web scraping, natural language processing, and statistical analysis to surface word associations, sentiment trends, and coverage patterns — all without relying on AI-generated conclusions.

---

## 🖥️ Demo

> Enter any keyword — a politician's name, a topic, an event — and the app automatically gathers news articles and breaks down how the media covers it.

![screenshot placeholder]

---

## ✨ Features

- 🔍 **Keyword-based article scraping** from Rappler's RSS feed
- 📝 **Word frequency analysis** — see which words dominate coverage
- 📈 **Word trend over time** — track when a word spikes in the news
- 🧠 **VADER Sentiment Analysis** — scores each article as positive, negative, or neutral
- 📊 **Sentiment trend over time** — see how coverage tone shifts month by month
- ⚙️ **Customizable stop words** — add or remove words to clean up your analysis
- ⛔ **Stop fetching anytime** — cancel mid-scrape and still process what was gathered
- 🌑 **Dark mode dashboard** — clean, modern UI built with Plotly and Streamlit

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Web app framework |
| BeautifulSoup | HTML/XML parsing |
| Requests | HTTP requests |
| Pandas | Data manipulation |
| Plotly Express | Interactive charts |
| VADER Sentiment | Sentiment scoring |
| NLTK | Stop words |
| urllib.parse | URL encoding |

---

## 📦 Installation

**1. Clone the repository**
```bash
git clone https://github.com/John-Jefferson/news-narrative-tracker.git
cd news-narrative-tracker
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Download NLTK stop words**
```python
import nltk
nltk.download('stopwords')
```

**4. Run the app**
```bash
streamlit run webClient.py
```

---

## 📋 Requirements

```
streamlit
requests
beautifulsoup4
lxml
pandas
plotly
vaderSentiment
nltk
```

Or install all at once:
```bash
pip install streamlit requests beautifulsoup4 lxml pandas plotly vaderSentiment nltk
```

---

## 🚀 How to Use

1. Enter a **keyword** in the search bar (e.g. `Duterte`, `Sara`, `Marcos`)
2. Set the **sample size** — how many articles to fetch
3. Click **🔎 Search** to start scraping
4. Optionally click **⚙️ Manage Stop Words** to customize which words are excluded
5. View results:
   - **Word Frequency** — top 25 most associated words
   - **Word Trend** — select any word to see when it appeared most
   - **Sentiment Overview** — negative, neutral, positive article counts
   - **Sentiment Distribution** — box plot and pie chart
   - **Sentiment Over Time** — average sentiment trend line
   - **Raw Articles** — full table of all fetched articles

---

## 📊 How It Works

### Scraping
Articles are fetched from Rappler's RSS feed using keyword-based search pagination. Each article is filtered — only articles where the keyword appears in the title, categories, or description are kept.

### Text Processing
Combined text (title + categories + description) is cleaned by:
- Lowercasing all text
- Removing punctuation and numbers
- Removing stop words (NLTK English stop words + custom additions)

### Sentiment Scoring
Each article is scored using **VADER (Valence Aware Dictionary and sEntiment Reasoner)** — a rule-based sentiment tool that assigns a compound score between -1 (most negative) and +1 (most positive).

> **Note:** Because news articles are objective by nature, sentiment scores reflect the emotional weight of the events being reported rather than editorial bias.

### Word Frequency
Words are extracted from the cleaned combined text, exploded into individual rows per word per date, and counted using `value_counts()`.

---

## ⚠️ Limitations

- **Source:** Currently scrapes Rappler only. Other sources (Inquirer, PhilStar) can be added.
- **RSS depth:** Rappler's RSS feed returns a limited number of articles per page. Very old articles may not be accessible.
- **Sentiment accuracy:** VADER was trained on social media text. News sentiment scores should be interpreted as event tone, not editorial opinion.
- **Sample size:** Results depend on how many articles the RSS feed returns for your keyword. Small samples may produce less reliable statistics.
- **Language:** English articles only. Tagalog or mixed-language articles may score inaccurately.

---

## 🗂️ Project Structure

```
news-narrative-tracker/
│
├── webClient.py        # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 🔮 Planned Features

- [ ] Multi-source scraping (Inquirer, PhilStar, Manila Bulletin)
- [ ] Chi-Square test for word significance
- [ ] LDA topic clustering
- [ ] Export results to Excel/CSV
- [ ] Keyword comparison mode (e.g. Leni vs Sara)
- [ ] Date range filtering

---

## 👤 Author

**John Jefferson Leonardo**
Data Analyst · BS Information Technology Student · New Era University

- 📧 johnjefferson.leonardo@gmail.com
- 🐙 [GitHub](https://github.com/John-Jefferson)

---

## 📄 License

This project is for portfolio and educational purposes.
