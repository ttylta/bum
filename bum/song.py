"""
Get song info.
"""
import shutil
import os
import mpd
import pprint
from xdg.BaseDirectory import xdg_config_home

from . import brainz
from . import util


def init(port=6600, server="localhost"):
    """Initialize mpd."""
    client = mpd.MPDClient()

    try:
        client.connect(server, port)
        return client

    except ConnectionRefusedError:
        print("error: Connection refused to mpd/mopidy.")
        os._exit(1)  # pylint: disable=W0212


def get_art(cache_dir, size, client):
    """Get the album art."""
    song = client.currentsong()
    
    if len(song) < 2:
        print("album: Nothing currently playing.")
        util.bytes_to_file(util.default_album_art(), cache_dir / "current.jpg")
        return

    file_name = f"{song['artist']}_{song['album']}_{size}.jpg".replace("/", "")
    file_name = cache_dir / file_name

    mpd_directory = xdg_config_home + "/mpd"
    folder_file = song["file"].split("/")[0] + "/folder.jpg"

    music_directory = "";
    if os.path.isdir(mpd_directory):
        conf = mpd_directory + "/mpd.conf"
        if os.path.isfile(conf):
            with open(conf) as c:
                for line in c:
                    if line.startswith("music_directory"):
                        music_directory = line.split("\"")[1].replace('~', '')
                        print("Found music directory: ", music_directory)
                        break
        else:
            print("There is no mpd.conf in your home directory.")
    else:
        print("There is no mpd folder in your XDG config folder.")


    song_dir = '/'.join(song["file"].split("/")[:-1])
    folder_file = os.path.expanduser("~") + music_directory + "/" + song_dir + "/folder.jpg"

    if os.path.isfile(folder_file):
        print("Using local folder.jpg...")
        shutil.copy(folder_file, cache_dir / "current.jpg")

    elif file_name.is_file():
        shutil.copy(file_name, cache_dir / "current.jpg")
    
    else:
        print("album: Downloading album art...")

        brainz.init()
        album_art = brainz.get_cover(song, size)

        if not album_art:
            album_art = util.default_album_art()

        util.bytes_to_file(album_art, cache_dir / file_name)
        util.bytes_to_file(album_art, cache_dir / "current.jpg")

        print(f"album: Swapped art to {song['artist']}, {song['album']}.")
