import json
import requests
import time
import os

TMDB_BEARER_TOKEN = ''  # Replace with your token

HEADERS = {
    "Authorization": f"Bearer {TMDB_BEARER_TOKEN}",
    "accept": "application/json"
}

def get_tmdb_movie_data(tmdb_id):
    url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?append_to_response=keywords,credits,recommendations&language=en-US'
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# Load recommended movie IDs
with open("recommended_movie_ids.txt", "r", encoding="utf-8") as f:
    recommended_ids = [line.strip() for line in f if line.strip()]

# Load existing data if file exists
output_file = "recommended_movie_data.json"
existing_data = []
fetched_ids = set()

if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as f:
        try:
            existing_data = json.load(f)
            fetched_ids = {movie["id"] for movie in existing_data if "id" in movie}
        except json.JSONDecodeError:
            print("Warning: Output file exists but is not valid JSON. Starting fresh.")

# Append data for unfetched IDs
new_data = []
for tmdb_id in recommended_ids:
    tmdb_id = int(tmdb_id)
    if tmdb_id in fetched_ids:
        continue

    try:
        data = get_tmdb_movie_data(tmdb_id)
        new_data.append(data)
        print(f"Fetched: {tmdb_id} - {data.get('title')}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {tmdb_id}: {e}")
    
    time.sleep(0.25)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(existing_data + new_data, f, ensure_ascii=False, indent=2)

print(f"Appended {len(new_data)} new entries to {output_file}")
