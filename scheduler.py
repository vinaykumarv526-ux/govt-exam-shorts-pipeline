"""
Multi-Platform Social Media Scheduler:
Uploads and schedules 9:16 vertical videos to YouTube Shorts (YouTube Data API v3)
and Facebook Reels (Meta Graph API / Pages API).
Includes validation, simulated dry-run mode, and automated metadata formatting.
"""

import os
import sys
import time
import json
import datetime
from typing import Dict, Any, Optional, Tuple
import requests
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

# YouTube API configuration
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
YOUTUBE_TOKEN_FILE = os.getenv("YOUTUBE_TOKEN_FILE", "youtube_token.json")

# Meta Graph API configuration
META_PAGE_ID = os.getenv("META_PAGE_ID", "")
META_PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN", "")
META_GRAPH_API_VERSION = os.getenv("META_GRAPH_API_VERSION", "v19.0")


def generate_social_metadata(exam_data: Dict[str, Any], scheduled_dt: datetime.datetime = None) -> Dict[str, Any]:
    """Formats rich, high-engagement title, description, and tags for Shorts & Reels."""
    raw_title = exam_data.get("title", "Government Job Recruitment 2026")
    vac = exam_data.get("vacancy_callout", "Latest Vacancies")
    org = exam_data.get("org_short", "Govt Exam")

    # YouTube Shorts title (Max 100 chars, ideal 60-80 chars)
    yt_title = f"{org}: {vac} | Apply Online #Shorts"
    if len(yt_title) > 95:
        yt_title = f"{org} Recruitment 2026 #Shorts"

    # Rich formatted description with full exam specifications
    specs = exam_data.get("table", {})
    specs_lines = "\n".join([f"📌 {k}: {v}" for k, v in specs.items()])

    notif_url = exam_data.get("notification_url", "https://www.freejobalert.com")
    apply_url = exam_data.get("apply_url", notif_url)

    description = f"""📢 {raw_title}
🔥 Total Vacancies: {vac}

📋 KEY SPECIFICATIONS:
{specs_lines}

🔗 IMPORTANT LINKS:
👉 Official Notification: {notif_url}
👉 Online Application: {apply_url}

🔔 Subscribe to our channel for daily instant government job alerts, syllabus, and admit cards!
#Shorts #GovtJobs #JobAlert #FreeJobAlert #{org.replace(' ', '')} #GovtExam2026 #SarkariNaukri
"""

    tags = exam_data.get("tags", ["GovtJobs", "JobAlert", "Shorts", "SarkariResult"])
    base_tags = ["Shorts", "GovtJobs", "SarkariNaukri", "JobAlert", "EmploymentNews", org]
    all_tags = list(dict.fromkeys(tags + base_tags))

    return {
        "title": yt_title,
        "description": description.strip(),
        "tags": all_tags,
        "scheduled_time": scheduled_dt or (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)),
    }


# =====================================================================
# YOUTUBE SHORTS PUBLISHER (YouTube Data API v3)
# =====================================================================

def get_youtube_service():
    """Initializes authorized YouTube service instance using OAuth 2.0."""
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError:
        print("[YouTube Warning] google-api-python-client / google-auth-oauthlib not installed.")
        return None

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = None

    if os.path.exists(YOUTUBE_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(YOUTUBE_TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"[YouTube Auth] Refresh failed: {e}")
                creds = None
        if not creds and os.path.exists(YOUTUBE_CLIENT_SECRETS_FILE):
            try:
                flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRETS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(YOUTUBE_TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"[YouTube Auth] Flow authorization failed: {e}")
                return None

    if not creds:
        return None

    return build("youtube", "v3", credentials=creds)


def upload_to_youtube_shorts(
    video_path: str,
    metadata: Dict[str, Any],
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Uploads a video to YouTube as a Short with scheduled publishing.
    """
    print(f"\n[YouTube Publisher] Preparing upload for: {os.path.basename(video_path)}")
    print(f"  • Title: {metadata['title']}")
    print(f"  • Scheduled Date (UTC): {metadata['scheduled_time'].isoformat()}")

    if dry_run or not os.path.exists(YOUTUBE_CLIENT_SECRETS_FILE) and not os.path.exists(YOUTUBE_TOKEN_FILE):
        print("  [DRY RUN / SIMULATION MODE] (No YouTube credentials found or --dry-run active)")
        simulated_id = f"yt_sim_{int(time.time())}"
        return {
            "status": "simulated",
            "platform": "YouTube Shorts",
            "video_id": simulated_id,
            "url": f"https://youtube.com/shorts/{simulated_id}",
            "scheduled_time": metadata["scheduled_time"].isoformat(),
        }

    youtube = get_youtube_service()
    if not youtube:
        raise RuntimeError("Failed to authenticate YouTube API. Check client_secrets.json.")

    from googleapiclient.http import MediaFileUpload

    # Format publish time to RFC 3339
    publish_at_rfc = metadata["scheduled_time"].strftime("%Y-%m-%dT%H:%M:%SZ")

    body = {
        "snippet": {
            "title": metadata["title"][:100],
            "description": metadata["description"],
            "tags": metadata["tags"][:20],
            "categoryId": "27",  # Education
        },
        "status": {
            "privacyStatus": "private",  # Required for scheduled release
            "publishAt": publish_at_rfc,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=1024 * 1024 * 4, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  • Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    video_url = f"https://youtube.com/shorts/{video_id}"
    print(f"  ✓ Successfully scheduled YouTube Short! ID: {video_id} -> {video_url}")

    return {
        "status": "scheduled",
        "platform": "YouTube Shorts",
        "video_id": video_id,
        "url": video_url,
        "scheduled_time": publish_at_rfc,
    }


# =====================================================================
# META GRAPH API PUBLISHER (Facebook Reels for Pages)
# =====================================================================

def upload_to_facebook_reels(
    video_path: str,
    metadata: Dict[str, Any],
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Publishes / schedules video reels to Facebook Pages via Meta Graph API v19.0.
    Follows official 3-step Reels publishing protocol:
    1. Initialize upload session
    2. Stream video binary
    3. Finalize and schedule with publish time
    """
    print(f"\n[Meta Publisher] Preparing Facebook Reel: {os.path.basename(video_path)}")

    if dry_run or not META_PAGE_ID or not META_PAGE_ACCESS_TOKEN:
        print("  [DRY RUN / SIMULATION MODE] (META_PAGE_ID or META_PAGE_ACCESS_TOKEN not set)")
        sim_id = f"fb_reel_{int(time.time())}"
        return {
            "status": "simulated",
            "platform": "Facebook Reels",
            "video_id": sim_id,
            "url": f"https://facebook.com/reel/{sim_id}",
            "scheduled_time": metadata["scheduled_time"].isoformat(),
        }

    # Step 1: Initialize session
    init_url = f"https://graph.facebook.com/{META_GRAPH_API_VERSION}/{META_PAGE_ID}/video_reels"
    init_params = {
        "upload_phase": "start",
        "access_token": META_PAGE_ACCESS_TOKEN,
    }
    init_resp = requests.post(init_url, data=init_params)
    init_data = init_resp.json()

    if "video_id" not in init_data:
        raise RuntimeError(f"Meta Reels start failed: {init_data}")

    video_id = init_data["video_id"]
    upload_url = init_data.get("upload_url", f"https://rupload.facebook.com/video-reels/{video_id}")

    # Step 2: Upload Binary
    file_size = os.path.getsize(video_path)
    with open(video_path, "rb") as vf:
        headers = {
            "Authorization": f"OAuth {META_PAGE_ACCESS_TOKEN}",
            "offset": "0",
            "file_size": str(file_size),
            "Content-Type": "application/octet-stream",
        }
        upload_resp = requests.post(upload_url, data=vf, headers=headers)
        if upload_resp.status_code not in (200, 201):
            raise RuntimeError(f"Meta binary upload failed: {upload_resp.text}")

    # Step 3: Finish & Schedule
    scheduled_unix = int(metadata["scheduled_time"].timestamp())
    finish_params = {
        "upload_phase": "finish",
        "access_token": META_PAGE_ACCESS_TOKEN,
        "video_id": video_id,
        "video_state": "SCHEDULED",
        "scheduled_publish_time": scheduled_unix,
        "description": f"{metadata['title']}\n\n{metadata['description']}",
    }

    finish_resp = requests.post(init_url, data=finish_params)
    finish_data = finish_resp.json()

    if not finish_data.get("success", False):
        raise RuntimeError(f"Meta finish failed: {finish_data}")

    reel_url = f"https://facebook.com/reel/{video_id}"
    print(f"  ✓ Successfully scheduled Facebook Reel! ID: {video_id} -> {reel_url}")

    return {
        "status": "scheduled",
        "platform": "Facebook Reels",
        "video_id": video_id,
        "url": reel_url,
        "scheduled_time": metadata["scheduled_time"].isoformat(),
    }


def publish_exam_short(
    video_path: str,
    exam_data: Dict[str, Any],
    scheduled_dt: datetime.datetime = None,
    platforms: Tuple[str] = ("youtube", "facebook"),
    dry_run: bool = False
) -> Dict[str, Any]:
    """Coordinates multi-platform upload and returns audit summary."""
    meta = generate_social_metadata(exam_data, scheduled_dt)
    results = {}

    if "youtube" in platforms:
        try:
            results["youtube"] = upload_to_youtube_shorts(video_path, meta, dry_run=dry_run)
        except Exception as e:
            results["youtube"] = {"status": "error", "error": str(e)}

    if "facebook" in platforms:
        try:
            results["facebook"] = upload_to_facebook_reels(video_path, meta, dry_run=dry_run)
        except Exception as e:
            results["facebook"] = {"status": "error", "error": str(e)}

    return results


if __name__ == "__main__":
    from scraper import load_mock_exams
    exams = load_mock_exams()
    if exams:
        sample_meta = generate_social_metadata(exams[0])
        print("Generated Social Metadata Preview:")
        print("Title:", sample_meta["title"])
        print("\nDescription Snippet:\n", sample_meta["description"][:250], "...\n")
        print("Tags:", sample_meta["tags"])
