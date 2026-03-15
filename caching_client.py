"""
Test client for CachingMechanism (caching_mechanism.py).
Focused on: nearest-cache tie-breaking, LRU eviction tie-breaking,
and expiration/TTL boundary conditions.

Usage:
    python geo_cache_test_client.py
"""

from caching_mechanism import CachingMechanism

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

results = []

def run(label, got, expected):
    ok = got == expected
    tag = PASS if ok else FAIL
    print(f"  [{tag}] {label}")
    if not ok:
        print(f"         expected: {expected}")
        print(f"         got:      {got}")
    results.append(ok)

def section(title):
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")

def make(locations, k, ttl):
    """Construct a CachingMechanism with a movie_list derived from all titles
    used in the tests so lookup never hits an invalid-title branch."""
    movies = ["MovieA","MovieB","MovieC","Inception","Ghost","Dune",
              "Zorro","Apple","Newfilm","OldA","OldB","Fresh",
              "Keeper","Goner","NewFilm"]
    return CachingMechanism(movies, locations, k, ttl)


# ═══════════════════════════════════════════════════════════════
# SECTION 1 — NEAREST CACHE TIE-BREAKING
# ═══════════════════════════════════════════════════════════════
section("1. NEAREST CACHE TIE-BREAKING")

# Two caches equidistant from user; lexicographically smaller name wins.
#   "alpha" at (0.0, 5.0)  → dist to (0,0) = 5.0
#   "beta"  at (0.0,-5.0)  → dist to (0,0) = 5.0
#   Expected winner: "alpha"
c = make([("alpha", 0.0, 5.0), ("beta", 0.0, -5.0)], k=3, ttl=100)
run("Equidistant pair: miss returns (False, None)",
    c.lookup("MovieA", 0.0, 0.0, t=1), (False, None))
run("Equidistant pair: hit confirms insert went to 'alpha'",
    c.lookup("MovieA", 0.0, 0.0, t=2), (True, "alpha"))

# Three-way tie — all equidistant, lex order: "a" < "b" < "c"
#   "c" at (3.0, 0.0), "a" at (0.0, 3.0), "b" at (-3.0, 0.0) → all dist=3
c = make([("c", 3.0, 0.0), ("a", 0.0, 3.0), ("b", -3.0, 0.0)], k=3, ttl=100)
run("Three-way tie: miss returns (False, None)",
    c.lookup("MovieB", 0.0, 0.0, t=1), (False, None))
run("Three-way tie: hit confirms insert went to 'a'",
    c.lookup("MovieB", 0.0, 0.0, t=2), (True, "a"))

# User is exactly on top of one cache — zero-distance wins unconditionally.
#   "far" at (100.0, 0.0), "close" at (0.0, 0.0)
c = make([("far", 100.0, 0.0), ("close", 0.0, 0.0)], k=3, ttl=100)
run("Zero-distance cache: miss returns (False, None)",
    c.lookup("MovieC", 0.0, 0.0, t=1), (False, None))
run("Zero-distance cache: hit confirmed in 'close'",
    c.lookup("MovieC", 0.0, 0.0, t=2), (True, "close"))

# Tie between two caches whose names differ only in case — pure lex order.
#   "Beta" (0.0,5.0) vs "alpha" (0.0,-5.0); "B" (66) > "a" (97) in ASCII,
#   but lexicographic string comparison in Python is case-sensitive:
#   uppercase letters sort before lowercase → "Beta" < "alpha".
c = make([("alpha", 0.0, -5.0), ("Beta", 0.0, 5.0)], k=3, ttl=100)
run("Case-sensitive lex tie-break: 'Beta' < 'alpha' (uppercase sorts first)",
    c.lookup("MovieA", 0.0, 0.0, t=1), (False, None))
run("Case-sensitive lex tie-break: hit confirms insert went to 'Beta'",
    c.lookup("MovieA", 0.0, 0.0, t=2), (True, "Beta"))


# ═══════════════════════════════════════════════════════════════
# SECTION 2 — EXPIRATION & TTL BOUNDARY CONDITIONS
# ═══════════════════════════════════════════════════════════════
section("2. EXPIRATION & TTL BOUNDARY CONDITIONS")

# Spec: valid at t iff t < expiration_time (strict less-than).
# TTL=10, insert at t=1 → expiry=11.
c = make([("loc", 0.0, 0.0)], k=5, ttl=10)
c.lookup("Inception", 0.0, 0.0, t=1)   # miss → inserts, expiry=11

run("Valid at t=expiry-1  (10 < 11 → True)",
    c.lookup("Inception", 0.0, 0.0, t=10), (True, "loc"))
run("Expired at t=expiry  (11 < 11 → False, strict boundary)",
    c.lookup("Inception", 0.0, 0.0, t=11), (False, None))

# Expired item re-inserted with fresh expiry on the same miss call.
# Re-insert at t=11 → new expiry=21.
run("Re-inserted item valid before new expiry  (20 < 21 → True)",
    c.lookup("Inception", 0.0, 0.0, t=20), (True, "loc"))
run("Re-inserted item expires again at t=21  (21 < 21 → False)",
    c.lookup("Inception", 0.0, 0.0, t=21), (False, None))

# TTL=0: expiry = t + 0 = t, so item is never valid (t < t is always False).
c = make([("loc", 0.0, 0.0)], k=5, ttl=0)
c.lookup("Ghost", 0.0, 0.0, t=5)       # miss → inserts with expiry=5
run("TTL=0: item expires immediately  (5 < 5 → False)",
    c.lookup("Ghost", 0.0, 0.0, t=5), (False, None))

# t=0 edge: request at timestamp 0, TTL=1 → expiry=1.
c = make([("loc", 0.0, 0.0)], k=5, ttl=1)
c.lookup("Dune", 0.0, 0.0, t=0)        # miss → inserts with expiry=1
run("t=0 insert, hit at t=0  (0 < 1 → True)",
    c.lookup("Dune", 0.0, 0.0, t=0), (True, "loc"))
run("t=0 insert, expired at t=1  (1 < 1 → False)",
    c.lookup("Dune", 0.0, 0.0, t=1), (False, None))

# Access at t=expiry-1 does NOT extend the expiry.
# Insert at t=1, expiry=11. Hit at t=10 — expiry must remain 11.
c = make([("loc", 0.0, 0.0)], k=5, ttl=10)
c.lookup("Dune", 0.0, 0.0, t=1)        # inserts, expiry=11
c.lookup("Dune", 0.0, 0.0, t=10)       # hit — must NOT refresh expiry
run("Hit does not extend expiry: still expires at original t=11",
    c.lookup("Dune", 0.0, 0.0, t=11), (False, None))


# ═══════════════════════════════════════════════════════════════
# SECTION 3 — LRU EVICTION TIE-BREAKING
# ═══════════════════════════════════════════════════════════════
section("3. LRU EVICTION TIE-BREAKING")

# Basic LRU order: A inserted before B → A is LRU when C triggers eviction.
c = make([("loc", 0.0, 0.0)], k=2, ttl=1000)
c.lookup("MovieA", 0.0, 0.0, t=1)  # insert A
c.lookup("MovieB", 0.0, 0.0, t=2)  # insert B
c.lookup("MovieC", 0.0, 0.0, t=3)  # full → A evicted (LRU)

run("Basic LRU: oldest-inserted item (A) evicted",
    c.lookup("MovieA", 0.0, 0.0, t=4), (False, None))
# After re-inserting A at t=4: cache has B(last_used=2), C(last_used=3), A(last_used=4)
# → B is now LRU, C survives
run("Basic LRU: C (inserted t=3) survives over B (last_used=2)",
    c.lookup("MovieC", 0.0, 0.0, t=5), (True, "loc"))

# True LRU: a hit must update recency, not just track insertion order.
# Insert A then B. Hit A → A becomes MRU, B becomes LRU. Insert C → B evicted.
c = make([("loc", 0.0, 0.0)], k=2, ttl=1000)
c.lookup("MovieA", 0.0, 0.0, t=1)  # insert A
c.lookup("MovieB", 0.0, 0.0, t=2)  # insert B
c.lookup("MovieA", 0.0, 0.0, t=3)  # HIT on A → A becomes MRU, B is now LRU
c.lookup("MovieC", 0.0, 0.0, t=4)  # full → B evicted

run("True LRU: re-accessed item (A) survives eviction",
    c.lookup("MovieA", 0.0, 0.0, t=5), (True, "loc"))
run("True LRU: untouched item (B) evicted after A was re-accessed",
    c.lookup("MovieB", 0.0, 0.0, t=6), (False, None))

# update_cache_state also counts as a recency update.
# Insert A then B. Call update_cache_state on A → A becomes MRU.
# Insert C → B evicted.
c = make([("loc", 0.0, 0.0)], k=2, ttl=1000)
c.lookup("MovieA", 0.0, 0.0, t=1)          # insert A
c.lookup("MovieB", 0.0, 0.0, t=2)          # insert B
c.update_cache_state("loc", "MovieA", t=3) # refresh A → A is MRU, B is LRU
c.lookup("MovieC", 0.0, 0.0, t=4)          # full → B evicted

run("update_cache_state updates recency: A survives, B evicted",
    c.lookup("MovieB", 0.0, 0.0, t=5), (False, None))
# Looking up B (miss) re-inserts it at t=5 → cache has C(last_used=4), A(last_used=3), B(last_used=5)
# A is now LRU — checking C survives instead
run("update_cache_state updates recency: C (last touched t=4) still present",
    c.lookup("MovieC", 0.0, 0.0, t=6), (True, "loc"))

# Lex tie-break on eviction: two items share identical last-access time.
# "Apple" and "Zorro" both accessed at t=3 → lex smaller "Apple" evicted first.
c = make([("loc", 0.0, 0.0)], k=2, ttl=1000)
c.lookup("Zorro", 0.0, 0.0, t=1)           # insert Zorro
c.lookup("Apple", 0.0, 0.0, t=2)           # insert Apple
c.update_cache_state("loc", "Zorro", t=3)  # both touched at t=3
c.update_cache_state("loc", "Apple", t=3)
c.lookup("Newfilm", 0.0, 0.0, t=4)         # full → "Apple" evicted (lex smaller)

run("Lex tie-break: 'Apple' evicted (lex smaller than 'Zorro')",
    c.lookup("Apple", 0.0, 0.0, t=5), (False, None))
# Looking up Apple (miss) re-inserts it at t=5 → cache has Newfilm(last_used=4), Apple(last_used=5)
# Zorro was already evicted — checking Newfilm survives
run("Lex tie-break: 'Newfilm' (inserted t=4) still present after Apple re-insert",
    c.lookup("Newfilm", 0.0, 0.0, t=6), (True, "loc"))

# Expired items are purged before LRU eviction.
# Both items expire before the next insert → no valid item should be evicted.
c = make([("loc", 0.0, 0.0)], k=2, ttl=5)
c.lookup("OldA", 0.0, 0.0, t=1)   # expiry=6
c.lookup("OldB", 0.0, 0.0, t=1)   # expiry=6, cache full
# At t=10 both are expired. Insert Fresh → expired items purged, no LRU needed.
c.lookup("Fresh", 0.0, 0.0, t=10)

run("Expired purge before LRU: Fresh inserted without evicting valid entries",
    c.lookup("Fresh", 0.0, 0.0, t=11), (True, "loc"))
run("Expired purge before LRU: OldA no longer present",
    c.lookup("OldA", 0.0, 0.0, t=11), (False, None))

# Partial expiry: one slot freed by expiry is enough; valid item must survive.
c = make([("loc", 0.0, 0.0)], k=2, ttl=5)
c.lookup("Keeper", 0.0, 0.0, t=1)  # expiry=6, still valid at t=10
c.lookup("Goner",  0.0, 0.0, t=1)  # expiry=6, expired at t=10
c.lookup("Keeper", 0.0, 0.0, t=9)  # hit, update recency
# At t=10: Goner expired (purged), Keeper valid. Insert NewFilm fits in freed slot.
c.lookup("NewFilm", 0.0, 0.0, t=10)

run("Partial expiry: valid item 'Keeper' untouched",
    c.lookup("Keeper", 0.0, 0.0, t=10), (True, "loc"))
run("Partial expiry: newly inserted item 'NewFilm' present",
    c.lookup("NewFilm", 0.0, 0.0, t=10), (True, "loc"))


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*60}")
total  = len(results)
passed = sum(results)
failed = total - passed
print(f"  Results: {passed}/{total} passed", end="")
if failed:
    print(f"  ({failed} FAILED)")
else:
    print("  ✓ All tests passed")
print(f"{'═'*60}\n")