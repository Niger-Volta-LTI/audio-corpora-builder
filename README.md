# audio corpora builder
Build large audio corpora in various languages &rarr; {Yorùbá, Urhobo, Edo, Èʋe, Igbo}


## Audio Corpora

Curate specific language corpora from the wealth of audio available in good quality on [YouTube](https://www.youtube.com/channel/UCJ6EtHY8NGtpSK5m7fBxytw) 
The process is as follows:
  * Locate a list of existing playlists, e.g. [OrisunTV Iroyin](https://www.youtube.com/playlist?list=PLerPP_LFfERFAYid2qavoTOc81W0fGdnZ)
  * Alternatively, create a new playlist with a custom set of YouTube videos 
  * Update `yoruba_sources.yml` with the reference to the playlist
  * Execute `$ python download_youtube.py --output ./audio/`


## Install dependencies
 * Python 3.5, 3.6 or 3.7
 * `pip install -r requirements.txt`
