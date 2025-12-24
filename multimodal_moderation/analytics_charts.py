import matplotlib.pyplot as plt
import pandas as pd
import requests

from multimodal_moderation.env import API_BASE_URL, USER_API_KEY


def _fetch_analytics_summary() -> dict:
    url = f"{API_BASE_URL}/api/v1/analytics/summary"
    r = requests.get(url, headers={"Authorization": f"Bearer {USER_API_KEY}"})
    r.raise_for_status()
    return r.json()


def _fetch_analytics_recent(limit: int = 50) -> list[dict]:
    url = f"{API_BASE_URL}/api/v1/analytics/recent"
    r = requests.get(url, params={"limit": limit}, headers={"Authorization": f"Bearer {USER_API_KEY}"})
    r.raise_for_status()
    return r.json().get("events", [])


def _bar_plot_from_dict(title: str, data: dict) -> "plt.Figure":
    fig = plt.figure()
    ax = fig.add_subplot(111)

    if not data:
        ax.set_title(title)
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center")
        ax.set_axis_off()
        return fig

    labels = list(data.keys())
    values = list(data.values())

    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return fig


def _pie_plot_safe_unsafe(title: str, by_decision: dict) -> "plt.Figure":
    fig = plt.figure()
    ax = fig.add_subplot(111)

    safe = int(by_decision.get("safe", 0) or 0)
    unsafe = int(by_decision.get("unsafe", 0) or 0)

    total = safe + unsafe
    if total == 0:
        ax.set_title(title)
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center")
        ax.set_axis_off()
        return fig

    ax.pie([safe, unsafe], labels=["safe", "unsafe"], autopct="%1.1f%%")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def load_analytics(limit: int = 50):
    """
    Return:
      total_events, safe_rate, safe_count, unsafe_count,
      flags_fig, types_fig, decision_fig, recent_df
    """
    try:
        summary = _fetch_analytics_summary()
        events = _fetch_analytics_recent(limit=limit)

        total_events = int(summary.get("total_events", 0) or 0)
        safe_rate = float(summary.get("safe_rate", 0.0) or 0.0)

        by_decision = summary.get("by_decision", {}) or {}
        safe_count = int(by_decision.get("safe", 0) or 0)
        unsafe_count = int(by_decision.get("unsafe", 0) or 0)

        flag_counts_true = summary.get("flag_counts_true", {}) or {}
        by_type = summary.get("by_type", {}) or {}

        flags_fig = _bar_plot_from_dict("Flags (True) - count", flag_counts_true)
        types_fig = _bar_plot_from_dict("Events by type", by_type)
        decision_fig = _pie_plot_safe_unsafe("Safe vs Unsafe", by_decision)

        # Recent events table
        if events:
            df = pd.DataFrame(events)
            # sort by timestamp (ISO string) desc
            if "ts" in df.columns:
                df = df.sort_values("ts", ascending=False)
            # flatten flags into useful columns (optional)
            if "flags" in df.columns:
                flags_df = pd.json_normalize(df["flags"])
                flags_df.columns = [f"flag.{c}" for c in flags_df.columns]
                df = pd.concat([df.drop(columns=["flags"]), flags_df], axis=1)

            # nicer columns first, if they exist
            preferred = [
                c
                for c in ["ts", "content_type", "decision", "model_name", "mime_type", "input_size_bytes"]
                if c in df.columns
            ]
            rest = [c for c in df.columns if c not in preferred]
            df = df[preferred + rest]
        else:
            df = pd.DataFrame(columns=["ts", "content_type", "decision", "model_name", "mime_type", "input_size_bytes"])

        return total_events, safe_rate, safe_count, unsafe_count, flags_fig, types_fig, decision_fig, df

    except Exception as e:
        # nice-looking fallback on the dashboard
        err_fig = plt.figure()
        ax = err_fig.add_subplot(111)
        ax.set_title("Error loading analytics")
        ax.text(0.5, 0.5, str(e), ha="center", va="center")
        ax.set_axis_off()
        err_fig.tight_layout()

        empty_df = pd.DataFrame(columns=["error"])
        empty_df.loc[0] = [str(e)]

        return 0, 0.0, 0, 0, err_fig, err_fig, err_fig, empty_df
