import json


def load_nodes(
    emb_path="services/chatbot/data/embeddings.json",
    meta_path="services/chatbot/data/nodes.json"
):
    """
    Load career-tree metadata.

    The chatbot no longer requires SentenceTransformer/BGE
    embeddings for traversal. The embeddings file is therefore
    used only as the source of node IDs, names, hierarchy,
    and keywords.

    Actual career matching is performed using lightweight
    text similarity in traversal.py.
    """

    # --------------------------------------------------
    # Load node metadata
    # --------------------------------------------------

    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)

    # --------------------------------------------------
    # Load existing embedding file only for structure
    # --------------------------------------------------

    with open(emb_path, "r", encoding="utf-8") as f:
        emb_data = json.load(f)

    meta_lookup = {
        item["node_id"]: item
        for item in meta_data
    }

    nodes = {}

    # --------------------------------------------------
    # Build nodes
    # --------------------------------------------------

    for item in emb_data:

        node_id = item["id"]

        meta = meta_lookup.get(
            node_id,
            {}
        )

        # Keywords are now plain text.
        # Their old embedding vectors are not needed.
        keywords = []

        for kw in item.get("keywords", []):

            keywords.append({
                "text": kw.get("text", "")
            })

        nodes[node_id] = {
            "id": node_id,

            "name": meta.get(
                "name",
                item.get("name", "")
            ),

            "keywords": keywords,

            "parent": item.get(
                "parent"
            ),

            "children": [],

            "level": item.get(
                "level",
                meta.get("level", 0)
            ),

            "description": meta.get(
                "description",
                ""
            ),

            "skills": meta.get(
                "skills",
                []
            ),

            "core_tasks": meta.get(
                "core_tasks",
                []
            )
        }

    # --------------------------------------------------
    # Build parent → children mapping
    # --------------------------------------------------

    for node in nodes.values():

        parent = node["parent"]

        if (
            parent is not None
            and parent in nodes
        ):

            nodes[parent]["children"].append(
                node["id"]
            )

    return nodes