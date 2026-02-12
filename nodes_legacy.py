from pathlib import Path
from typing import Dict, Type

from .data_store import AnimeDataStore


def _legacy_class_name(anime_title: str) -> str:
    return f"AnimePromptNode_{anime_title.replace(' ', '_').replace('-', '_')}"


def _legacy_node_factory(anime_title: str, store: AnimeDataStore):
    class LegacyAnimePromptNode:
        @classmethod
        def INPUT_TYPES(cls):
            names = store.character_names_for(anime_title)
            return {"required": {"character_name": (names if names else [""],)}}

        RETURN_TYPES = ("STRING",)
        RETURN_NAMES = ("character_prompt",)
        FUNCTION = "select_prompt"
        CATEGORY = f"Anime_Character/{anime_title}"

        def select_prompt(self, character_name: str):
            return (store.prompt_for(anime_title, character_name),)

    return LegacyAnimePromptNode


def get_legacy_mappings(store: AnimeDataStore) -> Dict[str, Dict[str, Type[object]]]:
    class_map: Dict[str, Type[object]] = {}
    display_map: Dict[str, str] = {}

    for title in store.anime_titles():
        class_name = _legacy_class_name(title)
        class_map[class_name] = _legacy_node_factory(title, store)
        display_map[class_name] = f"{title} Prompt"

    return {"class_map": class_map, "display_map": display_map}
