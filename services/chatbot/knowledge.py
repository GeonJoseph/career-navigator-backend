def handle_description(user_input, state, nodes):

    text = user_input.lower()

    # --------------------------------------------------
    # 🔥 1️⃣ Check if user explicitly mentioned a domain
    # --------------------------------------------------
    for node_id, node in nodes.items():
        if node["name"].lower() in text:
            return node.get("description", "No description available.")

    # --------------------------------------------------
    # 🔥 2️⃣ fallback → current context
    # --------------------------------------------------
    node_id = state.get("current_branch") or state.get("pending_confirmation")

    if node_id is None:
        return "Please select a career path first."

    return nodes[node_id].get("description", "No description available.")


def handle_skills(state, nodes):

    # --------------------------------------------------
    # 🔥 1️⃣ Determine current node
    # --------------------------------------------------
    node_id = state.get("current_branch") or state.get("pending_confirmation")

    if node_id is None:
        return "Please select a career path first."

    node = nodes[node_id]

    skills = node.get("skills", [])

    # --------------------------------------------------
    # 🔥 2️⃣ Handle empty skills gracefully
    # --------------------------------------------------
    if not skills:
        return "No specific skills listed for this field."

    return "Key skills:\n- " + "\n- ".join(skills)