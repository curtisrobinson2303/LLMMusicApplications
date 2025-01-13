import requests
import json
import time
import csv

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

# Main function
def main():
    genres = ["pop", "rock", "hip hop", "jazz", "classical"]
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    artist_data = []

    # Fetch artists for each genre
    for genre in genres:
        print(f"Fetching top artists for genre: {genre}")
        artists = get_top_artists_by_genre(access_token, genre, limit=10)  # Increase limit as needed
        for artist in artists:
            artist_data.append([genre, artist['name']])

    # Save to CSV file with two columns: Genre, Artist
    csv_file_name = "genre_artist_data.csv"
    with open(csv_file_name, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["Genre", "Artist"])
        # Write data
        writer.writerows(artist_data)

    print(f"Data saved to '{csv_file_name}'")

if __name__ == "__main__":
    main()
