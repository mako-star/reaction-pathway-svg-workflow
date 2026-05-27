"""Layout algorithms for reaction pathway SVG assembly."""

from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict, deque

from .schema import PathwaySpec


@dataclass(frozen=True)
class NodeBox:
    molecule_id: str
    x: float
    y: float
    w: float
    h: float
    role: str = "main"

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


@dataclass(frozen=True)
class EdgePath:
    source: str
    target: str
    label: str | None = None
    conditions: str | None = None
    kind: str = "main"


@dataclass(frozen=True)
class LayoutResult:
    nodes: dict[str, NodeBox]
    edges: list[EdgePath]


def compute_layout(spec: PathwaySpec) -> LayoutResult:
    if spec.layout == "linear" or spec.main_chain:
        return _linear_layout(spec)
    return _network_layout(spec)


def _linear_layout(spec: PathwaySpec) -> LayoutResult:
    style = spec.style
    canvas = spec.canvas
    chain = spec.main_chain or _infer_main_chain(spec)
    if not chain:
        return _network_layout(spec)

    top = 130 if canvas.title else 80
    main_y = max(top, canvas.height * 0.46 - style.molecule_height / 2)
    n = len(chain)
    available = canvas.width - 120 - n * style.molecule_width
    gap = max(80, available / max(1, n - 1))
    x0 = 60

    nodes: dict[str, NodeBox] = {}
    for idx, mol_id in enumerate(chain):
        x = x0 + idx * (style.molecule_width + gap)
        nodes[mol_id] = NodeBox(mol_id, x, main_y, style.molecule_width, style.molecule_height)

    side_seen: set[str] = set()
    side_index_by_parent: dict[str, int] = defaultdict(int)
    for reaction in spec.reactions:
        parent = reaction.sources[0]
        if parent not in nodes:
            continue
        for side_id in reaction.side_products:
            if side_id in side_seen:
                continue
            side_seen.add(side_id)
            slot = side_index_by_parent[parent]
            side_index_by_parent[parent] += 1
            parent_box = nodes[parent]
            side_above = slot % 2 == 0
            sx = parent_box.cx - style.side_molecule_width / 2 + (slot // 2) * 24
            sy = (
                parent_box.y - style.side_molecule_height - 60
                if side_above
                else parent_box.y + parent_box.h + 74
            )
            nodes[side_id] = NodeBox(
                side_id,
                max(20, min(sx, canvas.width - style.side_molecule_width - 20)),
                max(76, min(sy, canvas.height - style.side_molecule_height - 46)),
                style.side_molecule_width,
                style.side_molecule_height,
                role="side",
            )

    edges: list[EdgePath] = []
    for reaction in spec.reactions:
        for source in reaction.sources:
            for target in reaction.targets:
                if source in nodes and target in nodes:
                    edges.append(
                        EdgePath(source, target, reaction.label, reaction.conditions, reaction.kind)
                    )
            for side_id in reaction.side_products:
                if source in nodes and side_id in nodes:
                    edges.append(EdgePath(source, side_id, None, None, "side"))

    return LayoutResult(nodes=nodes, edges=edges)


def _network_layout(spec: PathwaySpec) -> LayoutResult:
    style = spec.style
    canvas = spec.canvas
    graph: dict[str, set[str]] = defaultdict(set)
    indegree: dict[str, int] = {mol_id: 0 for mol_id in spec.molecules}

    for reaction in spec.reactions:
        targets = reaction.targets + reaction.side_products
        for source in reaction.sources:
            for target in targets:
                graph[source].add(target)
    for source, targets in graph.items():
        indegree.setdefault(source, 0)
        for target in targets:
            indegree[target] = indegree.get(target, 0) + 1

    queue = deque([mol_id for mol_id, degree in indegree.items() if degree == 0])
    level = {mol_id: 0 for mol_id in queue}
    while queue:
        current = queue.popleft()
        for target in graph.get(current, set()):
            level[target] = max(level.get(target, 0), level[current] + 1)
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)

    for mol_id in spec.molecules:
        level.setdefault(mol_id, 0)

    by_level: dict[int, list[str]] = defaultdict(list)
    for mol_id, lvl in level.items():
        by_level[lvl].append(mol_id)

    levels = sorted(by_level)
    x_gap = (canvas.width - 160 - style.molecule_width) / max(1, len(levels) - 1)
    nodes: dict[str, NodeBox] = {}
    for col, lvl in enumerate(levels):
        ids = sorted(by_level[lvl])
        total_h = len(ids) * style.molecule_height + (len(ids) - 1) * 42
        y0 = max(90, (canvas.height - total_h) / 2)
        for row, mol_id in enumerate(ids):
            x = 80 + col * x_gap
            y = y0 + row * (style.molecule_height + 42)
            role = "side" if spec.molecules[mol_id].role == "side" else "main"
            nodes[mol_id] = NodeBox(mol_id, x, y, style.molecule_width, style.molecule_height, role)

    edges = []
    for reaction in spec.reactions:
        for source in reaction.sources:
            for target in reaction.targets:
                edges.append(EdgePath(source, target, reaction.label, reaction.conditions, reaction.kind))
            for target in reaction.side_products:
                edges.append(EdgePath(source, target, None, None, "side"))
    return LayoutResult(nodes=nodes, edges=edges)


def _infer_main_chain(spec: PathwaySpec) -> list[str]:
    chain: list[str] = []
    for reaction in spec.reactions:
        if len(reaction.sources) != 1 or len(reaction.targets) != 1:
            return []
        if not chain:
            chain.append(reaction.sources[0])
        if chain[-1] == reaction.sources[0]:
            chain.append(reaction.targets[0])
        elif reaction.sources[0] not in chain:
            chain.extend([reaction.sources[0], reaction.targets[0]])
    return chain
