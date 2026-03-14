## TODO: Implement other classes or helper functions if needed

# =========================
# Main mechanism
# =========================
class CachingMechanism(object):
    """A Python emulator of a caching mechanism for movies (Video cache++)."""
    class kd_tree (object):
            class Node:
                def __init__ (self, name, x, y, axis, left = None, right = None):
                    self.x = x
                    self.y = y
                    self.axis = axis
                    self.left = left
                    self.right = right
                    self.name = name
            
            def __init__ (self, cache_list:list[tuple[str, float, float]]):
                depth = len(cache_list)
                self.tree = self.build_tree(cache_list, 0)
            
            def build_tree(self, nodes, depth):
                axis = depth%2

                # +1 because we're using the full cache tuple
                sorted_nodes = sorted(nodes, key=lambda x:x[axis+1])
                root = sorted_nodes[len(sorted_nodes)//2]
                
                root_node = self.Node(
                    name = root[0],
                    x = root[1], 
                    y = root[2],
                    axis = axis,
                    left = self.build_tree(sorted_nodes[:len(sorted_nodes)//2], depth+1),
                    right = self.build_tree(sorted_nodes[len(sorted_nodes)//2 +1:], depth+1),
                )

                return root_node
            
            def get_nearest(self, X,Y):
                nearest = ('', float('inf'), float('inf'))


                
                return nearest[0]
    
    class Cache(object):
        class Node(object):
            def __init__(self, movie):
                self.next = None
                self.prev = None
                self.movie = movie
        def __init__(self,x,y,movies, name):
            self.x = x
            self.y = y
            self.name = name
            self.movies = movies
            self.head = self.Node(None)
            self.tail = self.Node(None)
            self.size = 0

            # lasdkfjalkdsf
        def put(movie, time):
            return None
        def evict():
            return None
    
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

        self.movie_list = movie_list
        self.caches = {}
        for cache in cache_list:
            self.caches[cache[0]] = (self.Cache(x=cache[1], y = cache[2], name = cache[0], movies = {}))
        self.capacity = movies_per_cache
        self.ttl = ttl

        self.cache_tree = self.kd_tree(cache_list)
        
    def find_nearest_cache(self, x: float, y: float) -> str:
        """
        Return nearest cache location name using Euclidean distance.
        Tie-break: lexicographically smallest LocationName.
        """
        ## TODO: Implement it
        return self.cache_tree.get_nearest(x,y)

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
        nearest = self.find_nearest_cache(user_x, user_y)
        nearest_movies = self.caches[nearest].movies

        if movie_title in nearest_movies and t<nearest_movies[movie_title]+self.ttl:
            self.update_cache_state(nearest,movie_title,t)
            return (True, nearest)
        else:
            self.update_cache_state(nearest,movie_title,t)
            return (False, None)