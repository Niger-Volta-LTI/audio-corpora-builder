# audio corpora builder
Build large audio corpora in various languages &rarr; {Yorùbá, Urhobo, Edo, Èʋe, Igbo}


## Audio Corpora

Curate specific language corpora from the wealth of {speech, dialogues, interviews, films, podcasts, etc}, 
available in good quality on [YouTube](https://www.youtube.com/channel/UCJ6EtHY8NGtpSK5m7fBxytw) &rarr;

### Quick start example (Yorùbá):
  * Locate a list of existing playlists, e.g. [OrisunTV Iroyin](https://www.youtube.com/playlist?list=PLerPP_LFfERFAYid2qavoTOc81W0fGdnZ)
  * Alternatively, create a new playlist with a custom set of YouTube videos 
  * Update `yoruba_sources.yml` with the reference to the playlist
```bash
$ python3 download_youtube.py --output ./audio --sources yoruba_sources.yml --verbose
```


## Install dependencies
 * Python 3.10 or newer
 * `$ python3.10 -m venv venv`
 * `$ pip install -r requirements.txt`


### With custom/different playlist files:
```bash
python3 download_youtube.py --output ./audio/ --sources urhobo_sources.yml
```

### With MP3 format:
```bash
python3 download_youtube.py --output ./audio/ --format mp3
```


## Sanity Test Results

```bash
$ python3 -m pytest tests/test_download.py -v
============================= test session starts ==============================
...
collected 11 items

tests/test_download.py::TestValidateUrl::test_validate_url_valid_playlist PASSED
tests/test_download.py::TestValidateUrl::test_validate_url_valid_user PASSED
tests/test_download.py::TestValidateUrl::test_validate_url_empty PASSED
tests/test_download.py::TestValidateUrl::test_validate_url_none PASSED
tests/test_download.py::TestValidateUrl::test_validate_url_missing_https PASSED
tests/test_download.py::TestValidateUrl::test_validate_url_with_whitespace PASSED
tests/test_download.py::TestBuildYtDlpCommand::test_build_playlist_command PASSED
tests/test_download.py::TestBuildYtDlpCommand::test_build_users_command PASSED
tests/test_download.py::TestBuildYtDlpCommand::test_build_command_output_path PASSED
tests/test_download.py::TestBuildYtDlpCommand::test_build_command_audio_format PASSED
tests/test_download.py::TestBuildYtDlpCommand::test_build_command_invalid_source_type PASSED

============================== 11 passed in 0.03s ==============================
```