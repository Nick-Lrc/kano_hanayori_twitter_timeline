# @Kanolive_ Twitter Archive Workspace

## Introduction

- This workspace includes the source code of [Kano Hanayori - Twitter Archive](https://github.com/Nick-Lrc/kano_hanayori_twitter).
- This project is initially designed to achive Twitter data of [Kanolive_](https://twitter.com/Kanolive_), but you can try it with different users.
  - You will need to modify `./src/config/twitter.json`.
- Status
  - Jun 14, 2021: Done 1st round rafctoring. The current code is fully functional. You can use it if you want.
  - Jun 19, 2021: Undergoing the 2nd round.

## Requirements

- Program
  - [FFmpeg](https://www.ffmpeg.org/)
  - [Python](https://www.python.org/): &ge; 3.8
- Packages
  - Note: `run.py` or `src/setup.py` will attempt to install the following packages automatically. 
  - [Tweepy](https://github.com/tweepy/tweepy): &ge; 4.0.0.a (Latest version from GitHub)
  - [You-Get](https://github.com/soimort/you-get)
  - [youtube-dl](https://github.com/ytdl-org/youtube-dl/)
  - [Pillow](https://github.com/python-pillow/Pillow)
- [Twitter API credentials](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api)
  - Save your credential in `./src/configs/credentials.json`
  - See `./src/configs/credentials_template.json` for template.
- Disk space
  - ~ 30 GB

## Usage

```bash
python run.py
```

- Note: The following paths are relative to the project root directory.
- This script:
  - Downloads Twitter text and media data to `./data`
  - Writes `./index.html`.
- To adjust the running configuration, see `./src/configs/scripts.json`.
- `run.py` does not export the resulting work by default.
  - To export the work without video files **after** a regular run, use

```bash
python run.py -i src/configs/scripts_export.json
```
