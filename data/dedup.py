#!/usr/bin/env python3
"""Deduplicate OSM PBF by (type, ID).

osmium merge can produce duplicate objects at continent boundaries
when geofabrik extracts were generated at slightly different times,
causing version mismatches for the same OSM node/way/relation.
This script removes all but the first occurrence of each (type, ID) pair,
ensuring planetiler receives strictly unique, ascending IDs."""

import osmium, sys


class DedupHandler(osmium.SimpleHandler):
    def __init__(self, writer):
        super().__init__()
        self.writer = writer
        self.seen = set()
        self.removed = 0

    def _emit(self, typ, obj):
        key = (typ, obj.id)
        if key in self.seen:
            self.removed += 1
            return
        self.seen.add(key)
        if typ == 'n':
            self.writer.add_node(obj)
        elif typ == 'w':
            self.writer.add_way(obj)
        elif typ == 'r':
            self.writer.add_relation(obj)

    def node(self, n):
        self._emit('n', n)

    def way(self, w):
        self._emit('w', w)

    def relation(self, r):
        self._emit('r', r)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.pbf> <output.pbf>")
        sys.exit(1)
    writer = osmium.SimpleWriter(sys.argv[2])
    handler = DedupHandler(writer)
    handler.apply_file(sys.argv[1], locations=True)
    writer.close()
    print(f"dedup: removed {handler.removed} duplicate objects")
