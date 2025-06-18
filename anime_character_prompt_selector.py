import os
import json
from pathlib import Path

CHARACTER_DATA_DIR = Path(__file__).parent / "anime_data"

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}


def create_anime_class(anime_name, data_path):
    class AnimePromptNode:
        @classmethod
        def INPUT_TYPES(cls):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    characters = json.load(f)
                    character_names = [c['name'] for c in characters if 'name' in c and 'prompt' in c]
                    return {
                        "required": {
                            "character_name": (character_names, )
                        }
                    }
            except Exception as e:
                print(f"⚠️ Failed to load character file for {anime_name}: {e}")
                return {"required": {"character_name": ([], )}}

        RETURN_TYPES = ("STRING", )
        RETURN_NAMES = ("character_prompt", )
        FUNCTION = "select_prompt"
        CATEGORY = f"Anime_Character/{anime_name}"

        def __init__(self):
            self.character_prompt_map = {}
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    characters = json.load(f)
                    self.character_prompt_map = {
                        char['name']: char['prompt']
                        for char in characters if 'name' in char and 'prompt' in char
                    }
            except Exception as e:
                print(f"⚠️ Failed to initialize {anime_name} node: {e}")

        def select_prompt(self, character_name):
            return (self.character_prompt_map.get(character_name, ""), )

    return AnimePromptNode


def discover_anime_nodes():
    if not CHARACTER_DATA_DIR.exists():
        print("⚠️ anime_data directory not found.")
        return

    for root, _, files in os.walk(CHARACTER_DATA_DIR):
        for file in files:
            if file.endswith(".json") and file != "metadata.json":
                full_path = Path(root) / file
                anime_title = file.replace(".json", "").strip()
                class_name = f"AnimePromptNode_{anime_title.replace(' ', '_').replace('-', '_')}"
                node_class = create_anime_class(anime_title, full_path)
                NODE_CLASS_MAPPINGS[class_name] = node_class
                NODE_DISPLAY_NAME_MAPPINGS[class_name] = f"{anime_title} Prompt"


discover_anime_nodes()
