# =========================
# Main mechanism
# =========================
import math
import heapq
from typing import Optional


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
            
            def get_nearest(self, x,y):
                best_node = [None, float('inf')]

                def search(node):
                    # let best_node be [best distance, best node]
                    if not node:
                        return
                    dist = (math.dist((x,y), (node.x, node.y)))**2
                    
                    if dist<best_node[1] or (dist==best_node[1] and node.name<best_node[0].name):
                        best_node[0] = node
                        best_node[1] = dist

                    val = x if node.axis == 0 else y
                    node_val = node.x if node.axis ==0 else node.y


                    near, far = (node.left, node.right) if val < node_val else (node.right, node.left)

                    search(near)

                    if (val - node_val) ** 2 < best_node[1]:
                        search(far)

                search(self.tree)
                return best_node[0]
    
    class Cache(object):
        # tail will be mru, head will be lru
        class Node(object):
            def __init__(self, movie, expiry, last_used):
                self.next = None
                self.prev = None
                self.name = movie
                self.time = expiry        
                self.last_used = last_used
        
        def __init__(self,x,y, name, capacity, ttl):
            self.x = x
            self.y = y
            self.name = name
            self.movies = {}
            self.head = self.Node(None, None, None)
            self.tail = self.Node(None, None, None)

            self.head.next = self.tail
            self.tail.prev = self.head
            self.size = 0
            self.capacity = capacity
            
            self.expiry_heap = []
            self.lru_heap = []
            self.ttl = ttl
        
        def put(self, movie, time):
            expiry = time + self.ttl
            if movie in self.movies:
                node = self.movies[movie]
                node.prev.next = node.next
                node.next.prev = node.prev
                node.time = expiry
                node.last_used = time
            else:
                self.movies[movie] = self.Node(movie, expiry, time)
                self.size += 1

            heapq.heappush(self.expiry_heap, (expiry, movie))
            heapq.heappush(self.lru_heap, (time, movie))

            self.evict(time)

            # check edge case of immediate expiration?
            if movie in self.movies: 
                node = self.movies[movie]
                node.prev = self.tail.prev
                node.next = self.tail
                self.tail.prev.next = node
                self.tail.prev = node

        def evict_expired(self, time):
            while self.expiry_heap:
                expiry, name = self.expiry_heap[0]
                # skip stale entries
                if name not in self.movies or self.movies[name].time != expiry:
                    heapq.heappop(self.expiry_heap)
                    continue
                if expiry <= time:
                    heapq.heappop(self.expiry_heap)
                    node = self.movies.pop(name)
                    if node.prev is not None:
                        node.prev.next = node.next
                        node.next.prev = node.prev
                    self.size -= 1
                else:
                    break

        def evict(self, time):
            self.evict_expired(time)
            while self.size > self.capacity:
                while self.lru_heap:
                    last_used, name = self.lru_heap[0]
                    if name not in self.movies or self.movies[name].last_used != last_used:
                        heapq.heappop(self.lru_heap)
                        continue
                    break
                _, name = heapq.heappop(self.lru_heap)
                node = self.movies.pop(name)
                if node.prev is not None:
                    node.prev.next = node.next
                    node.next.prev = node.prev
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
        return self.cache_tree.get_nearest(x,y).name

    def update_cache_state(self, location_name: str, movie_title: str, t: int) -> None:
        """
        Bring a movie into the specified cache at time t.
        (This is called on misses/expired, per the prompt.)
        """
        ## TODO: Implement it
        self.caches[location_name].put(movie_title, t)

    def lookup(self, movie_title: str, user_x: float, user_y: float, t: int) -> tuple[bool, Optional[str]]:
        """
        Look up a movie given title and user coordinates at time t.

        If nearest cache contains a valid copy, return (True, LocationName) and update recency.
        Otherwise return (False, None) and insert/refresh in nearest cache with expiration t+TTL.
        """
        ## TODO: Implement it
        nearest = self.find_nearest_cache(user_x, user_y)
        if movie_title not in self.movie_list:
            return(False, None)

        nearest_movies = self.caches[nearest].movies

        # if movie_title in nearest_movies and t<nearest_movies[movie_title].time:
        #     self.update_cache_state(nearest,movie_title,t)
        #     return (True, nearest)
        # else:
        #     self.update_cache_state(nearest,movie_title,t)
        #     return (False, None)

        if movie_title in nearest_movies and t < nearest_movies[movie_title].time:
            self.caches[nearest].put(movie_title, t)
            return (True, nearest)
        else:
            self.update_cache_state(nearest, movie_title, t)
            return (False, None)