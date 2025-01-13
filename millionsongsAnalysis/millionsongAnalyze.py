# Required imports
import os
import sys
import time
import glob
import datetime
import sqlite3
import numpy as np
import hdf5_getters as GETTERS  # Ensure this module is accessible

# Paths (change these to your local setup)
msd_subset_path = './MillionSongSubset'  # Path to Million Song Dataset subset
msd_subset_data_path = os.path.join(msd_subset_path, 'data')
msd_subset_addf_path = os.path.join(msd_subset_path, 'AdditionalFiles')
msd_code_path = './MillionSongSubset'

assert os.path.isdir(msd_subset_path), 'Incorrect path to MSD subset'
assert os.path.isdir(msd_code_path), 'Incorrect path to MSD code'
sys.path.append(os.path.join(msd_code_path, 'PythonSrc'))

# Utility function to format time differences
def str_timedelta(start_time, stop_time):
    return str(datetime.timedelta(seconds=stop_time - start_time))

# Function to iterate over all files in a directory and apply a function
def apply_to_all_files(base_dir, func=lambda x: x, ext='.h5'):
    count = 0
    for root, dirs, files in os.walk(base_dir):
        files = glob.glob(os.path.join(root, '*' + ext))
        count += len(files)
        for f in files:
            func(f)
    return count

# Counting number of song files
print('Number of song files:', apply_to_all_files(msd_subset_data_path))

# Extract all artist names
all_artist_names = set()

def func_to_get_artist_name(filename):
    h5 = GETTERS.open_h5_file_read(filename)
    artist_name = GETTERS.get_artist_name(h5)
    all_artist_names.add(artist_name)
    h5.close()

start_time = time.time()
apply_to_all_files(msd_subset_data_path, func=func_to_get_artist_name)
end_time = time.time()
print('All artist names extracted in:', str_timedelta(start_time, end_time))
print('Found', len(all_artist_names), 'unique artist names')

# Get unique artist names using SQLite
conn = sqlite3.connect(os.path.join(msd_subset_addf_path, 'subset_track_metadata.db'))
query = "SELECT DISTINCT artist_name FROM songs"
start_time = time.time()
res = conn.execute(query)
all_artist_names_sqlite = res.fetchall()
end_time = time.time()
conn.close()
print('All artist names extracted (SQLite) in:', str_timedelta(start_time, end_time))

# Find the artist with the most songs
conn = sqlite3.connect(os.path.join(msd_subset_addf_path, 'subset_track_metadata.db'))
query = "SELECT artist_id, artist_name, COUNT(track_id) FROM songs GROUP BY artist_id ORDER BY COUNT(track_id) DESC LIMIT 1"
start_time = time.time()
res = conn.execute(query)
most_popular_artist = res.fetchone()
end_time = time.time()
conn.close()
print('Most popular artist found in:', str_timedelta(start_time, end_time))
print('Artist ID:', most_popular_artist[0], '| Artist Name:', most_popular_artist[1], '| Song Count:', most_popular_artist[2])