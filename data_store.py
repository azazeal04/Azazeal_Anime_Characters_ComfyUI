import json
import os
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List


class AnimeDataStore:
    """Index + lazy data loader for anime character prompt files."""

    INDEX_FILE_NAME = ".index.json"

    def __init__(self, data_dir: Path, max_cache_size: int = 64):
        self.data_dir = Path(data_dir)
        self.index_path = self.data_dir / self.INDEX_FILE_NAME
        self.max_cache_size = max(1, max_cache_size)
        self._index: Dict[str, Dict[str, object]] = {}
        self._prompt_cache: "OrderedDict[str, Dict[str, str]]" = OrderedDict()
        self._load_or_rebuild_index()

    def anime_titles(self) -> List[str]:
        return sorted(self._index.keys())

    def character_names_for(self, anime_title: str) -> List[str]:
        item = self._index.get(anime_title)
        if not item:
            return []
        names = item.get("characters", [])
        if isinstance(names, list):
            return names
        return []

    def prompt_for(self, anime_title: str, character_name: str) -> str:
        if anime_title not in self._index:
            return ""
        prompt_map = self._get_or_load_prompt_map(anime_title)
        return prompt_map.get(character_name, "")

    def _get_or_load_prompt_map(self, anime_title: str) -> Dict[str, str]:
        if anime_title in self._prompt_cache:
            self._prompt_cache.move_to_end(anime_title)
            return self._prompt_cache[anime_title]

        entry = self._index.get(anime_title)
        if not entry:
            return {}

        rel_path = entry.get("path")
        if not isinstance(rel_path, str):
            return {}

        abs_path = self.data_dir / rel_path
        prompt_map = self._load_prompt_map(abs_path)
        self._prompt_cache[anime_title] = prompt_map
        self._prompt_cache.move_to_end(anime_title)

        if len(self._prompt_cache) > self.max_cache_size:
            self._prompt_cache.popitem(last=False)

        return prompt_map

    def _load_prompt_map(self, data_path: Path) -> Dict[str, str]:
        try:
            with open(data_path, "r", encoding="utf-8") as handle:
                characters = json.load(handle)
        except Exception as exc:
            print(f"⚠️ Failed to load prompts from {data_path}: {exc}")
            return {}

        prompt_map: Dict[str, str] = {}
        for item in characters:
            if isinstance(item, dict) and "name" in item and "prompt" in item:
                prompt_map[str(item["name"])] = str(item["prompt"])
        return prompt_map

    def _load_or_rebuild_index(self) -> None:
        disk_index = self._read_index_file()
        discovered = self._discover_json_files()

        new_index: Dict[str, Dict[str, object]] = {}
        changed = False

        for anime_title, abs_path in discovered.items():
            rel_path = str(abs_path.relative_to(self.data_dir))
            mtime = abs_path.stat().st_mtime

            cached = disk_index.get(anime_title)
            if (
                cached
                and cached.get("path") == rel_path
                and isinstance(cached.get("mtime"), (int, float))
                and float(cached["mtime"]) == float(mtime)
                and isinstance(cached.get("characters"), list)
            ):
                new_index[anime_title] = cached
                continue

            chars = self._extract_character_names(abs_path)
            new_index[anime_title] = {
                "path": rel_path,
                "mtime": mtime,
                "characters": chars,
            }
            changed = True

        if set(disk_index.keys()) != set(discovered.keys()):
            changed = True

        self._index = new_index

        if changed or not self.index_path.exists():
            self._write_index_file(new_index)

    def _discover_json_files(self) -> Dict[str, Path]:
        discovered: Dict[str, Path] = {}
        if not self.data_dir.exists():
            return discovered

        for root, _, files in os.walk(self.data_dir):
            for name in files:
                if not name.endswith(".json"):
                    continue
                if name == "metadata.json" or name == self.INDEX_FILE_NAME:
                    continue
                abs_path = Path(root) / name
                anime_title = name[:-5].strip()
                discovered[anime_title] = abs_path

        return discovered

    def _extract_character_names(self, data_path: Path) -> List[str]:
        try:
            with open(data_path, "r", encoding="utf-8") as handle:
                characters = json.load(handle)
        except Exception as exc:
            print(f"⚠️ Failed to build index for {data_path.name}: {exc}")
            return []

        names: List[str] = []
        for item in characters:
            if isinstance(item, dict) and "name" in item and "prompt" in item:
                names.append(str(item["name"]))
        return names

    def _read_index_file(self) -> Dict[str, Dict[str, object]]:
        if not self.index_path.exists():
            return {}
        try:
            with open(self.index_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:
            print(f"⚠️ Failed to read anime index file: {exc}")
            return {}

        if isinstance(payload, dict):
            return payload
        return {}

    def _write_index_file(self, payload: Dict[str, Dict[str, object]]) -> None:
        try:
            with open(self.index_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
        except Exception as exc:
            print(f"⚠️ Failed to write anime index file: {exc}")


def build_store(data_dir: Path) -> AnimeDataStore:
    return AnimeDataStore(data_dir=data_dir)
