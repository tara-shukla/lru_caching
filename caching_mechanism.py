## TODO: Implement other classes or helper functions if needed

# =========================
# Main mechanism
# =========================
import math
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
                if not nodes: 
                    return None
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

                def search(node):
                    if not node:
                        return
                    # dist = (math.dist((X,Y), (node.x, node.y)))**2
                    
                    nodes = [node]
                    
                    node_left =  search(node.left)
                    node_right = search(node.right)

                    if node_left:
                        nodes.append(node_left)
                    if node_right:
                        nodes.append(node_right)
                    
                    dists = sorted(nodes, key = lambda n: (math.dist((X,Y), (n.x, n.y))**2, n.name))
                    return dists[0]

                nearest = search(self.tree)
                return nearest.name
    
    class Cache(object):
        # tail will be mru, head will be lru
        class Node(object):
            def __init__(self, movie, t):
                self.next = None
                self.prev = None
                self.name = movie
                self.time = t
        def __init__(self,x,y, name, capacity, ttl):
            self.x = x
            self.y = y
            self.name = name
            self.movies = {}
            self.head = self.Node(None, None)
            self.tail = self.Node(None, None)

            self.head.next = self.tail
            self.tail.prev = self.head
            self.size = 0
            self.capacity = capacity

            self.ttl = ttl

        def put(self, movie, time):
            if movie in self.movies:
                self.movies[movie].time = time+self.ttl
                self.movies[movie].prev.next = self.movies[movie].next
                self.movies[movie].next.prev = self.movies[movie].prev
            else:
                self.movies[movie] = self.Node(movie, time+self.ttl)
                self.size+=1
            
            self.movies[movie].prev = self.tail.prev
            self.movies[movie].next = self.tail

            self.tail.prev.next = self.movies[movie]
            self.tail.prev = self.movies[movie]

            self.evict()

        def evict(self):
            while(self.size>self.capacity):
                lru = self.head.next
                self.movies.pop(lru.name)

                lru.next.prev = self.head
                self.head.next = lru.next
                self.size -= 1

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
            self.caches[cache[0]] = (self.Cache(x=cache[1], y = cache[2], name = cache[0], capacity=movies_per_cache, ttl = ttl))
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
        self.caches[location_name].put(movie_title, t)

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