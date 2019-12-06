#!/usr/bin/env python3

import networkx as nx
import sys

def calc_distance():
    pass

def main(inputfile):
    G = nx.Graph()
    print(inputfile)
    with open(inputfile) as inputf:
        for line in inputf:
            node, nextnode = line.strip().split(")")
            G.add_edge(node, nextnode)

    print(G)
    nx.write_gexf(G, "grid.gehpi")
    spl = dict(nx.all_pairs_shortest_path_length(G))
   
    distance = 0
    node1="COM"
    for node2 in spl[node1]:
        #print("Length between", node1, "and", node2, "is", spl[node1][node2])
        distance += spl[node1][node2]

    print("part 1: orbits: %s" %distance)
if __name__ == "__main__":
    main(sys.argv[1])
