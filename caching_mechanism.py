## TODO: Implement other classes or helper functions if needed

# =========================
# Main mechanism
# =========================
class CachingMechanism(object):
    """A Python emulator of a caching mechanism for movies (Video cache++)."""

    def __init__(self, movie_list, cache_list, movies_per_cache, ttl: int):
        """
        Parameters
        ----------
        movie_list : list[str]
            Valid movie titles.
        cache_list : list[tuple[str, float, float]]
            Each tuple is (LocationName, X, Y).
        movies_per_cache : int
            Capacity K per cache.
        ttl : int
            TTL for new inserts; expiration time is t + ttl.
        """
        ## TODO: Implement it
        

    def find_nearest_cache(self, x: float, y: float) -> str:
        """
        Return nearest cache location name using Euclidean distance.
        Tie-break: lexicographically smallest LocationName.
        """
        ## TODO: Implement it
        location_name = None
        return location_name

    def update_cache_state(self, location_name: str, movie_title: str, t: int) -> None:
        """
        Bring a movie into the specified cache at time t.
        (This is called on misses/expired, per the prompt.)
        """
        ## TODO: Implement it
        

    def lookup(self, movie_title: str, user_x: float, user_y: float, t: int) -> Tuple[bool, Optional[str]]:
        """
        Look up a movie given title and user coordinates at time t.

        If nearest cache contains a valid copy, return (True, LocationName) and update recency.
        Otherwise return (False, None) and insert/refresh in nearest cache with expiration t+TTL.
        """
        ## TODO: Implement it
        return (False, None)
