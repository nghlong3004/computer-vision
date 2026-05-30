# -*- coding: utf-8 -*-
"""Generates a matplotlib session report chart."""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class ReportService:
    """Creates and saves a pie-chart session report as PNG."""

    def __init__(self, output_dir="screenshots"):
        self._dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, summary, neck_th, torso_th, alert_time, screenshot_count):
        """Create report chart. Returns file path."""
        d = summary["duration"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle("Session Report — Posture Monitor", fontsize=15, fontweight="bold")

        ax1.pie(
            [summary["good_pct"], summary["bad_pct"]],
            labels=["Good Posture", "Bad Posture"],
            colors=["#7FFF00", "#3232FF"],
            autopct="%1.1f%%",
            startangle=90,
            textprops={"fontsize": 12},
        )
        ax1.set_title("Posture Distribution")

        ax2.axis("off")
        info = (
            f"Duration:         {d:.0f}s ({d/60:.1f} min)\n"
            f"Good frames:      {summary['total_good']}\n"
            f"Bad frames:       {summary['total_bad']}\n"
            f"Screenshots:      {screenshot_count}\n"
            f"\n"
            f"Neck threshold:   {neck_th} deg\n"
            f"Torso threshold:  {torso_th} deg\n"
            f"Alert after:      {alert_time}s"
        )
        ax2.text(
            0.1, 0.5, info, fontsize=12,
            verticalalignment="center", fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="#f0f0f0", alpha=0.9),
        )
        ax2.set_title("Session Details")

        path = os.path.join(self._dir, "session_report.png")
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"\n  [📊] Đã lưu báo cáo: {path}")
        return path
