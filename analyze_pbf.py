# /// script
# dependencies = [
#     "osmium",
# ]
# ///

import osmium
from collections import Counter

class TagAnalyzer(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.node_tags = Counter()
        self.way_tags = Counter()
        self.total_nodes_with_tags = 0
        self.total_ways_with_tags = 0

    def node(self, n):
        if len(n.tags) > 0:
            self.total_nodes_with_tags += 1
            for tag in n.tags:
                self.node_tags[tag.k] += 1

    def way(self, w):
        if len(w.tags) > 0:
            self.total_ways_with_tags += 1
            for tag in w.tags:
                self.way_tags[tag.k] += 1

if __name__ == '__main__':
    filename = 'malopolskie-261002.osm.pbf'
    print(f"Skanowanie pliku {filename} w poszukiwaniu WSZYSTKICH tagów...")
    
    handler = TagAnalyzer()
    handler.apply_file(filename)
    
    print("\n--- STATYSTYKI WĘZŁÓW (NODES) ---")
    print(f"Węzły posiadające jakiekolwiek tagi: {handler.total_nodes_with_tags}")
    print(f"Liczba unikalnych kluczy tagów: {len(handler.node_tags)}")
    print("Top 30 najpopularniejszych tagów dla węzłów:")
    for k, v in handler.node_tags.most_common(30):
        print(f"  {k}: {v}")
        
    print("\n--- STATYSTYKI DRÓG/OBSZARÓW (WAYS) ---")
    print(f"Drogi/obszary posiadające jakiekolwiek tagi: {handler.total_ways_with_tags}")
    print(f"Liczba unikalnych kluczy tagów: {len(handler.way_tags)}")
    print("Top 30 najpopularniejszych tagów dla dróg/obszarów:")
    for k, v in handler.way_tags.most_common(30):
        print(f"  {k}: {v}")
