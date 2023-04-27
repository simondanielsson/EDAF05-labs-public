from __future__ import annotations

import copy
import sys
from dataclasses import dataclass, field
from collections import abc
import heapq


@dataclass
class Node:
    id_: int
    neighbors: list[int] = field(default_factory=list)  # list of node identifiers, as indexed in graph list
    weights: list[int] = field(default_factory=list)  # at index i is weight of edge connecting to node at index i in `neighbors`
    cost: int | float = float('inf')  # C[v] cost of taking including this node in tree

    def __lt__(self, other):
        if isinstance(other, Node):
            return self.cost < other.cost

        return False


def main() -> int:
    graph = _load_graph()

    minimal_spanning_tree = find_minimal_spanning_tree(graph)

    print(sum(node.cost for node in minimal_spanning_tree))

    return 0


def _load_graph() -> list[Node]:
    """Load graph from stdin."""
    n_vertices, n_edges = _read_row_as_ints()

    # vertex identifier is index in this node list
    graph = [Node(id_=id_) for id_ in range(n_vertices)]

    for _ in range(n_edges):
        node_index_1, node_index_2, weight = _read_row_as_ints()
        # -1 to align indices in input with graph list index; the algorithm is independent
        # the actual value of these indices
        graph = _add_edge_between_nodes(node_index_1 - 1, node_index_2 - 1, weight, graph)

    return graph


def _read_row_as_ints() -> abc.Iterable[int]:
    return [int(nbr) for nbr in input().split(' ')]


def _add_edge_between_nodes(node_index_1, node_index_2, weight, graph) -> list[Node]:
    graph[node_index_1].neighbors.append(node_index_2)
    graph[node_index_2].neighbors.append(node_index_1)

    graph[node_index_1].weights.append(weight)
    graph[node_index_2].weights.append(weight)

    return graph


def find_minimal_spanning_tree_1(graph: list[Node]) -> list[Node]:
    """Find minimal spanning tree of this undirected weighted graph."""
    nodes_not_in_tree = copy.deepcopy(graph)

    # priority queue wrt cost (linear time operation)
    heapq.heapify(nodes_not_in_tree)  # Q-set

    # update the first fetched nodes cost to 0: it is our anchor point and is not connected elsewhere
    count = 0

    minimal_spanning_tree = [None] * len(graph)
    while not all(minimal_spanning_tree):
        nearest_node = heapq.heappop(nodes_not_in_tree)

        if not count:
            nearest_node.cost = 0
            count += 1

        minimal_spanning_tree[nearest_node.id_] = nearest_node

        for neighbor_idx in nearest_node.neighbors:

            # only update vertices that are not already in the tree
            if minimal_spanning_tree[neighbor_idx]:
                continue

            # weight_index is the "local" index of a neighbor within a node, as opposed to the global id idx in `graph`
            weight_index = nearest_node.neighbors.index(neighbor_idx)
            if nearest_node.weights[weight_index] < graph[neighbor_idx].cost:
                # update cost of the neighbor to the weight of going from here to the neighbor
                graph[neighbor_idx].cost = nearest_node.weights[weight_index]

    # the graph contains the updated values
    return graph


def find_minimal_spanning_tree(graph: list[Node]) -> list[Node]:
    """
    Find minimal spanning tree.

    ---------------------------- Pseudo-code -----------------------------------
    initialize priority queue of adjacent nodes with arbitrary source node
    initialize empty mst

    while mst does not contain all nodes
        get the closest adjacent node
        if node not in mst
          add node to mst
          for each of its neighbors
              if neighbor in mst
                  continue

              update the nodes cost if weight is less than current cost
              if updated cost
                add neighbor to adjacent nodes (again!)
    ----------------------------------------------------------------------------

    :param graph: graph to run algorithm on
    :return: minimal spanning tree
    """
    source = graph[0]
    # no cost of adding first node
    source.cost = 0
    # priority queue to keep track of the closest adjacent nodes
    # initialize with an arbitrary node
    adjacent_nodes = [source]
    heapq.heapify(adjacent_nodes)

    # index nodes by id_ for quick lookup
    minimal_spanning_tree = [None] * len(graph)

    while not all(minimal_spanning_tree):
        nearest_node = heapq.heappop(adjacent_nodes)

        # if this node is not already in mst
        if not minimal_spanning_tree[nearest_node.id_]:
            minimal_spanning_tree[nearest_node.id_] = nearest_node

            for local_index, neighbor_index in enumerate(nearest_node.neighbors):
                neighbor = graph[neighbor_index]
                if minimal_spanning_tree[neighbor.id_]:
                    continue

                if (new_cost := nearest_node.weights[local_index]) < neighbor.cost:
                    neighbor.cost = new_cost
                    heapq.heappush(adjacent_nodes, neighbor)

    return minimal_spanning_tree


if __name__ == '__main__':
    sys.exit(main())