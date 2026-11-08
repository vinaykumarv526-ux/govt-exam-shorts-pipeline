"""
Autonomous Government Exam Shorts Pipeline Runner:
Orchestrates data ingestion, 1080x1920 visual layout rendering with rotating palettes,
royalty-free audio looping (-18dB), and multi-platform scheduling (YouTube Shorts & Facebook Reels).
"""

import os
import sys
import json
import time
import datetime
import argparse
from typing import List, Dict, Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from scraper import fetch_notifications
from renderer import render_exam_video, render_preview_poster, PALETTES
from audio_mixer import ensure_background_track
from scheduler import publish_exam_short

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
STATE_FILE = os.path.join(BASE_DIR, "data", "pipeline_state.json")


def load_pipeline_state() -> Dict[str, Any]:
    """Loads state to maintain continuous palette rotation across pipeline runs."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_palette_index": -1, "total_videos_rendered": 0}


def save_pipeline_state(state: Dict[str, Any]):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def calculate_scheduled_slots(days: int = 2, slots_per_day: int = 3) -> List[datetime.datetime]:
    """
    Computes peak publication timestamps across N days.
    Strategic daily slots (IST):
      - Slot 1 (Morning Alert): 09:30 AM IST
      - Slot 2 (Afternoon Break): 02:30 PM IST
      - Slot 3 (Evening Prime): 07:30 PM IST
    """
    # Base starting date is tomorrow (or next available slot today)
    ist_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now_ist = datetime.datetime.now(ist_tz)
    tomorrow = (now_ist + datetime.timedelta(days=1)).date()

    daily_slot_hours = [
        (9, 30),   # 09:30 AM IST
        (14, 30),  # 02:30 PM IST
        (19, 30),  # 07:30 PM IST
    ]

    # If more slots requested per day, distribute evenly
    if slots_per_day != 3:
        step = 12.0 / max(1, slots_per_day)
        daily_slot_hours = [(int(9 + s * step), int(((9 + s * step) % 1) * 60)) for s in range(slots_per_day)]

    slots = []
    for day_offset in range(days):
        target_date = tomorrow + datetime.timedelta(days=day_offset)
        for h, m in daily_slot_hours[:slots_per_day]:
            slot_dt = datetime.datetime(
                year=target_date.year,
                month=target_date.month,
                day=target_date.day,
                hour=h,
                minute=m,
                tzinfo=ist_tz
            )
            # Convert to UTC
            slots.append(slot_dt.astimezone(datetime.timezone.utc))
    return slots


def run_pipeline(
    source: str = "mock",
    limit: int = 3,
    days: int = 1,
    slots_per_day: int = 3,
    duration: float = 15.0,
    fps: int = 30,
    posters_only: bool = False,
    schedule: bool = False,
    dry_run: bool = True,
    interval_hours: float = 4.0,
    platforms: List[str] = None,
):
    """
    Executes end-to-end automated pipeline:
    1. Scrapes or ingests exam alerts.
    2. Cycles through color palettes.
    3. Renders pixel-perfect 1080x1920 9:16 Shorts with -18dB audio.
    4. Schedules to Facebook Reels (and optionally other platforms) across N days.
    """
    if platforms is None:
        platforms = ["facebook"]  # Facebook Reels only by default ("no youtube")
    # If multi-day scheduling requested, adjust total limit
    if days > 1:
        total_required = days * slots_per_day
        if limit < total_required:
            limit = total_required

    print("=" * 75)
    print("  GOVT EXAM SHORTS AUTOMATION PIPELINE")
    print(f"  Mode: source={source} | days={days} | slots/day={slots_per_day} | total_videos={limit}")
    print(f"  Video: duration={duration}s | fps={fps} | dry_run={dry_run}")
    print("=" * 75)

    # Step 1: Ensure assets & audio
    print("\n[Step 1/4] Checking and preparing audio assets...")
    bg_audio = ensure_background_track()
    print(f"  • Active background music track: {os.path.basename(bg_audio)}")

    # Step 2: Fetch notifications
    print("\n[Step 2/4] Ingesting Government Exam alerts...")
    exams = fetch_notifications(source=source, limit=limit)
    if not exams:
        print("[Error] No notifications available to process.")
        return

    print(f"  • Successfully received {len(exams)} exam alert(s) for rendering.")

    state = load_pipeline_state()
    start_palette = (state.get("last_palette_index", -1) + 1) % len(PALETTES)

    manifest = []
    scheduled_slot_times = calculate_scheduled_slots(days=max(1, days), slots_per_day=slots_per_day)

    # Step 3: Render videos and posters
    print(f"\n[Step 3/4] Rendering 9:16 vertical short-form content (Palette cycle starting at #{start_palette + 1})...")
    for i, exam in enumerate(exams):
        palette_idx = (start_palette + i) % len(PALETTES)
        palette = PALETTES[palette_idx]

        staggered_time = (
            scheduled_slot_times[i]
            if i < len(scheduled_slot_times)
            else (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2 + i * interval_hours))
        )
        ist_time_str = staggered_time.astimezone(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%d %b %Y, %I:%M %p IST")

        print("-" * 65)
        print(f"  Job {i + 1}/{len(exams)}: {exam['title']}")
        print(f"  • Color Palette: #{palette_idx + 1} '{palette['name']}'")
        print(f"  • Vacancies: {exam.get('vacancy_callout')}")
        print(f"  • Scheduled Slot: {ist_time_str} (UTC: {staggered_time.strftime('%Y-%m-%dT%H:%M:%SZ')})")

        # Render poster preview
        poster_path = render_preview_poster(exam, palette_idx=palette_idx)

        video_path = None
        if not posters_only:
            video_path = render_exam_video(
                exam_data=exam,
                palette_idx=palette_idx,
                duration_sec=duration,
                fps=fps,
            )

        # Step 4: Schedule publishing
        publish_results = None
        if schedule and video_path:
            publish_results = publish_exam_short(
                video_path=video_path,
                exam_data=exam,
                scheduled_dt=staggered_time,
                platforms=tuple(platforms),
                dry_run=dry_run,
            )

        manifest.append({
            "exam_id": exam.get("id"),
            "title": exam.get("title"),
            "palette": palette["name"],
            "poster": poster_path,
            "video": video_path,
            "scheduled_time_utc": staggered_time.isoformat(),
            "scheduled_time_ist": ist_time_str,
            "publish_results": publish_results,
        })

    # Save state
    state["last_palette_index"] = (start_palette + len(exams) - 1) % len(PALETTES)
    state["total_videos_rendered"] = state.get("total_videos_rendered", 0) + len(exams)
    save_pipeline_state(state)

    # Save execution report
    summary_path = os.path.join(OUTPUT_DIR, f"pipeline_summary_{int(time.time())}.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 75)
    print("  PIPELINE EXECUTION COMPLETE")
    print(f"  Total Processed: {len(manifest)} video(s)")
    print(f"  Execution Summary: {summary_path}")
    print("=" * 75 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Govt Exam 9:16 Shorts Video Generator & Scheduler",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--source", choices=["auto", "mock", "live"], default="mock", help="Notification data source")
    parser.add_argument("--limit", type=int, default=3, help="Number of exams to process (overridden if --days > 1)")
    parser.add_argument("--days", type=int, default=1, help="Number of days ahead to generate & schedule (e.g. 2)")
    parser.add_argument("--slots-per-day", type=int, default=3, help="Publishing slots per day (e.g. 3 = 09:30 AM, 02:30 PM, 07:30 PM IST)")
    parser.add_argument("--duration", type=float, default=15.0, help="Video duration in seconds (15-30s)")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("--posters-only", action="store_true", help="Only render posters for instant review")
    parser.add_argument("--schedule", action="store_true", default=True, help="Schedule to YouTube Shorts & FB Reels")
    parser.add_argument("--live-publish", action="store_true", help="Disables dry-run and executes live API uploads")
    parser.add_argument("--interval-hours", type=float, default=4.0, help="Staggered hours fallback")
    parser.add_argument("--platforms", nargs="+", choices=["facebook", "youtube"], default=["facebook"], help="Platforms to schedule (default: facebook only)")

    args = parser.parse_args()

    run_pipeline(
        source=args.source,
        limit=args.limit,
        days=args.days,
        slots_per_day=args.slots_per_day,
        duration=args.duration,
        fps=args.fps,
        posters_only=args.posters_only,
        schedule=args.schedule,
        dry_run=not args.live_publish,
        interval_hours=args.interval_hours,
        platforms=args.platforms,
    )


if __name__ == "__main__":
    main()
