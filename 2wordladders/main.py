import sys
import collections
from typing import Generator

from node import Node


def main() -> int:
    words, word_pairs = _parse_input()

    _populate_adjacency_lists(words)

    shortest_path_lengths = _find_shortest_path_lengths(words, word_pairs)

    _print_result(shortest_path_lengths)

    return 0


def _parse_input() -> tuple[dict[str, Node], list[tuple[str, str]]]:
    """Parse input."""
    n_words, n_word_pairs = input().split(' ')
    n_words, n_word_pairs = int(n_words), int(n_word_pairs)

    words: dict[str, Node] = {}
    for _ in range(n_words):
        word = input()
        words[word] = Node(word)

    word_pairs = []
    for _ in range(n_word_pairs):
        word_from, word_to = input().split(' ')
        # use same reference as above, so their neighbors only
        #   have to be populated once
        word_pairs.append(
            (words[word_from], words[word_to])
        )

    return words, word_pairs


def _populate_adjacency_lists(words: dict[str, Node]) -> None:
    """Populate adjacency list of the nodes."""
    # create adjacency lists for each node
    for node in words.values():
        for other_node in words.values():
            if node == other_node:  # equality is wrt word attr
                # don't add self as neighbor
                continue

            if _is_neighbor(node, other_node):
                node.neighbors.append(other_node)

    return


def _is_neighbor(word: Node, other_word: Node) -> bool:
    """Check if other word is neighbor to word (directed)"""
    other_word_chars = list(other_word.word)
    for word_char in word.word[1:]:
        if word_char not in other_word_chars:
            return False

        other_word_chars.remove(word_char)

    return True


def _find_shortest_path_lengths(
    words: dict[str, Node],
    word_pairs: list[tuple[Node, Node]]
) -> Generator[int | str, None, None]:
    """Find shortest path lengths of a collection of word pairs."""
    for from_word, to_word in word_pairs:
        final_node = bfs(from_word, to_word, words)
        path_length = _count_length(final_node, from_word)
        if path_length < 0:
            yield 'Impossible'
        else:
            yield path_length


def bfs(from_word: Node, to_word: Node, words: dict[str, Node]) -> Node | None:
    """Find the shortest path length in graph using bfs.

    Specifically, it populates the sequence of predecessors which
    the algorithm generates. If a path is found, the final node (to_word) is
    returned. If no path is found, None is returned.

    To get the shortest path length, you have to trace back thourgh the generated
    predecessors, and count how long it takes to get back to the root node.

    We could also not keep track of predecessors, and get the shortest path length
    by incrementing a length variable once every time we progress one step further in the
    search.
    """
    # reset states (always needed after first bfs as we modify the `visited` attr)
    _reset_visited(words)

    queue = collections.deque([from_word])
    from_word.visited = True

    while queue:
        next = queue.popleft()
        if next == to_word:  # equality on word attr
            return next

        for neighbor in next.neighbors:
            if not neighbor.visited:
                neighbor.visited = True
                neighbor.predecessor = next
                queue.append(neighbor)

    # only way to get here is if queue is empty (i.e.
    # all nodes are visited but none is the word we are
    # looking for)
    return None


def _reset_visited(words: dict[str, Node]) -> None:
    """Reset the visited attribute of all nodes in a graph."""
    for node in words.values():
        node.visited = False


def _count_length(final_node: Node, from_word: Node) -> int:
    """Count the length of the shortest path between a root and final node.

    The final node may be missing if no path was found.
    """
    if final_node is None:
        return -1

    if final_node == from_word:
        return 0

    pred = final_node.predecessor
    length = 1
    # progress backwards until we get to the start
    while pred != from_word:
        length += 1
        pred = pred.predecessor

    return length


def _print_result(shortest_path_lengths: Generator[int | str, None, None]) -> None:
    """Display results to stdout."""
    for shortest_path_length in shortest_path_lengths:
        print(shortest_path_length)


if __name__ == '__main__':
    sys.exit(main())
