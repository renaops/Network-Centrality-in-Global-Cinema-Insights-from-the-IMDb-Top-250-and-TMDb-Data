import json

# Load your movie data
with open("tmdb_movies.json", "r", encoding="utf-8") as f:
    movies = json.load(f)

# Use a set to avoid duplicates
recommended_ids = set()

# Extract all recommended movie IDs
for movie in movies:
    recommendations = movie.get("recommendations", {}).get("results", [])
    for rec in recommendations:
        rec_id = rec.get("id")
        if rec_id:
            recommended_ids.add(rec_id)

# Export to a text file
with open("recommended_movie_ids.txt", "w", encoding="utf-8") as out_file:
    for movie_id in sorted(recommended_ids):
        out_file.write(f"{movie_id}\n")

print(f"Exported {len(recommended_ids)} unique recommended movie IDs.")
