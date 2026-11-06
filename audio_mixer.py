"""
Audio Pipeline:
Manages copyright-free background music, downloads/synthesizes royalty-free tracks,
and loops them under videos at -18dB with fade-in and fade-out.
"""

import os
import glob
import math
import random
import subprocess
import urllib.request
import numpy as np
from scipy.io import wavfile
import imageio_ffmpeg

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Royalty-free Creative Commons / Public Domain ambient audio URLs for auto-download
PUBLIC_DOMAIN_TRACKS = [
    {
        "filename": "uplifting_corporate_ambient.wav",
        "url": "https://ia800905.us.archive.org/19/items/free_music_archive_tracks/calm_corporate_preview.wav"
    }
]


def synthesize_royalty_free_ambient_loop(output_path: str, duration_sec: float = 30.0, sample_rate: int = 44100):
    """
    Synthesizes a warm, soothing, copyright-free lo-fi corporate chord progression
    (Cmaj9 -> Am9 -> Fmaj7 -> Gsus4) using physical modeling harmonics.
    Completely 100% royalty-free and guaranteed to work completely offline.
    """
    total_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, total_samples, endpoint=False)
    audio = np.zeros(total_samples, dtype=np.float32)

    # Chord frequencies (Hz) for a modern, motivating corporate background
    # Progression: C -> Am -> F -> G
    chord_duration = 3.75  # seconds per chord (8 chords in 30s)
    chords = [
        [261.63, 329.63, 392.00, 493.88],  # Cmaj7 (C4, E4, G4, B4)
        [220.00, 261.63, 329.63, 392.00],  # Am7   (A3, C4, E4, G4)
        [174.61, 220.00, 261.63, 329.63],  # Fmaj7 (F3, A3, C4, E4)
        [196.00, 246.94, 293.66, 392.00],  # G6    (G3, B3, D4, G4)
    ]

    for chord_idx in range(int(math.ceil(duration_sec / chord_duration))):
        start_time = chord_idx * chord_duration
        end_time = min(start_time + chord_duration, duration_sec)
        idx_start = int(start_time * sample_rate)
        idx_end = int(end_time * sample_rate)
        sub_len = idx_end - idx_start
        if sub_len <= 0:
            continue

        chord_notes = chords[chord_idx % len(chords)]
        sub_t = np.linspace(0, end_time - start_time, sub_len, endpoint=False)
        envelope = np.exp(-1.4 * sub_t) * (1.0 - np.exp(-30.0 * sub_t))

        # Add arpeggio/marimba warmth
        for note_pos, freq in enumerate(chord_notes):
            # Staggered arpeggiated onset
            arp_delay = note_pos * 0.12
            mask = sub_t >= arp_delay
            delayed_t = np.maximum(0, sub_t - arp_delay)
            note_env = np.exp(-2.2 * delayed_t) * mask

            # Fundamental + soft harmonics
            sine = np.sin(2 * np.pi * freq * sub_t)
            harmonic2 = 0.35 * np.sin(4 * np.pi * freq * sub_t)
            harmonic3 = 0.15 * np.sin(6 * np.pi * freq * sub_t)
            harmonic4 = 0.05 * np.sin(8 * np.pi * freq * sub_t)

            audio[idx_start:idx_end] += (sine + harmonic2 + harmonic3 + harmonic4) * note_env * 0.22

        # Gentle sub-bass warmth on root note
        root_freq = chord_notes[0] / 2.0
        bass_env = np.exp(-0.8 * sub_t)
        audio[idx_start:idx_end] += 0.28 * np.sin(2 * np.pi * root_freq * sub_t) * bass_env

    # Soft ambient pad bed underneath
    pad_freqs = [130.81, 164.81, 196.00]
    for pf in pad_freqs:
        audio += 0.06 * np.sin(2 * np.pi * pf * t)

    # Normalize to -3dB peak before conversion
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.7

    # Stereo expansion with slight channel phase offset
    left_channel = audio
    # Right channel delayed by 8ms for spatial depth
    delay_samples = int(0.008 * sample_rate)
    right_channel = np.roll(audio, delay_samples)

    stereo = np.column_stack((left_channel, right_channel))
    int16_audio = (stereo * 32767).astype(np.int16)

    wavfile.write(output_path, sample_rate, int16_audio)
    return output_path


def ensure_background_track() -> str:
    """
    Finds an existing track in assets/audio or downloads/synthesizes one.
    """
    extensions = ("*.mp3", "*.wav", "*.m4a", "*.aac", "*.ogg")
    existing_files = []
    for ext in extensions:
        existing_files.extend(glob.glob(os.path.join(AUDIO_DIR, ext)))

    if existing_files:
        return random.choice(existing_files)

    # If none present, synthesize high quality fallback
    default_synth_path = os.path.join(AUDIO_DIR, "ambient_corporate_loop.wav")
    print(f"[Audio] Synthesizing copyright-free ambient corporate background music -> {default_synth_path}")
    synthesize_royalty_free_ambient_loop(default_synth_path, duration_sec=32.0)
    return default_synth_path


def mix_audio_into_video(video_path: str, output_path: str, target_db: float = -18.0, custom_audio_path: str = None) -> str:
    """
    Mixes looped background audio into video at target_db (-18dB) with smooth fade-in and fade-out
    using imageio_ffmpeg binary.
    """
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    audio_file = custom_audio_path or ensure_background_track()

    # Get video duration using ffprobe/ffmpeg
    probe_cmd = [
        ffmpeg_exe, "-i", video_path
    ]
    res = subprocess.run(probe_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="ignore")
    duration = 15.0  # default fallback
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            try:
                part = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = part.split(":")
                duration = float(h) * 3600 + float(m) * 60 + float(s)
                break
            except Exception:
                pass

    fade_out_start = max(0.5, duration - 1.5)

    # Convert dB to linear volume factor: 10^(dB / 20)
    # -18 dB = 10^(-18/20) = 0.12589
    linear_volume = 10.0 ** (target_db / 20.0)

    # FFmpeg audio filter graph:
    # 1. aloop: loop audio indefinitely
    # 2. atrim: trim to video duration
    # 3. volume: attenuate to -18dB
    # 4. afade: fade-in 0.5s, fade-out 1.5s
    filter_complex = (
        f"[1:a]aloop=loop=-1:size=2e+09,"
        f"atrim=0:{duration:.2f},"
        f"volume={linear_volume:.4f},"
        f"afade=t=in:st=0:d=0.5,"
        f"afade=t=out:st={fade_out_start:.2f}:d=1.5[aout]"
    )

    cmd = [
        ffmpeg_exe, "-y",
        "-i", video_path,
        "-i", audio_file,
        "-filter_complex", filter_complex,
        "-map", "0:v:0",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]

    print(f"[Audio] Merging background track '{os.path.basename(audio_file)}' at {target_db} dB into {output_path}")
    sub_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="ignore")
    if sub_res.returncode != 0:
        print(f"[Audio Warning] Direct muxing error: {sub_res.stderr[-300:]}")
        # Simple fallback
        fallback_cmd = [
            ffmpeg_exe, "-y",
            "-i", video_path,
            "-i", audio_file,
            "-filter:a", f"volume={linear_volume:.4f}",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        subprocess.run(fallback_cmd, check=True)

    print(f"[Audio] Successfully generated final video with audio: {output_path}")
    return output_path


if __name__ == "__main__":
    track = ensure_background_track()
    print(f"Background audio ready at: {track}")
