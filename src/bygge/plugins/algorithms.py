from __future__ import annotations

from collections.abc import Iterable, Sequence


# O(n(L^2))
# Don't need to use trie-based approach for the size of data we care about
def remove_redundant_prefixes[T](inputs: Iterable[Sequence[T]]) -> set[tuple[T, ...]]:
    result = set[tuple[T, ...]]()
    for input in inputs:
        redundant = False
        for i in range(1, len(input)):
            if input[:i] in inputs:
                redundant = True
                break
        if not redundant:
            result.add(tuple[T, ...](input))
    return result


def remove_redundant_prefixes_str(inputs: Iterable[str]) -> set[str]:
    return {"".join(t) for t in remove_redundant_prefixes(inputs)}
