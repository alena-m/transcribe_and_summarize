# Transcribe and Summarize

Transcribe Youtube videos (or any mp3), summarize with chatGPT and save Markdown file formatted for Obsidian.

## Performance tests
Performance tests run on MacBook Pro M2
|lang|whisper_model|video_duration, min|size_mp3, Mb|processing, sec|
|---|---|---|---|------|
|en|small.en|60|87|268|
|en|small.en|120|140|574|
|ru|medium|60|76|797|

## Installation
Script `install.sh` works for macOS only. Run
```bash
./install.sh
```

Alternatively, you can manually install [yt-dlp](https://github.com/yt-dlp/yt-dlp), [ffmpeg](https://ffmpeg.org/), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), `requirements.txt` and replace `examples/main/main.cpp` with provided `main.cpp`.


## How to run
Edit `config.json` with your preferable values:

- `whisper_models` - what [Whisper models](https://github.com/ggerganov/whisper.cpp#more-audio-samples) to download, space-separated string. Based on my experiments `small.en` provides good quality for English audio. For other languages at least `medium` is needed.
- `output_folder` - path for output Markdown file
- `openai_key` - OpenAI API key if you need summary.
- `openai_model` - OpenAI model for summary. Defaul `gpt-3.5-turbo` - good quality and not expensive.

Usage:
```bash
./main.sh [options]

options:
  -u,   youtube url
  -f,   mp3 file name (placed in the current directory)
  -m,   Whisper model
  -l,   language (for Whisper), optional, default is `en`
  -s,   flag if summary is need, optional, if not present summary will not be done
```

`-u` and `-f` are mutually exclusive. One of them must be provided.

### Examples

Transcribe and summarize Youtube video (in English):
```bash
./main.sh -u https://www.youtube.com/watch?v=AaTRHFaaPG8 -m small.en -s
```

Transcribe and summarize Youtube video (in Russian):
```bash
./main.sh -u https://www.youtube.com/watch?v=cMDpWf-aSrs -m medium -l ru -s
```

Transcribe file `some_podcast.mp3` without summary (in English). Don't add `.mp3` to file name:
```bash
./main.sh -f some_podcast -m smal.en
```