import subprocess
import os
import argparse
import string
import yaml


def read_yaml(file_name):
    with open(file_name, "r") as f:
        return yaml.load(f)

def download(language, source, source_name, source_type):

    output_path_raw = os.path.join(args.output_path, "raw", language, source_name.split('/')[-1])
    if source_type == "playlist":
        playlist_archive = os.path.join(output_path_raw, "archive.txt")

        print("Downloading {0} {1} to {2}".format(source_type, source_name, output_path_raw))
        command = """youtube-dl -i --download-archive {} --no-post-overwrites --max-downloads {} --extract-audio --audio-format wav {} -o "{}/%(track)s-%(id)s.%(ext)s" """.format(
            playlist_archive, args.max_downloads, source, output_path_raw)
        subprocess.call(command, shell=True)
    else:       
        if os.path.exists(output_path_raw):
            print("skipping {0} because the target folder already exists".format(output_path_raw))
        else:
            print("Downloading {0} {1} to {2}".format(source_type, source_name, output_path_raw))
            command = """youtube-dl -i --max-downloads {} --extract-audio --audio-format wav {} -o "{}/%(title)s.%(ext)s" """.format(args.max_downloads, source, output_path_raw)
            print(command)
            subprocess.call(command, shell=True)

def download_user(language, user):
    user_selector = "ytuser:%s" % user
    download(language, user_selector, user, "user")


def download_playlist(language, playlist_name, playlist_id):
    download(language, playlist_id, playlist_name, "playlist")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="path to download videos and max number")
    parser.add_argument('--output', dest='output_path', default=os.getcwd(), required=True)
    parser.add_argument('--downloads', type=int, dest='max_downloads', default=1200)
    args = parser.parse_args()
    # Example: $Python download_youtube.py --output user/folder/download

    sources = read_yaml("yoruba_sources.yml")
    for language, categories in sources.items():
        for category in categories["playlists"]:
            if category is None:
                continue

            playlist_name = category
            playlist_id = category
            download_playlist(language, playlist_name, playlist_id)
