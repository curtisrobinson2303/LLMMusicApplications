import requests
import csv
import time

CLIENT_ID = '2349e6e7f26b48f8b76a8e8e6e4d8321'
CLIENT_SECRET = 'ce10691531f94d8eb0d6fe09ee6e2bf9'

# Spotify API URLs
AUTH_URL = 'https://accounts.spotify.com/api/token'
SEARCH_URL = 'https://api.spotify.com/v1/search'
TOP_TRACKS_URL = 'https://api.spotify.com/v1/artists/{id}/top-tracks'
AUDIO_FEATURES_URL = 'https://api.spotify.com/v1/audio-features'

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
    if response.status_code == 200:
        return response_data['access_token']
    else:
        print(f"Error fetching access token: {response_data}")
        return None

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

def get_top_tracks(access_token, artist_id, country='US'):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(TOP_TRACKS_URL.format(id=artist_id), headers=headers, params={'country': country})
    if response.status_code == 200:
        return response.json()['tracks']
    else:
        print(f"Error fetching top tracks for artist ID {artist_id}: {response.status_code}")
        return []

def get_audio_features(access_token, track_ids):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'ids': ','.join(track_ids)}
    response = requests.get(AUDIO_FEATURES_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['audio_features']
    elif response.status_code == 403:
        print("Access forbidden: Check if the access token is still valid or if the endpoint requires user authentication.")
        return []
    else:
        print(f"Error fetching audio features: {response.status_code}")
        return []

def main():
    genres = ["pop", "rock", "hip hop", "jazz", "classical"]
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    if not access_token:
        print("Failed to authenticate. Exiting.")
        return

    song_count = 0
    target_songs = 10000

    with open("artist_track_data.csv", "w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Artist Name', 'Genre', 'Track Name', 'Popularity', 'Tempo', 'Key', 'Energy', 'Danceability'])

        for genre in genres:
            print(f"Fetching top artists for genre: {genre}")
            artists = get_top_artists_by_genre(access_token, genre, limit=50)
            for artist in artists:
                if song_count >= target_songs:
                    break
                top_tracks = get_top_tracks(access_token, artist['id'])
                for track in top_tracks:
                    if song_count >= target_songs:
                        break
                    track_info = [
                        artist['name'],
                        artist['genre'],
                        track['name'],
                        track['popularity']
                    ]
                    audio_features = get_audio_features(access_token, [track['id']])
                    if audio_features and audio_features[0]:
                        audio_feature = audio_features[0]
                        track_info.extend([
                            audio_feature.get('tempo', None),
                            audio_feature.get('key', None),
                            audio_feature.get('energy', None),
                            audio_feature.get('danceability', None)
                        ])
                    else:
                        track_info.extend([None, None, None, None])
                    writer.writerow(track_info)
                    song_count += 1
                time.sleep(1)

    print(f"Data for {song_count} songs saved to 'artist_track_data.csv'")

if __name__ == "__main__":
    main()