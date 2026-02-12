#!/usr/bin/env python3
"""Migrate ComfyUI workflow JSON from legacy AnimePromptNode_* nodes to V2 nodes."""

import argparse
import json
from pathlib import Path


def legacy_to_title(node_type: str) -> str:
    raw = node_type.replace("AnimePromptNode_", "", 1)
    return raw.replace("_", " ")


def migrate(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        workflow = json.load(handle)

    nodes = workflow.get("nodes", [])
    replaced = 0

    for node in nodes:
        node_type = node.get("type", "")
        if isinstance(node_type, str) and node_type.startswith("AnimePromptNode_"):
            anime_title = legacy_to_title(node_type)
            node["type"] = "AnimeCharacterPromptSelectorV2"

            widgets = node.setdefault("widgets_values", [])
            if len(widgets) == 0:
                widgets.extend([anime_title, ""])
            elif len(widgets) == 1:
                widgets.insert(0, anime_title)
            else:
                widgets[0] = anime_title

            replaced += 1

    return {"workflow": workflow, "replaced": replaced, "total_nodes": len(nodes)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=False)
    args = parser.parse_args()

    result = migrate(args.input)
    output = args.output or args.input.with_name(args.input.stem + "_v2.json")

    with open(output, "w", encoding="utf-8") as handle:
        json.dump(result["workflow"], handle, ensure_ascii=False, indent=2)

    print(
        f"Migrated {result['replaced']} legacy anime nodes out of {result['total_nodes']} total nodes -> {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
