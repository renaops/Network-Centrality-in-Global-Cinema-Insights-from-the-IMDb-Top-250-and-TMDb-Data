import json
import networkx as nx

# Load data
with open("data/tmdb_movies.json", "r", encoding="utf-8") as f:
    movies = json.load(f)

with open("data/recommended_movie_data.json", "r", encoding="utf-8") as f:
    recommended_data = json.load(f)

# Build lookups
recommended_lookup = {movie["id"]: movie for movie in recommended_data}
movie_dict = {movie["id"]: movie for movie in movies}

# Merge recommended movies into a unified list (if not already present)
all_movies = {**movie_dict, **recommended_lookup}

# Initialize graph
G = nx.DiGraph()

# Extract features
def get_features(movie):
    genres = {g["id"]: g["name"] for g in movie.get("genres", [])}
    cast = {c["id"] for c in movie.get("credits", {}).get("cast", [])}
    crew = {c["id"] for c in movie.get("credits", {}).get("crew", [])}
    keywords = {k["id"] for k in movie.get("keywords", {}).get("keywords", [])}
    companies = {p["id"] for p in movie.get("production_companies", [])}
    countries = {p["iso_3166_1"] for p in movie.get("production_countries", [])}
    return genres, cast, crew, keywords, companies, countries

# Add all movies as nodes
for movie_id, movie in all_movies.items():
    title = movie.get("title", "")
    release_date = movie.get("release_date", "")
    genres_dict, cast, crew, keywords, companies, countries = get_features(movie)
    genre_names = list(genres_dict.values())

    # Check if Brazilian
    is_brazilian = any(
        c.get("iso_3166_1", "").lower() == "br" or
        c.get("name", "").lower() in {"brazil", "brasil"}
        for c in movie.get("production_countries", [])
    )

    G.add_node(movie_id, title=title, label=title, brazilian=is_brazilian, release_date=release_date, genres="|".join(genre_names))

# Add edges based on similarity between any two connected movies
all_ids = list(all_movies.keys())

for i, id1 in enumerate(all_ids):
    movie1 = all_movies[id1]
    genres1, cast1, crew1, keywords1, companies1, countries1 = get_features(movie1)

    # Compare to all movies that come after it to avoid duplicate edges (if undirected)
    for id2 in movie1.get("recommendations", {}).get("results", []):
        id2 = id2["id"]
        if id2 not in all_movies:
            continue

        movie2 = all_movies[id2]
        genres2, cast2, crew2, keywords2, companies2, countries2 = get_features(movie2)

        shared_genres = len(set(genres1.keys()) & set(genres2.keys()))
        shared_cast = len(cast1 & cast2)
        shared_crew = len(crew1 & crew2)
        shared_keywords = len(keywords1 & keywords2)
        shared_companies = len(companies1 & companies2)
        shared_countries = len(countries1 & countries2)
        weight = shared_genres + shared_cast + shared_crew + shared_keywords + shared_companies + shared_countries

        if weight > 0:
            G.add_edge(id1, id2, weight=weight, label=str(weight))

# Save the graph
nx.write_gexf(G, "movies_graph_weighted_br.gexf")
print("Graph saved with edge weights, genres, and Brazilian info.")

brazilian_nodes = {n for n, data in G.nodes(data=True) if data.get("brazilian", False)}

# Step 2: Find all connected nodes (neighbors in and out)
connected_nodes = set()
for node in brazilian_nodes:
    connected_nodes.add(node)
    connected_nodes.update(G.successors(node))
    connected_nodes.update(G.predecessors(node))

# Step 3: Create a subgraph
G_sub = G.subgraph(connected_nodes).copy()

# Save the cleaned/pruned graph
nx.write_gexf(G_sub, "movies_graph_brazilian_related_only.gexf")
print(f"Pruned graph saved with {G_sub.number_of_nodes()} nodes and {G_sub.number_of_edges()} edges.")