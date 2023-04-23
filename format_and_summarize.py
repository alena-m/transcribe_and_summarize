import argparse
from datetime import datetime
import json
import logging
import openai
import re
import sys

import logging
logging.basicConfig(
    level=logging.INFO,
    format= '[%(asctime)s] [%(filename)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def format_duration(seconds):
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def split_to_paragraphs(text):
    text = text.replace("\n-", "\n—")
    sentences = text.split('. ')
 
    sub_lists = []
    num_sentences = 5
    for idx in range(0, len(sentences), num_sentences):
        paragraph = ". ".join(sentences[idx:idx+num_sentences])
        sub_lists.append(paragraph)
    return ".\n\n".join(sub_lists)


def read_file(file_name):
    with open(file_name) as f:
        if ".json" in file_name:
           return json.load(f)
        elif ".txt" in file_name:
            line_lst = [line.lstrip() for line in f.readlines()]
            return''.join(line_lst)
        else:
            return f.read()


def get_batches(text, max_tokens):
    batches = []
    sentences = re.findall(r'[^.!?]+[.!?]', text)

    current_batch = ""
    for sentence in sentences:
        if len(current_batch.split(" ")) + len(sentence.split(" ")) <= max_tokens:
            current_batch += sentence
        else:
            batches.append(current_batch)
            current_batch = sentence
    
    if len(batches) == 0:
        batches.append(current_batch)

    return batches

def summarize_text(text, api_key, model, batch_size=2500):    
    openai.api_key = api_key

    text_batches = get_batches(text, batch_size)
    num_batches = len(text_batches)
    logging.info(f"Batches for summarization: {num_batches}")

    summary = ""
    i = 1
    used_tokens = 0
    logging.info("Summarization...")    
    for text_batch in text_batches:
        logging.info(f"Summarise batch {i} out of {num_batches}...")

        response = openai.ChatCompletion.create(
            model = model,
            messages = [
                {"role": "system", "content": "You are a helpful assistant that  makes professional and concise summary with less than 80 words."},
                {"role": "user", "content": f"Summarize this text with less than 80 words: {text_batch}"}
            ],
            temperature = 0.5,
            max_tokens = 120
        )

        used_tokens += response["usage"]["total_tokens"]
        summary += response['choices'][0]['message']["content"] + "\n\n"
        i+=1

    logging.info(f"Used OpenAI tokens: {used_tokens}")
    return summary


parser = argparse.ArgumentParser()
parser.add_argument("-f", type=str)
parser.add_argument("-d", type=str)
parser.add_argument("-s", action="store_true")
args = parser.parse_args()


def main():
    config = read_file("config.json")
    transript = read_file("transcript.txt")

    if args.s:
        summary = summarize_text(transript, config["openai_key"], config["openai_model"])
    else:
        summary = ""
    
    # if we process audio file
    if args.f: 
        title = args.f.replace(":", ".").replace('|', '-')
        duration = args.d.strip().split(" ")[1].split(".")[0]
        template = read_file("template_mp3.md")

        header = template.format(
                            title, 
                            datetime.now().strftime('%Y-%m-%d'),
                            duration,
                            title,
                            summary)
        
        file_name = f"{title}.md"

    # if we process youtube video
    else: 
        metadata = read_file("temp.info.json")
        template = read_file("template_youtube.md")
        title = metadata['title'].replace(':', '.').replace('|', '-')
        
        header = template.format(title, 
                            metadata["channel"], 
                            datetime.now().strftime('%Y-%m-%d'),
                            f"{metadata['upload_date'][0:4]}-{metadata['upload_date'][4:6]}-{metadata['upload_date'][6:8]}",
                            format_duration(metadata["duration"]),
                            metadata["like_count"] if "like_count" in metadata.keys() else 0,
                            metadata["view_count"] if "view_count" in metadata.keys() else 0,
                            metadata["comment_count"] if "comment_count" in metadata.keys() else 0,
                            metadata["webpage_url"],
                            title,
                            summary)
        
        file_name = f"{title}.md"


    final_text = split_to_paragraphs(transript)

    output_path = f"{config['output_folder']}/{file_name}"
    with open(output_path, "w") as f:
        f.write(header + "\n")
        f.write(final_text)


if __name__ == "__main__":
    main()