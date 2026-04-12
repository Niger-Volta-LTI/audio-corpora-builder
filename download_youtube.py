import argparse
import logging
import os
import sys
from urllib.parse import urlparse, parse_qs

import runez
import yaml

LOGGER = logging.getLogger(__name__)


def read_yaml(file_name):
    """Load and validate YAML configuration file."""
    try:
        with open(file_name, "r") as f:
            sources = yaml.load(f, Loader=yaml.FullLoader)
        validate_sources(sources, file_name)
        return sources
    except FileNotFoundError:
        LOGGER.error(f"Configuration file not found: {file_name}")
        raise
    except yaml.YAMLError as e:
        LOGGER.error(f"Invalid YAML in {file_name}: {e}")
        raise


def validate_sources(sources, file_name):
    """Validate sources dictionary structure."""
    if not sources:
        LOGGER.error(f"Configuration file {file_name} is empty or invalid")
        raise ValueError(f"Empty configuration in {file_name}")

    for category, data in sources.items():
        if not isinstance(data, dict):
            LOGGER.error(
                f"Category '{category}' must be a dictionary with 'playlists' and 'users' keys"
            )
            raise ValueError(
                f"Invalid structure for category '{category}' in {file_name}"
            )

        if "playlists" not in data:
            LOGGER.error(f"Category '{category}' missing 'playlists' key")
            raise ValueError(
                f"Missing 'playlists' in category '{category}' of {file_name}"
            )

        if "users" not in data:
            LOGGER.error(f"Category '{category}' missing 'users' key")
            raise ValueError(f"Missing 'users' in category '{category}' of {file_name}")


def validate_url(url, source_type):
    """Validate YouTube URL format."""
    if not url:
        return False, f"Empty URL for {source_type}"

    url = url.strip()
    if not url.startswith("https://"):
        return False, f"URL must start with 'https://': {url}"

    if "youtube.com" not in url and "youtu.be" not in url:
        LOGGER.warning(f"URL may not be a YouTube link: {url}")

    return True, url

def extract_playlist_id(url):
    """Extract YouTube playlist ID from URL.
    Args:       url: YouTube playlist URL
    Returns:    Playlist ID string
    Raises:     ValueError: If URL is invalid or doesn't contain a playlist ID
    """
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        playlist_id = query_params.get('list', [None])[0]

        if not playlist_id:
            raise ValueError(f"No playlist ID found in URL: {url}")

        # Basic validation: playlist IDs are typically alphanumeric
        if not playlist_id.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Invalid playlist ID format: {playlist_id}")

        return playlist_id
    except Exception as e:
        raise ValueError(f"Failed to parse playlist URL '{url}': {e}")


def build_yt_dlp_command(source, source_type, output_path, max_downloads, audio_format="wav"):
    """Build yt-dlp command arguments based on a source type."""
    args = ["yt-dlp", "-i", "--progress"]

    if source_type == "playlists":
        archive_path = os.path.join(output_path, "archive.txt")
        args.extend(["--download-archive", archive_path, "--no-post-overwrites"])
        args.extend(["--max-downloads", str(max_downloads)])

    elif source_type == "users":
        args.extend(["--max-downloads", str(min(10, max_downloads))])

    else:
        raise ValueError(f"Unknown source type: {source_type}")

    args.extend(["--extract-audio", "--audio-format", audio_format, source, "-o", f"{output_path}/%(track)s-%(id)s.%(ext)s"])
    return args


def download(yaml_category, source, source_type, args):
    """Download audio from a YouTube source."""
    if not source or not source.strip():
        LOGGER.warning(f"Skipping empty {source_type} in category '{yaml_category}'")
        return True

    valid, result = validate_url(source, source_type)
    if not valid:
        LOGGER.error(f"Invalid URL in category '{yaml_category}': {result}")
        return False

    source = result
    if source_type == "playlists":
        # Extract playlist ID safely from URL
        try:
            playlist_id = extract_playlist_id(source)
        except ValueError as e:
            sys.stdout.write(f"[ERROR] {e}\n")
            sys.stdout.flush()
            return None
        output_path = os.path.join(args.output_path, yaml_category, source_type, playlist_id)

    elif source_type == "users":
        source_id = source.split("/")[-1]
        output_path = os.path.join(
            args.output_path, yaml_category, source_type, source_id
        )
    else:
        LOGGER.error(f"Unknown source type: {source_type}")
        return False

    os.makedirs(output_path, exist_ok=True)
    LOGGER.info(f"Downloading {source_type} to {output_path}")
    command = build_yt_dlp_command(
        source=source,
        source_type=source_type,
        output_path=output_path,
        max_downloads=args.max_downloads,
        audio_format=args.audio_format,
    )
    run_result = runez.run(*command, fatal=False)

    if run_result.failed:
        _handle_download_failure(run_result, source_type, source, output_path)
        return False

    LOGGER.info(f"Successfully downloaded {source_type}: {source}")
    return True


def _handle_download_failure(run_result, source_type, source, output_path):
    """Handle download failure with helpful error messages."""
    output_logs = "./download_logs.txt"
    with open(output_logs, mode="wt") as f:
        f.write(run_result.full_output)

    error_msg = f"Failed to download {source_type}: {source}"
    if "max-downloads" in run_result.full_output.lower():
        error_msg += (
            f" - max-downloads limit likely exceeded. Check {output_logs} for details."
        )
    elif "playlist" in run_result.full_output.lower():
        error_msg += " - playlist may be private or invalid."
    elif "video" in run_result.full_output.lower():
        error_msg += " - video may be unavailable or region-locked."
    else:
        error_msg += f" - see {output_logs} for full error output."

    LOGGER.error(error_msg)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Download YouTube audio for language corpora")
    parser.add_argument(
        "--output",
        dest="output_path",
        default=os.getcwd(),
        required=True,
        help="Output directory for downloaded audio",
    )
    parser.add_argument(
        "--sources",
        dest="sources_file",
        default="yoruba_sources.yml",
        help="Sources configuration file (default: yoruba_sources.yml)",
    )
    parser.add_argument(
        "--users",
        dest="download_users",
        action="store_true",
        help="Download from users section if specified (default: off)",
    )
    parser.add_argument(
        "--format",
        dest="audio_format",
        choices=["wav", "mp3", "flac"],
        default="wav",
        help="Audio format (default: wav)",
    )
    parser.add_argument(
        "--downloads",
        type=int,
        dest="max_downloads",
        default=1200,
        help="Maximum number of downloads per source (default: 1200)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    LOGGER.info(f"Loading sources from {args.sources_file}")
    try:
        sources = read_yaml(args.sources_file)
    except (FileNotFoundError, yaml.YAMLError, ValueError) as e:
        LOGGER.error(f"Failed to load sources: {e}")
        return 1

    total_downloads, successful, failed = 0,0,0
    for yaml_category, categories in sources.items():
        LOGGER.info(f"Processing category: {yaml_category}")

        for playlist_name in categories["playlists"]:
            if playlist_name:
                total_downloads += 1
                if download(yaml_category, playlist_name, "playlists", args):
                    successful += 1
                else:
                    failed += 1

        if args.download_users:
            for url in categories["users"]:
                if url:
                    total_downloads += 1
                    if download(yaml_category, url, "users", args):
                        successful += 1
                    else:
                        failed += 1

    LOGGER.info(f"Download complete: {successful}/{total_downloads} successful, {failed} failed")
    if failed > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
