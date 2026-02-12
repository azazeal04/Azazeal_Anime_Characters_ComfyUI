import os
from pathlib import Path

from .data_store import build_store
from .nodes_legacy import get_legacy_mappings
from .nodes_v2 import get_v2_mappings

CHARACTER_DATA_DIR = Path(__file__).parent / "anime_data"
ENABLE_LEGACY_NODES = os.getenv("AZAZEAL_ENABLE_LEGACY_NODES", "0") == "1"

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}


store = build_store(CHARACTER_DATA_DIR)

v2 = get_v2_mappings(store)
NODE_CLASS_MAPPINGS.update(v2["class_map"])
NODE_DISPLAY_NAME_MAPPINGS.update(v2["display_map"])

if ENABLE_LEGACY_NODES:
    legacy = get_legacy_mappings(store)
    NODE_CLASS_MAPPINGS.update(legacy["class_map"])
    NODE_DISPLAY_NAME_MAPPINGS.update(legacy["display_map"])
    print(f"ℹ️ Legacy anime nodes enabled: {len(legacy['class_map'])} nodes registered.")
else:
    print("ℹ️ Legacy anime nodes disabled. Set AZAZEAL_ENABLE_LEGACY_NODES=1 for old workflow node types.")
