#!/usr/bin/env python3
"""
Simple music server that auto-discovers songs in the music/ folder.
Drop .wav, .mp3, .ogg, .flac files in music/ and they appear automatically.

Optional: create a track-meta.json to add tags to specific songs:
{
  "Falling Through the Frets": ["acoustic", "chill"],
  "Salt in My Head": ["electronic", "moody"]
}

Run: python3 server.py
"""

import http.server
import json
import os
import urllib.parse

PORT = 8765
MUSIC_DIR = "music"
META_FILE = "track-meta.json"
AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a"}


def get_tracks():
    meta = {}
    if os.path.exists(META_FILE):
        with open(META_FILE, "r") as f:
            meta = json.load(f)

    tracks = []
    if not os.path.isdir(MUSIC_DIR):
        return tracks

    for filename in sorted(os.listdir(MUSIC_DIR)):
        ext = os.path.splitext(filename)[1].lower()
        if ext in AUDIO_EXTENSIONS:
            title = os.path.splitext(filename)[0]
            tracks.append({
                "title": title,
                "tags": meta.get(title, []),
                "file": f"{MUSIC_DIR}/{filename}",
            })
    return tracks


class MusicHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/tracks":
            tracks = get_tracks()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(tracks).encode())
        else:
            super().do_GET()

    def log_message(self, format, *args):
        # Quieter logging
        pass


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Music server running at http://localhost:{PORT}")
    print(f"Auto-discovering songs in ./{MUSIC_DIR}/")
    server = http.server.HTTPServer(("", PORT), MusicHandler)
    server.serve_forever()
