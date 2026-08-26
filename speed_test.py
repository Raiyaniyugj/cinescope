import requests, time

# Test JUST the movie detail (which calls get_movie_details + get_similar_movies)
t = time.time()
r = requests.get('http://127.0.0.1:5000/movie/550', timeout=15)
elapsed = (time.time() - t) * 1000
print(f'Movie/550 first: {elapsed:.0f}ms, status: {r.status_code}')

# Second call should be fully cached
t = time.time()
r = requests.get('http://127.0.0.1:5000/movie/550', timeout=15)
elapsed = (time.time() - t) * 1000
print(f'Movie/550 second: {elapsed:.0f}ms')

# Third call
t = time.time()
r = requests.get('http://127.0.0.1:5000/movie/550', timeout=15)
elapsed = (time.time() - t) * 1000
print(f'Movie/550 third: {elapsed:.0f}ms')
