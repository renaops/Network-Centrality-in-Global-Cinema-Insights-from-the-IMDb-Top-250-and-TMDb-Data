import csv
import json
import time
import requests

TMDB_BEARER_TOKEN = ''  # Replace with your token
CSV_FILE_PATH = 'imdb_top_250_2025-05-28.csv'
OUTPUT_FILE_PATH = 'tmdb_movies.json'

HEADERS = {
    'Authorization': f'Bearer {TMDB_BEARER_TOKEN}',
    'accept': 'application/json'
}

def get_tmdb_id(imdb_id):
    url = f'https://api.themoviedb.org/3/find/{imdb_id}?external_source=imdb_id'
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    movie_results = data.get('movie_results')
    if movie_results:
        return movie_results[0].get('id')
    return None

def get_tmdb_movie_data(tmdb_id):
    url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?append_to_response=keywords,credits,recommendations&language=en-US'
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def main():
    movie_data_list = []

    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            imdb_id = row['imdbid']
            print(f'Processing IMDb ID: {imdb_id}...')
            try:
                tmdb_id = get_tmdb_id(imdb_id)
                if tmdb_id:
                    movie_data = get_tmdb_movie_data(tmdb_id)
                    movie_data_list.append(movie_data)
                    print(f'  → Found TMDb ID {tmdb_id} for {row["title"]}')
                else:
                    print(f'  → No TMDb ID found for {imdb_id}')
            except Exception as e:
                print(f'  ✖ Error processing {imdb_id}: {e}')
            time.sleep(0.25)

    # Save all movie data to file
    with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as outfile:
        json.dump(movie_data_list, outfile, ensure_ascii=False, indent=2)

    print(f'\n✅ Done. Saved {len(movie_data_list)} movies to {OUTPUT_FILE_PATH}')

if __name__ == '__main__':
    main()
