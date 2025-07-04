import json
import os
from pathlib import Path

BLOCK_FILE = Path.home() / ".nodectl" / "manual_unavailable.json"

def load_manual_block():
    if not BLOCK_FILE.exists():
        return set()
    try:
        with open(BLOCK_FILE, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_manual_block(blocked_nodes):
    BLOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BLOCK_FILE, "w") as f:
        json.dump(sorted(list(blocked_nodes)), f, indent=2)

def add_manual_block(node):
    nodes = load_manual_block()
    nodes.add(node)
    save_manual_block(nodes)

def remove_manual_block(node):
    nodes = load_manual_block()
    nodes.discard(node)
    save_manual_block(nodes)

def clear_manual_block():
    if BLOCK_FILE.exists():
        BLOCK_FILE.unlink()
