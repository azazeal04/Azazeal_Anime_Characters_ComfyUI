from typing import Dict, Type

from .data_store import AnimeDataStore


def _with_default(items, default_value=""):
    return items if items else [default_value]


class AnimeCharacterPromptSelectorV2:
    CATEGORY = "Anime_Character"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("character_prompt", "character_name", "anime_title")
    FUNCTION = "select_prompt"

    @classmethod
    def INPUT_TYPES(cls):
        store: AnimeDataStore = cls.DATA_STORE
        titles = _with_default(store.anime_titles())
        return {
            "required": {
                "anime_title": (titles,),
                "character_name": ("STRING", {"default": ""}),
            }
        }

    def select_prompt(self, anime_title: str, character_name: str):
        prompt = self.DATA_STORE.prompt_for(anime_title, character_name)
        return (prompt, character_name, anime_title)


class AnimeCharacterListV2:
    CATEGORY = "Anime_Character/Tools"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("character_name",)
    FUNCTION = "pick_character"

    @classmethod
    def INPUT_TYPES(cls):
        store: AnimeDataStore = cls.DATA_STORE
        titles = _with_default(store.anime_titles())
        default_title = titles[0]
        character_names = _with_default(store.character_names_for(default_title))
        return {
            "required": {
                "anime_title": (titles,),
                "character_name": (character_names,),
            }
        }

    def pick_character(self, anime_title: str, character_name: str):
        return (character_name,)


def get_v2_mappings(store: AnimeDataStore) -> Dict[str, Dict[str, Type[object]]]:
    AnimeCharacterPromptSelectorV2.DATA_STORE = store
    AnimeCharacterListV2.DATA_STORE = store

    class_map = {
        "AnimeCharacterPromptSelectorV2": AnimeCharacterPromptSelectorV2,
        "AnimeCharacterListV2": AnimeCharacterListV2,
    }
    display_map = {
        "AnimeCharacterPromptSelectorV2": "Anime Character Prompt Selector (V2)",
        "AnimeCharacterListV2": "Anime Character List (V2)",
    }

    return {"class_map": class_map, "display_map": display_map}
