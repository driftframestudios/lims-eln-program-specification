"""Pure traversal of a reference-resolved provenance graph."""

from collections.abc import Mapping
from graphlib import CycleError, TopologicalSorter


def require_acyclic(parents: Mapping[str, tuple[str, ...]]) -> None:
    """Check all components in O(V + E) time/space, without Python recursion.

    The aggregate owns reference resolution before this stage. graphlib would
    otherwise admit an undeclared predecessor as an additional vertex.
    """
    try:
        TopologicalSorter(parents).prepare()
    except CycleError:
        raise ValueError("provenance assertion graph remains acyclic") from None


def reachable_sources(
    parents: Mapping[str, tuple[str, ...]],
    sources: Mapping[str, str],
    roots: tuple[str, ...],
) -> frozenset[str]:
    """Collect one scenario's sources in O(R + V + E) time, O(R + V + S) space.

    References and acyclicity are established by the aggregate. Scheduling each
    vertex once avoids retaining an ancestor closure for every assertion.
    All mutable containers belong to this invocation.
    """
    pending = list(dict.fromkeys(roots))
    scheduled = set(pending)
    observed: set[str] = set()
    while pending:
        assertion_id = pending.pop()
        source = sources.get(assertion_id)
        if source is not None:
            observed.add(source)
        for parent in parents[assertion_id]:
            if parent not in scheduled:
                scheduled.add(parent)
                pending.append(parent)
    return frozenset(observed)

