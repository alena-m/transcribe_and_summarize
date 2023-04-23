#!/bin/bash
set -e

msg() {
    echo [`date "+%Y-%m-%d %H:%M:%S"`] "${1-}"
}
start_time="$(date -u +%s)"

file=""
url=""
mode=""
lang="en"

# Parse the named arguments
while getopts "f:u:m:l:s" opt; do
  case $opt in
    f) file="$OPTARG"
    ;;
    u) url="$OPTARG"
    ;;
    m) model="$OPTARG"
    ;;
    l) lang="$OPTARG"
    ;;
    s) summary=true
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

# Check that either a file or a URL was specified
if [ -z "$file" ] && [ -z "$url" ]; then
  echo "Either a file or a URL must be specified"
  exit 1
fi

if [ ! -z "$file" ] 
then
  audio_file_name=$file
else
  audio_file_name="temp"
fi


if [ ! -z "$url" ]; then
  echo "URL: $url"
  msg "Extracting mp3 from $url..."
  yt-dlp -f bestaudio -x --audio-format mp3 --audio-quality 0 --add-metadata -o "$audio_file_name.%(ext)s" $url --write-info-json --force-overwrites -q
fi

msg "Converting mp3 to wav 16kHz..."
ffmpeg -i "$audio_file_name.mp3" -ar 16000 -ac 1 -c:a pcm_s16le "$audio_file_name.wav" -nostats -loglevel 16 -y

msg "Transcribing using model $2..."
whisper.cpp/main -f "$audio_file_name.wav" -otxt -of transcript -nt -pp -m whisper.cpp/models/ggml-$model.bin -l $lang

msg "Formating output..."
cmd="python3 format_and_summarize.py"
if [ ! -z "$file" ]; then
  duration=$(ffmpeg -i "$audio_file_name.mp3" 2>&1 | grep Duration | awk -F'[:,.]' '{print $2":"$3":"$4}')
  cmd+=" -f $audio_file_name -d $duration"
fi
if [ "$summary" = true ]; then
    cmd+=" -s"
fi
eval $cmd


msg "Clean up..."
rm -f temp.mp3
rm -f $audio_file_name.wav
rm -f temp.info.json
rm -f temp.webm
rm -f transcript.txt

msg "All DONE!"
end_time="$(date -u +%s)"
secs="$(($end_time-$start_time))"
elapsed=$(printf '%02dh:%02dm:%02ds\n' $(($secs/3600)) $(($secs%3600/60)) $(($secs%60)))
msg "Total elapsed time: $elapsed"
