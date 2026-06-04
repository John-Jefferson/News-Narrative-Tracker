import re
import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import nltk
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from urllib.parse import quote_plus

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="News Narrative Tracker", layout="wide")

# ── Global CSS ───────────────────────────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* dark background */
    .stApp { background-color: #0f1117; }

    /* hide default streamlit header decoration */
    header { visibility: hidden; }

    /* metric cards */
    [data-testid="metric-container"] {
        background: #1c1f2e;
        border: 1px solid #2e3250;
        border-radius: 12px;
        padding: 16px 20px;
    }

    /* buttons */
    .stButton > button {
        background: #4f6ef7;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: background 0.2s;
    }
    .stButton > button:hover { background: #3b55d4; }

    /* stop button red */
    .stButton > button[kind="secondary"] {
        background: #e84343;
    }

    /* selectbox */
    .stSelectbox > div { border-radius: 8px; }

    /* dataframe */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* divider */
    hr { border-color: #2e3250; }
    </style>
""", unsafe_allow_html=True)

# ── Helper: styled header ─────────────────────────────────────
def section_header(title, subtitle=None):
    st.markdown(f"""
        <div style="margin: 32px 0 12px 0;">
            <p style="font-size:22px; font-weight:700; color:#ffffff; margin:0;">{title}</p>
            {"" if not subtitle else f'<p style="font-size:13px; color:#8a8fa8; margin:4px 0 0 0;">{subtitle}</p>'}
        </div>
    """, unsafe_allow_html=True)

def divider():
    st.markdown("<hr>", unsafe_allow_html=True)

# ── Plotly theme ──────────────────────────────────────────────
PLOT_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="#1c1f2e",
    plot_bgcolor="#1c1f2e",
    font=dict(family="Inter", color="#c9cdd8"),
)

# ── Processing ────────────────────────────────────────────────
def processingDF(dataset):
    df = pd.DataFrame(dataset)
    analyzer = SentimentIntensityAnalyzer()
    df["Sentiment Score"] = df["combined_words"].apply(
        lambda x: analyzer.polarity_scores(x)["compound"]
    )
    df["Sentiment Label"] = df["Sentiment Score"].apply(
        lambda x: "positive" if x >= 0.05 else "negative" if x <= -0.05 else "neutral"
    )
    df['pubDate'] = pd.to_datetime(df['pubDate'], format='%a, %d %b %Y %H:%M:%S %z').dt.date
    word_and_date = df[["pubDate", "combined_words"]].copy()
    word_and_date["combined_words"] = word_and_date["combined_words"].str.split()
    word_and_date = word_and_date.explode("combined_words")
    word_and_date = word_and_date[~word_and_date["combined_words"].isin(st.session_state.stop_words)]
    return df, word_and_date

def fetchArticles(clean_keyword, limit):
    count = 0
    numPage = 1
    dataset = []
    keyword = quote_plus(clean_keyword)
    keyword_words_split = clean_keyword.lower().split()

    progress_bar = st.progress(0)
    status_text = st.empty()
    st.button("⛔ Stop Fetching", on_click=lambda: st.session_state.update({"stop_fetching": True}))

    while count < limit:
        if st.session_state.get("stop_fetching", False):
            status_text.text(f"Stopped. Processing {count} articles gathered so far...")
            break

        url = f"https://www.rappler.com/?s={keyword}&feed=rss2&paged={numPage}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "xml")
        numPage += 1
        items = soup.find_all("item")

        if not items:
            status_text.text("No more articles found.")
            break

        for item in items:
            if count >= limit or st.session_state.get("stop_fetching", False):
                break
            title = item.find("title").text
            link = item.find("link").text
            pub_date = item.find("pubDate").text
            categories = [cat.text for cat in item.find_all("category")]
            categories = ", ".join(categories)
            description = item.find("description").text
            combined_words = title + " " + categories + " " + description
            combined_words = re.sub(r'[^a-zA-Z\s]', '', combined_words.lower())

            if not all(word in combined_words for word in keyword_words_split):
                continue

            dataset.append({
                "title": title, "pubDate": pub_date,
                "description": description, "categories": categories,
                "combined_words": combined_words, "link": link
            })
            count += 1
            progress_bar.progress(min(count / limit, 1.0))
            status_text.text(f"Fetched {count} of {limit} articles... (Page {numPage - 1})")

    if not dataset:
        status_text.text("No articles found.")
        return pd.DataFrame(), pd.DataFrame()

    status_text.text(f"✅ Done! {count} articles processed.")
    progress_bar.progress(1.0)
    return processingDF(dataset)

# ══════════════════════════════════════════════════════════════
# APP HEADER
# ══════════════════════════════════════════════════════════════
st.markdown("""
    <div style="padding: 40px 0 20px 0; text-align: center;">
        <p style="font-size:38px; font-weight:800; color:#ffffff; margin:0; letter-spacing:-1px;">
            📰 News Narrative Tracker
        </p>
        <p style="font-size:15px; color:#8a8fa8; margin:8px 0 0 0;">
            Analyze how Philippine news covers any topic — powered by statistics
        </p>
    </div>
""", unsafe_allow_html=True)

divider()

# ══════════════════════════════════════════════════════════════
# SEARCH SECTION
# ══════════════════════════════════════════════════════════════
section_header("🔍 Search", "Enter a keyword and set how many articles to analyze")

col_kw, col_lim, col_btn = st.columns([3, 1, 1])
with col_kw:
    inputKeyword = st.text_input("Keyword", placeholder="e.g. Duterte, Sara, Marcos...")
with col_lim:
    numLimit = st.number_input("Sample size", min_value=1, step=1, value=50)
with col_btn:
    st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
    if "fetching" not in st.session_state:
        st.session_state.fetching = False
    enter_clicked = st.button("🔎 Search", disabled=st.session_state.fetching, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Stop words manager ────────────────────────────────────────
if "show_stopwords" not in st.session_state:
    st.session_state.show_stopwords = False
if "stop_words" not in st.session_state:
    st.session_state.stop_words = set(stopwords.words("english"))
    for w in ["philippine", "news", "newsbreak", "national", "international"]:
        st.session_state.stop_words.add(w)

if st.button("⚙️ Manage Stop Words"):
    st.session_state.show_stopwords = not st.session_state.show_stopwords

if st.session_state.show_stopwords:
    with st.container():
        st.markdown("""
            <div style="background:#1c1f2e; border:1px solid #2e3250;
                        border-radius:12px; padding:20px; margin:12px 0;">
        """, unsafe_allow_html=True)
        section_header("Stop Words", "Words excluded from the word frequency analysis")
        c1, c2 = st.columns(2)
        with c1:
            new_word = st.text_input("Add a word")
            if st.button("➕ Add"):
                if new_word:
                    st.session_state.stop_words.add(new_word.lower())
                    st.success(f"'{new_word}' added")
        with c2:
            remove_word = st.text_input("Remove a word")
            if st.button("➖ Remove"):
                if remove_word:
                    st.session_state.stop_words.discard(remove_word.lower())
                    st.success(f"'{remove_word}' removed")
        st.dataframe(pd.DataFrame(sorted(st.session_state.stop_words), columns=["words"]), height=200)
        st.caption("*Includes common Rappler-specific words like 'philippine', 'news', etc.*")
        st.markdown("</div>", unsafe_allow_html=True)

# ── Trigger fetch ─────────────────────────────────────────────
if enter_clicked:
    if inputKeyword and numLimit:
        st.session_state.stop_fetching = False
        st.session_state.fetching = True
        st.session_state.stop_words.add(inputKeyword.lower())
        df, word_and_date = fetchArticles(inputKeyword, int(numLimit))
        st.session_state.fetching = False
        if not df.empty:
            st.session_state.mainDF = df
            st.session_state.mainWord_and_Date = word_and_date
            st.session_state.keyword_used = inputKeyword
        else:
            st.warning("No articles found for that keyword.")
    elif not inputKeyword:
        st.warning("Please enter a keyword.")

# ══════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════
if "mainDF" in st.session_state and not st.session_state.mainDF.empty:
    df = st.session_state.mainDF
    word_and_date = st.session_state.mainWord_and_Date
    keyword_used = st.session_state.get("keyword_used", "")

    divider()

    # ── Overview metrics ──────────────────────────────────────
    section_header(f"📊 Overview — \"{keyword_used}\"",
                   f"Results from Rappler · {df['pubDate'].min()} to {df['pubDate'].max()}")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Articles", len(df))
    with m2:
        st.metric("Date Range",
                  f"{(pd.to_datetime(df['pubDate'].max()) - pd.to_datetime(df['pubDate'].min())).days} days")
    with m3:
        st.metric("Avg Sentiment Score", f"{df['Sentiment Score'].mean():.3f}")
    with m4:
        dominant = df['Sentiment Label'].value_counts().idxmax()
        st.metric("Dominant Tone", dominant.capitalize())

    divider()

    # ── Word frequency + timeline ─────────────────────────────
    section_header("📝 Word Frequency Analysis",
                   "Most associated words found across all article titles, categories, and descriptions")

    st.session_state.word_count = word_and_date["combined_words"].value_counts()

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        fig_left = px.bar(
            st.session_state.word_count.reset_index().head(25),
            x="count", y="combined_words",
            orientation="h", title="Top 25 Words",
            color="count",
            color_continuous_scale="Blues",
            labels={"combined_words": "Word", "count": "Frequency"}
        )
        fig_left.update_layout(height=600, showlegend=False,
                               coloraxis_showscale=False, **PLOT_THEME)
        fig_left.update_traces(marker_line_width=0)
        st.plotly_chart(fig_left, use_container_width=True)

        st.session_state.selected_word = st.selectbox(
            "Select a word to see its trend", st.session_state.word_count.index)

    with col2:
        filtered = word_and_date[word_and_date["combined_words"] == st.session_state.selected_word]
        date_counts = filtered.groupby("pubDate").size().reset_index(name="count")
        fig_right = px.line(
            date_counts, x="pubDate", y="count",
            title=f'"{st.session_state.selected_word}" mentions over time',
            markers=True,
            labels={"pubDate": "Date", "count": "Mentions"}
        )
        fig_right.update_traces(line_color="#4f6ef7", marker_color="#4f6ef7")
        fig_right.update_layout(height=600, **PLOT_THEME)
        st.plotly_chart(fig_right, use_container_width=True)

    divider()

    # ── Sentiment section ─────────────────────────────────────
    section_header("🧠 VADER Sentiment Analysis",
                   "Sentiment scores based on emotional weight of words in each article")

    s1, s2, s3 = st.columns(3)
    neg = len(df[df["Sentiment Label"] == "negative"])
    neu = len(df[df["Sentiment Label"] == "neutral"])
    pos = len(df[df["Sentiment Label"] == "positive"])
    total = len(df)

    with s1:
        st.metric("🔴 Negative", neg, f"{neg/total*100:.1f}%")
    with s2:
        st.metric("⚪ Neutral", neu, f"{neu/total*100:.1f}%")
    with s3:
        st.metric("🟢 Positive", pos, f"{pos/total*100:.1f}%")

    sc1, sc2 = st.columns(2)

    with sc1:
        box_fig = px.box(
            df, y="Sentiment Score",
            title="Sentiment Score Distribution",
            color_discrete_sequence=["#4f6ef7"],
            points="all"
        )
        box_fig.update_layout(**PLOT_THEME)
        box_fig.add_hline(y=0, line_dash="dash", line_color="#888")
        st.plotly_chart(box_fig, use_container_width=True)

    with sc2:
        pie_fig = px.pie(
            df, names="Sentiment Label",
            title="Sentiment Distribution",
            color="Sentiment Label",
            color_discrete_map={
                "negative": "#e84343",
                "neutral": "#8a8fa8",
                "positive": "#43c97e"
            },
            hole=0.4
        )
        pie_fig.update_layout(**PLOT_THEME)
        st.plotly_chart(pie_fig, use_container_width=True)

    grouped = df.groupby("pubDate")["Sentiment Score"].mean().reset_index()
    trend_fig = px.line(
        grouped, x="pubDate", y="Sentiment Score",
        title="Average Sentiment Score Over Time",
        markers=True,
        labels={"pubDate": "Date", "Sentiment Score": "Avg Score"}
    )
    trend_fig.update_traces(line_color="#4f6ef7", marker_color="#4f6ef7")
    trend_fig.add_hline(y=0, line_dash="dash", line_color="#888",
                        annotation_text="Neutral", annotation_position="bottom right")
    trend_fig.update_layout(**PLOT_THEME)
    st.plotly_chart(trend_fig, use_container_width=True)

    divider()

    # ── Raw data ──────────────────────────────────────────────
    section_header("📄 Raw Articles", f"{len(df)} articles fetched")
    st.dataframe(
        df[["title", "pubDate", "Sentiment Score", "Sentiment Label", "link"]],
        use_container_width=True, height=400
    )
