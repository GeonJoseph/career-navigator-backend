import json
import numpy as np


def load_nodes(
    emb_path="services/chatbot/data/embeddings.json",
    meta_path="services/chatbot/data/nodes.json"
):

    # --------------------------------------------------
    # 🔥 Load embeddings
    # --------------------------------------------------
    with open(emb_path, "r", encoding="utf-8") as f:
        emb_data = json.load(f)

    # --------------------------------------------------
    # 🔥 Load metadata
    # --------------------------------------------------
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)

    # lookup: node_id → metadata
    meta_lookup = {item["node_id"]: item for item in meta_data}

    nodes = {}

    # --------------------------------------------------
    # 🔥 Build nodes
    # --------------------------------------------------
    for item in emb_data:
        node_id = item["id"]

        node_embedding = np.array(item["embedding"])

        keywords = []
        for kw in item["keywords"]:
            keywords.append({
                "text": kw["text"],
                "embedding": np.array(kw["embedding"])
            })

        meta = meta_lookup.get(node_id, {})

        nodes[node_id] = {
            "id": node_id,
            "name": item["name"],
            "embedding": node_embedding,
            "keywords": keywords,
            "parent": item.get("parent"),
            "children": [],   # will rebuild
            "level": item.get("level", 0),

            # 🔥 metadata
            "description": meta.get("description"),
            "skills": meta.get("skills", []),
            "core_tasks": meta.get("core_tasks", [])
        }

    # --------------------------------------------------
    # 🔥 Build parent → children mapping
    # --------------------------------------------------
    for node in nodes.values():
        parent = node["parent"]
        if parent is not None and parent in nodes:
            nodes[parent]["children"].append(node["id"])

    return nodes