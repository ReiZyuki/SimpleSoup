# SimpleSoup

A simple Python wrapper for yt-dlp and FFmpeg.

## Installation

```bash
pip install simplesoup

For gallery support:

pip install "simplesoup[gallery]"

Import

from simplesoup import rz

Basic Syntax

result = rz({
    "WHAT_TO_REQUEST": "VARIABLE_NAME"
}, url)

WHAT_TO_REQUEST batata hai kya chahiye, aur VARIABLE_NAME batata hai result mein us value ko kis naam se save karna hai.

Example:

result = rz({
    "title": "title"
}, url)

print(result["title"])

Video Download

result = rz({
    "video[4]": "video"
}, url)

print(result["video"])

video[4] = 720p.

Video Quality

video[0] → audio
video[2] → 360p
video[3] → 480p
video[4] → 720p
video[5] → 1080p
video[6] → best available

Example:

result = rz({
    "video[5]": "video"
}, url)

Multiple Values At Once

Ek hi request mein video aur metadata dono le sakte ho:

result = rz({
    "video[4]": "video",
    "title": "title",
    "creator": "creator",
    "url": "video_url",
    "views": "views",
    "likes": "likes",
    "count": "comments",
    "time": "duration",
    "thumbnail": "thumbnail"
}, url)

Values access karne ke liye:

print(result["video"])
print(result["title"])
print(result["creator"])
print(result["video_url"])
print(result["views"])
print(result["likes"])
print(result["comments"])
print(result["duration"])
print(result["thumbnail"])

Order matter nahi karta.

Metadata

Available metadata:

title      → video title
creator    → uploader/channel
url        → video URL
views      → view count
likes      → like count
count      → comment count
time       → duration in seconds
thumbnail  → downloaded thumbnail path
formats    → available yt-dlp formats

Metadata Only

Agar sirf metadata chahiye aur video download nahi karna:

result = rz({
    "title": "title",
    "creator": "creator",
    "views": "views",
    "likes": "likes",
    "count": "comments",
    "time": "duration"
}, url)

video[...] block nahi hone par video download nahi hota.

Thumbnail

result = rz({
    "thumbnail": "thumbnail"
}, url)

print(result["thumbnail"])

Thumbnail actual .jpg file ke roop mein download hota hai.

Playlist

Playlist syntax:

result = rz({
    "playlist": "QUALITY:SKIP:COUNT"
}, playlist_url)

Example:

result = rz({
    "playlist": "4:20:3"
}, playlist_url)

Meaning:

4  → 720p
20 → first 20 videos skip
3  → next 3 videos download

So:

Video 1-20 → skip
Video 21   → download
Video 22   → download
Video 23   → download

Downloaded videos:

for video in result["videos"]:
    print(video)

Playlist + Metadata

result = rz({
    "playlist": "4:20:3",
    "title": "playlist_title"
}, playlist_url)

print(result["playlist_title"])
print(result["videos"])

Gallery

Gallery downloading ke liye:

result = rz({
    "gallery": "images"
}, gallery_url)

print(result)

Gallery support ke liye gallery-dl install hona chahiye:

pip install "simplesoup[gallery]"

Cookies

Cookies simplesoup/core.py mein configure kiye jaate hain:

COOKIES = "/storage/emulated/0/Download/cookies.txt"

Example:

COOKIES = "/storage/emulated/0/Download/reddit_cookies.txt"

Cookies disable karne ke liye:

COOKIES = None

SimpleSoup configured cookie file ko use karta hai.

Progress Callback

Optional progress callback:

def progress(percent, speed, mode):
    print(
        f"[Download {percent}] "
        f"[Network {speed}] "
        f"[Mode {mode}]"
    )

result = rz(
    {
        "video[4]": "video"
    },
    url,
    progress_callback=progress
)

Callback ko ye 3 values milti hain:

percent → download percentage
speed   → network speed
mode    → Video / Playlist

Complete Example

from simplesoup import rz

url = "VIDEO_URL"

result = rz({
    "video[4]": "video",
    "title": "title",
    "creator": "creator",
    "url": "video_url",
    "views": "views",
    "likes": "likes",
    "count": "comments",
    "time": "duration",
    "thumbnail": "thumbnail"
}, url)

print("Video:", result["video"])
print("Title:", result["title"])
print("Creator:", result["creator"])
print("URL:", result["video_url"])
print("Views:", result["views"])
print("Likes:", result["likes"])
print("Comments:", result["comments"])
print("Duration:", result["duration"])
print("Thumbnail:", result["thumbnail"])

Default Download Location

/storage/emulated/0/Download/ReiDownloader/

API Syntax Summary

Single video:

rz({
    "video[QUALITY]": "variable"
}, url)

Metadata:

rz({
    "title": "variable",
    "creator": "variable",
    "url": "variable",
    "views": "variable",
    "likes": "variable",
    "count": "variable",
    "time": "variable",
    "thumbnail": "variable"
}, url)

Video + metadata:

rz({
    "video[4]": "video",
    "title": "title",
    "creator": "creator",
    "views": "views",
    "likes": "likes",
    "count": "comments",
    "time": "duration",
    "thumbnail": "thumbnail"
}, url)

Playlist:

rz({
    "playlist": "QUALITY:SKIP:COUNT"
}, playlist_url)

Gallery:

rz({
    "gallery": "variable"
}, gallery_url)

Version

SimpleSoup 0.1.0
