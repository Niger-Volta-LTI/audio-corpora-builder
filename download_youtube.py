import argparse
import os

import runez
import yaml


def read_yaml(file_name):
    with open(file_name, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def download(yaml_category, source, source_type):
    if source_type == "playlists":
        output_path_raw = os.path.join(args.output_path, yaml_category, source_type, source.split('&')[-1])
        playlist_archive = os.path.join(output_path_raw, "archive.txt")

        print("Downloading {0} {1} to {2}".format(source_type, source, output_path_raw))
        run_result = runez.run("yt-dlp",
                               "-i",
                               "--download-archive",
                               "%s" % playlist_archive,
                               "--no-post-overwrites",
                               "--max-downloads",
                               "%s" % args.max_downloads,
                               "--extract-audio",
                               "--audio-format",
                               "wav",
                               "%s" % source,
                               "-o",
                               "{}/%(track)s-%(id)s.%(ext)s".format(output_path_raw),
                               fatal=False
                               )
        if run_result.failed:
            print("runez yt-dlp failed, check if the max-downloads is set properly ")
            output_logs = "./download_logs.txt"
            with open(output_logs, mode="wt") as f:
                f.write(run_result.full_output)
                print("Checkout failure details in the {} file".format(output_logs))
        else:
            print("yt-dlp success")

    else:  # source_type == "users"
        output_path_raw = os.path.join(args.output_path, yaml_category, source_type, source.split('/')[-1])
        if os.path.exists(output_path_raw):
            print("skipping {0} because the target folder already exists".format(output_path_raw))
        else:
            print("Downloading for {}: `source_type=={}` {} to {}".format(yaml_category,
                                                                          source_type,
                                                                          source,
                                                                          output_path_raw))
            # If we ever want to download everything from a users URL, set the max downloads to something reasonable
            max_downloads = min(10, args.max_downloads)
            run_result = runez.run("yt-dlp",
                                   "-i",
                                   "--max-downloads",
                                   "%s" % max_downloads,
                                   "--extract-audio",
                                   "--audio-format",
                                   "wav",
                                   "%s" % source,
                                   "-o",
                                   "{}/%(track)s-%(id)s.%(ext)s".format(output_path_raw),
                                   fatal=False
                                   )
            if run_result.failed:
                output_logs = "./download_logs.txt"
                with open(output_logs, mode="wt") as f:
                    f.write(run_result.full_output)
                    print("max-downloads={} was likely hit, see logs={} for details & adjust as needed".
                          format(max_downloads, output_logs))
            else:
                print("yt-dlp success")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="path to download videos and max number")
    parser.add_argument('--output', dest='output_path', default=os.getcwd(), required=True)
    parser.add_argument('--users', dest='users', action='store_true',
                        help='Download from users section if specified.')
    parser.add_argument('--downloads', type=int, dest='max_downloads', default=1200)
    args = parser.parse_args()
    # Example: $Python download_youtube.py --output user/folder/download

    sources = read_yaml("yoruba_sources.yml")
    for yaml_category, categories in sources.items():

        # collect particular playlists
        for playlist_name in categories["playlists"]:
            if playlist_name is None:
                continue
            download(yaml_category, playlist_name, "playlists")

        # collect users (i.e. OrisunTV), but default this option is off unless explicitly specificed with --users
        if args.users:
            for url in categories["users"]:
                if url is None:
                    continue
                download(yaml_category, url, "users")
