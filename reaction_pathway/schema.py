"""Typed schema for molecule-driven reaction pathway diagrams."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


LayoutMode = Literal["auto", "linear", "network"]


@dataclass(frozen=True)
class Molecule:
    id: str
    smiles: str | None = None
    label: str | None = None
    formula: str | None = None
    role: str | None = None
    asset_path: str | None = None

    @property
    def display_label(self) -> str:
        return self.label or self.formula or self.id

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Molecule":
        if "id" not in data:
            raise ValueError("Each molecule must include an `id`.")
        if "smiles" not in data and "asset_path" not in data:
            raise ValueError(f"Molecule `{data['id']}` must include `smiles` or `asset_path`.")
        return cls(
            id=str(data["id"]),
            smiles=str(data["smiles"]) if data.get("smiles") is not None else None,
            label=data.get("label"),
            formula=data.get("formula"),
            role=data.get("role"),
            asset_path=data.get("asset_path"),
        )


@dataclass(frozen=True)
class ReactionEdge:
    sources: list[str]
    targets: list[str]
    label: str | None = None
    conditions: str | None = None
    kind: str = "main"
    side_products: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReactionEdge":
        sources = _as_list(data.get("from") or data.get("sources"))
        targets = _as_list(data.get("to") or data.get("targets"))
        if not sources or not targets:
            raise ValueError("Each reaction must include non-empty `from` and `to`.")
        return cls(
            sources=sources,
            targets=targets,
            label=data.get("label") or data.get("arrow_label"),
            conditions=data.get("conditions"),
            kind=data.get("kind", "main"),
            side_products=_as_list(data.get("side_products", [])),
        )


@dataclass(frozen=True)
class Canvas:
    width: int = 1400
    height: int = 620
    background: str = "#ffffff"
    title: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Canvas":
        data = data or {}
        return cls(
            width=int(data.get("width", 1400)),
            height=int(data.get("height", 620)),
            background=str(data.get("background", "#ffffff")),
            title=bool(data.get("title", True)),
        )


@dataclass(frozen=True)
class Style:
    molecule_width: int = 190
    molecule_height: int = 145
    side_molecule_width: int = 145
    side_molecule_height: int = 108
    font_family: str = "Times New Roman, Times, serif"
    text_color: str = "#111111"
    muted_text_color: str = "#5f6368"
    arrow_color: str = "#2c2c2c"
    side_arrow_color: str = "#8a8a8a"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Style":
        data = data or {}
        return cls(
            molecule_width=int(data.get("molecule_width", 190)),
            molecule_height=int(data.get("molecule_height", 145)),
            side_molecule_width=int(data.get("side_molecule_width", 145)),
            side_molecule_height=int(data.get("side_molecule_height", 108)),
            font_family=str(data.get("font_family", cls.font_family)),
            text_color=str(data.get("text_color", cls.text_color)),
            muted_text_color=str(data.get("muted_text_color", cls.muted_text_color)),
            arrow_color=str(data.get("arrow_color", cls.arrow_color)),
            side_arrow_color=str(data.get("side_arrow_color", cls.side_arrow_color)),
        )


@dataclass(frozen=True)
class PathwaySpec:
    title: str
    molecules: dict[str, Molecule]
    reactions: list[ReactionEdge]
    main_chain: list[str] = field(default_factory=list)
    layout: LayoutMode = "auto"
    equation: str | None = None
    canvas: Canvas = field(default_factory=Canvas)
    style: Style = field(default_factory=Style)
    note: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PathwaySpec":
        molecules = [Molecule.from_dict(item) for item in data.get("molecules", [])]
        if not molecules:
            raise ValueError("Spec must include at least one molecule.")
        mol_by_id = {mol.id: mol for mol in molecules}
        if len(mol_by_id) != len(molecules):
            raise ValueError("Molecule ids must be unique.")

        reactions = [ReactionEdge.from_dict(item) for item in data.get("reactions", [])]
        main_chain = [str(item) for item in data.get("main_chain", [])]
        if not reactions and data.get("equation"):
            reactions, inferred_chain = _infer_reactions_from_equation(
                str(data["equation"]),
                mol_by_id,
            )
            if not main_chain:
                main_chain = inferred_chain
        if not reactions and data.get("main_chain"):
            chain = [str(item) for item in data["main_chain"]]
            reactions = [
                ReactionEdge(sources=[chain[i]], targets=[chain[i + 1]])
                for i in range(len(chain) - 1)
            ]
        if not reactions:
            raise ValueError("Spec must include `reactions` or a `main_chain`.")

        spec = cls(
            title=str(data.get("title", "Reaction Pathway")),
            molecules=mol_by_id,
            reactions=reactions,
            main_chain=main_chain,
            layout=data.get("layout", "auto"),
            equation=data.get("equation"),
            canvas=Canvas.from_dict(data.get("canvas")),
            style=Style.from_dict(data.get("style")),
            note=data.get("note"),
        )
        spec.validate()
        return spec

    def validate(self) -> None:
        known = set(self.molecules)
        for node_id in self.main_chain:
            if node_id not in known:
                raise ValueError(f"`main_chain` references unknown molecule `{node_id}`.")
        for reaction in self.reactions:
            for node_id in reaction.sources + reaction.targets + reaction.side_products:
                if node_id not in known:
                    raise ValueError(f"Reaction references unknown molecule `{node_id}`.")


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    return [str(value)]


def _infer_reactions_from_equation(
    equation: str,
    molecules: dict[str, Molecule],
) -> tuple[list[ReactionEdge], list[str]]:
    normalized = (
        equation.replace("=>", "->")
        .replace("→", "->")
        .replace("⟶", "->")
        .replace("➝", "->")
    )
    stages = [_split_species(stage) for stage in normalized.split("->")]
    stages = [stage for stage in stages if stage]
    if len(stages) < 2:
        raise ValueError("Equation must contain at least one reaction arrow.")

    alias_to_id: dict[str, str] = {}
    for mol in molecules.values():
        aliases = {mol.id, mol.display_label}
        if mol.formula:
            aliases.add(mol.formula)
        for alias in aliases:
            alias_to_id[_normalize_species(alias)] = mol.id

    resolved_stages: list[list[str]] = []
    for stage in stages:
        resolved = []
        for token in stage:
            key = _normalize_species(token)
            if key not in alias_to_id:
                raise ValueError(
                    f"Equation species `{token}` does not match any molecule id, label, or formula."
                )
            resolved.append(alias_to_id[key])
        resolved_stages.append(resolved)

    main_chain = [stage[0] for stage in resolved_stages]
    reactions: list[ReactionEdge] = []
    for idx in range(len(resolved_stages) - 1):
        sources = [resolved_stages[idx][0]]
        targets = [resolved_stages[idx + 1][0]]
        side_products = resolved_stages[idx + 1][1:]
        label = f"+ {' + '.join(side_products)}" if side_products else None
        reactions.append(
            ReactionEdge(
                sources=sources,
                targets=targets,
                label=label,
                side_products=side_products,
            )
        )
    return reactions, main_chain


def species_tokens_from_equation(equation: str) -> list[str]:
    normalized = (
        equation.replace("=>", "->")
        .replace("→", "->")
        .replace("⟶", "->")
        .replace("➝", "->")
    )
    seen: set[str] = set()
    tokens: list[str] = []
    for stage in normalized.split("->"):
        for token in _split_species(stage):
            key = _normalize_species(token)
            if key not in seen:
                seen.add(key)
                tokens.append(token)
    return tokens


def normalize_species_name(value: str) -> str:
    return _normalize_species(value)


def _split_species(stage: str) -> list[str]:
    return [part.strip() for part in stage.split("+") if part.strip()]


def _normalize_species(value: str) -> str:
    translated = value.translate(str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789"))
    translated = translated.replace("·", "").replace("•", "")
    translated = translated.replace("（", "(").replace("）", ")")
    return "".join(translated.split()).lower()
