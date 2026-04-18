"""
Visualisation Service — generates Seaborn charts from student feedback data.

Each function in this module:
  1. Accepts data as a pandas DataFrame or list of dicts
  2. Creates a Seaborn/Matplotlib figure
  3. Saves it to an in-memory buffer (no disk writes)
  4. Returns the buffer ready to be streamed as an HTTP response

Why in-memory buffers (BytesIO) instead of saving to disk?
  Saving to disk requires managing file cleanup, unique filenames,
  and disk space. BytesIO keeps everything in RAM — faster, simpler,
  and stateless. The chart exists only for the duration of the request.

Why a service layer and not directly in endpoints?
  Chart generation logic is complex and testable independently.
  Endpoints should only handle HTTP concerns — not chart styling.

Chart types provided:
  - Sentiment distribution bar chart
  - Sentiment pie chart
  - Attendance vs sentiment scatter plot
  - Backlogs distribution by sentiment
  - Study hours heatmap
  - Gender vs sentiment grouped bar chart
"""
import io
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Use non-interactive backend — CRITICAL for server environments
# Without this, Matplotlib tries to open a GUI window on the server
# which crashes because servers have no display
matplotlib.use("Agg")

# Global chart styling — consistent look across all charts
sns.set_theme(style="whitegrid", palette="muted")
FIGURE_DPI = 150
FIGURE_SIZE_STANDARD = (10, 6)
FIGURE_SIZE_SQUARE = (8, 8)

# Colour mapping for sentiment labels — consistent across all charts
SENTIMENT_COLOURS = {
    "Positive": "#2ecc71",   # Green
    "Neutral": "#3498db",    # Blue
    "Negative": "#e74c3c",   # Red
}


def _save_figure_to_buffer(fig: Figure) -> io.BytesIO:
    """
    Save a Matplotlib figure to an in-memory PNG buffer.

    Args:
        fig: Matplotlib Figure object to save

    Returns:
        BytesIO buffer containing the PNG image data,
        with the read position reset to the start (seek(0))
    """
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=FIGURE_DPI, bbox_inches="tight")
    buffer.seek(0)
    plt.close(fig)  # Free memory — always close figures after saving
    return buffer


def generate_sentiment_bar_chart(records: list[dict]) -> io.BytesIO:
    """
    Generate a bar chart showing sentiment distribution counts.

    Args:
        records: List of feedback record dictionaries

    Returns:
        BytesIO buffer containing the PNG bar chart

    Raises:
        ValueError: If records list is empty
    """
    if not records:
        raise ValueError("Cannot generate chart: no records provided.")

    df = pd.DataFrame(records)
    sentiment_counts = df["sentiment_label"].value_counts().reset_index()
    sentiment_counts.columns = ["Sentiment", "Count"]

    # Ensure consistent order
    order = ["Positive", "Neutral", "Negative"]
    sentiment_counts["Sentiment"] = pd.Categorical(
        sentiment_counts["Sentiment"], categories=order, ordered=True
    )
    sentiment_counts = sentiment_counts.sort_values("Sentiment")

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_STANDARD)

    colours = [
        SENTIMENT_COLOURS.get(s, "#95a5a6")
        for s in sentiment_counts["Sentiment"]
    ]

    bars = ax.bar(
        sentiment_counts["Sentiment"],
        sentiment_counts["Count"],
        color=colours,
        edgecolor="white",
        linewidth=1.5,
    )

    # Add count labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{int(height)}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    ax.set_title(
        "Student Sentiment Distribution",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Sentiment", fontsize=13)
    ax.set_ylabel("Number of Students", fontsize=13)
    ax.set_ylim(0, sentiment_counts["Count"].max() * 1.15)
    sns.despine()

    return _save_figure_to_buffer(fig)


def generate_sentiment_pie_chart(records: list[dict]) -> io.BytesIO:
    """
    Generate a pie chart showing sentiment distribution percentages.

    Args:
        records: List of feedback record dictionaries

    Returns:
        BytesIO buffer containing the PNG pie chart

    Raises:
        ValueError: If records list is empty
    """
    if not records:
        raise ValueError("Cannot generate chart: no records provided.")

    df = pd.DataFrame(records)
    sentiment_counts = df["sentiment_label"].value_counts()

    colours = [
        SENTIMENT_COLOURS.get(s, "#95a5a6")
        for s in sentiment_counts.index
    ]

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SQUARE)

    wedges, texts, autotexts = ax.pie(
        sentiment_counts.values,
        labels=sentiment_counts.index,
        autopct="%1.1f%%",
        colors=colours,
        startangle=140,
        pctdistance=0.85,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )

    for text in texts:
        text.set_fontsize(13)
    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_fontweight("bold")

    ax.set_title(
        "Sentiment Distribution (%)",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    return _save_figure_to_buffer(fig)


def generate_attendance_vs_sentiment(records: list[dict]) -> io.BytesIO:
    """
    Generate a box plot showing attendance distribution by sentiment.

    Box plots reveal whether students with lower attendance
    tend to have more negative sentiment — key insight for universities.

    Args:
        records: List of feedback record dictionaries

    Returns:
        BytesIO buffer containing the PNG box plot

    Raises:
        ValueError: If records list is empty
    """
    if not records:
        raise ValueError("Cannot generate chart: no records provided.")

    df = pd.DataFrame(records)
    order = ["Positive", "Neutral", "Negative"]
    palette = {k: v for k, v in SENTIMENT_COLOURS.items()}

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_STANDARD)

    sns.boxplot(
        data=df,
        x="sentiment_label",
        y="attendance_percentage",
        hue="sentiment_label",
        order=order,
        palette=palette,
        width=0.5,
        linewidth=1.5,
        legend=False,
        ax=ax,
    )

    sns.stripplot(
        data=df,
        x="sentiment_label",
        y="attendance_percentage",
        order=order,
        color="black",
        alpha=0.3,
        size=3,
        ax=ax,
    )

    ax.set_title(
        "Attendance Distribution by Sentiment",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Sentiment Label", fontsize=13)
    ax.set_ylabel("Attendance Percentage (%)", fontsize=13)
    ax.set_ylim(0, 110)
    sns.despine()

    return _save_figure_to_buffer(fig)


def generate_backlogs_by_sentiment(records: list[dict]) -> io.BytesIO:
    """
    Generate a count plot showing backlog distribution by sentiment.

    Reveals the relationship between academic backlogs and student
    emotional state — universities can use this to target support.

    Args:
        records: List of feedback record dictionaries

    Returns:
        BytesIO buffer containing the PNG count plot

    Raises:
        ValueError: If records list is empty
    """
    if not records:
        raise ValueError("Cannot generate chart: no records provided.")

    df = pd.DataFrame(records)
    order = ["Positive", "Neutral", "Negative"]

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_STANDARD)

    sns.countplot(
        data=df,
        x="active_backlogs",
        hue="sentiment_label",
        hue_order=order,
        palette=SENTIMENT_COLOURS,
        ax=ax,
    )

    ax.set_title(
        "Active Backlogs Distribution by Sentiment",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Number of Active Backlogs", fontsize=13)
    ax.set_ylabel("Number of Students", fontsize=13)
    ax.legend(title="Sentiment", fontsize=11)
    sns.despine()

    return _save_figure_to_buffer(fig)


def generate_gender_sentiment_chart(records: list[dict]) -> io.BytesIO:
    """
    Generate a grouped bar chart of sentiment broken down by gender.

    Args:
        records: List of feedback record dictionaries

    Returns:
        BytesIO buffer containing the PNG grouped bar chart

    Raises:
        ValueError: If records list is empty
    """
    if not records:
        raise ValueError("Cannot generate chart: no records provided.")

    df = pd.DataFrame(records)
    order = ["Positive", "Neutral", "Negative"]

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_STANDARD)

    sns.countplot(
        data=df,
        x="gender",
        hue="sentiment_label",
        hue_order=order,
        palette=SENTIMENT_COLOURS,
        ax=ax,
    )

    ax.set_title(
        "Sentiment Distribution by Gender",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Gender", fontsize=13)
    ax.set_ylabel("Number of Students", fontsize=13)
    ax.legend(title="Sentiment", fontsize=11)
    sns.despine()

    return _save_figure_to_buffer(fig)


def generate_study_hours_distribution(records: list[dict]) -> io.BytesIO:
    """
    Generate a histogram showing study hours distribution by sentiment.

    Args:
        records: List of feedback record dictionaries

    Returns:
        BytesIO buffer containing the PNG histogram

    Raises:
        ValueError: If records list is empty
    """
    if not records:
        raise ValueError("Cannot generate chart: no records provided.")

    df = pd.DataFrame(records)
    order = ["Positive", "Neutral", "Negative"]

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_STANDARD)

    for sentiment in order:
        subset = df[df["sentiment_label"] == sentiment]
        if not subset.empty:
            ax.hist(
                subset["study_hours_per_day"],
                alpha=0.6,
                label=sentiment,
                color=SENTIMENT_COLOURS[sentiment],
                bins=range(1, 15),
                edgecolor="white",
            )

    ax.set_title(
        "Study Hours Distribution by Sentiment",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Study Hours Per Day", fontsize=13)
    ax.set_ylabel("Number of Students", fontsize=13)
    ax.legend(title="Sentiment", fontsize=11)
    sns.despine()

    return _save_figure_to_buffer(fig)