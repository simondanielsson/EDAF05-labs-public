from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True)
class Node:
    """Graph node representation of a word."""
    word: str
    predecessor: Optional[Node] = None
    visited: bool = False
    neighbors: list[Node] = field(default_factory=list)  # directed arc to neighbors

    def __eq__(self, other: Node):
        if not hasattr(other, 'word'):
            return False

        return self.word == other.word

    def __repr__(self) -> str:
        # override for debugging purposes
        neighbors = [neighbor.word for neighbor in self.neighbors]
        return f'{self.__class__.__name__}({self.word}, visited={self.visited}, neighbors={neighbors})'
