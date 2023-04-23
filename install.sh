#!/bin/bash
set -e

msg() {
    echo [`date "+%Y-%m-%d %H:%M:%S"`] "${1-}"
}

export HOMEBREW_NO_AUTO_UPDATE=1
export HOMEBREW_AUTO_UPDATING=0
export HOMEBREW_UPDATE_PREINSTALL=0

if ! [ command -v yt-dlp &> /dev/null ]; then
    msg "Install yt-dlp..."
    brew install yt-dlp
fi

if ! [ command -v ffmeg &> /dev/null ]; then
    msg "Install ffmpeg..."
    brew install ffmpeg
fi

if ! [ command -v jq &> /dev/null ]; then
    msg "Install jq..."
    brew install jq
fi

whisper_dir="whisper.cpp"
whisper_models=$( jq -r '.whisper_models' config.json; )
if ! [ -d "$whisper_dir" ]; then
    msg "Install whisper.cpp and download $whisper_models..."
    git clone https://github.com/ggerganov/whisper.cpp.git
    
    cd whisper.cpp
    for i in $whisper_models; do ./models/download-ggml-model.sh "$i"; done
    # replace origin main.cpp with modified output_txt() to remove extra new line characters
    cp ../main.cpp examples/main/
    make
fi

msg "Installation is finished."