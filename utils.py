import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings


def get_spotify_client(request):
    token_info = request.session.get("spotify_token")

    if not token_info:
        return None  # No token found, user needs to re-authenticate

    return spotipy.Spotify(auth=token_info["access_token"])


def get_song_details(song_id):
    sp = get_spotify_client()
    return sp.track(song_id)
