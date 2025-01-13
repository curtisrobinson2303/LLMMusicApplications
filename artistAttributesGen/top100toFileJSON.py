import requests
import json
import time

CLIENT_ID = '2349e6e7f26b48f8b76a8e8e6e4d8321'
CLIENT_SECRET = 'ce10691531f94d8eb0d6fe09ee6e2bf9'

# Spotify API URLs
AUTH_URL = 'https://accounts.spotify.com/api/token'
SEARCH_URL = 'https://api.spotify.com/v1/search'
TOP_TRACKS_URL = 'https://api.spotify.com/v1/artists/{id}/top-tracks'
AUDIO_FEATURES_URL = 'https://api.spotify.com/v1/audio-features'

# Authenticate and get the access token
def get_access_token(client_id, client_secret):
    response = requests.post(
        AUTH_URL,
        {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        }
    )
    response_data = response.json()
    return response_data['access_token']

# Fetch top artists by genre
def get_top_artists_by_genre(access_token, genre, limit=5):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'q': f'genre:"{genre}"', 'type': 'artist', 'limit': limit}
    response = requests.get(SEARCH_URL, headers=headers, params=params)
    if response.status_code == 200:
        artists = response.json()['artists']['items']
        return [{'name': artist['name'], 'id': artist['id'], 'genre': genre} for artist in artists]
    else:
        print(f"Error fetching artists for genre {genre}: {response.status_code}")
        return []

# Fetch top tracks for a given artist
def get_top_tracks(access_token, artist_id, country='US'):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(TOP_TRACKS_URL.format(id=artist_id), headers=headers, params={'country': country})
    if response.status_code == 200:
        return response.json()['tracks']
    else:
        print(f"Error fetching top tracks for artist ID {artist_id}: {response.status_code}")
        return []

# Fetch audio features for a list of track IDs
def get_audio_features(access_token, track_ids):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'ids': ','.join(track_ids)}
    response = requests.get(AUDIO_FEATURES_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['audio_features']
    else:
        print(f"Error fetching audio features: {response.status_code}")
        return []

def main():
    genres = ["pop", "rock", "hip hop", "jazz", "classical"]
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    artist_data = []
    for genre in genres:
        print(f"Fetching top artists for genre: {genre}")
        artists = get_top_artists_by_genre(access_token, genre, limit=10)  # Increase limit as needed
        for artist in artists:
            top_tracks = get_top_tracks(access_token, artist['id'])
            for track in top_tracks:
                track_info = {
                    'artist_name': artist['name'],
                    'genre': artist['genre'],
                    'track_name': track['name'],
                    'popularity': track['popularity']
                }
                # Fetch audio features
                audio_features = get_audio_features(access_token, [track['id']])
                if audio_features:
                    audio_feature = audio_features[0]
                    track_info.update({
                        'tempo': audio_feature['tempo'],
                        'key': audio_feature['key'],
                        'energy': audio_feature['energy'],
                        'danceability': audio_feature['danceability']
                    })
                artist_data.append(track_info)
            time.sleep(1)  # To avoid rate limits

    # Save to JSON file
    with open("artist_track_data.json", "w") as file:
        json.dump(artist_data, file, indent=4)

    print("Data saved to 'artist_track_data.json'")

if __name__ == "__main__":
    main()