from services.chatbot.utils import cosine


def traverse(user_input, state, nodes, model):

    # --------------------------------------------------
    # Step 1: embed user input
    # --------------------------------------------------
    user_vec = model.encode(user_input, normalize_embeddings=True)

    # --------------------------------------------------
    # Step 2: get candidates
    # --------------------------------------------------
    candidates = get_children(state["current_branch"], nodes)

    rejected = state.get("rejected_branches", set())

    candidates = [c for c in candidates if c["id"] not in rejected]

    print("[DEBUG] Rejected:", rejected)
    print("[DEBUG] Candidates:", [c["id"] for c in candidates])

    # --------------------------------------------------
    # Step 3: compute similarity
    # --------------------------------------------------
    scores = []
    for node in candidates:
        sim = cosine(user_vec, node["embedding"])
        scores.append((node, sim))

    # --------------------------------------------------
    # Step 4: sort
    # --------------------------------------------------
    scores.sort(key=lambda x: x[1], reverse=True)

    # --------------------------------------------------
    # EDGE CASE: only one candidate
    # --------------------------------------------------
    if len(scores) == 1:
        best_node = scores[0][0]

        state["candidate_branches"] = [best_node["id"]]
        state["current_stage"] = "confirmation"
        state["pending_confirmation"] = best_node["id"]

        question = f"{best_node['name']} seems to match your interests. Do you want to continue with this?"

        state["last_question"] = question

        return question

    # --------------------------------------------------
    # EDGE CASE: no candidates
    # --------------------------------------------------
    if len(candidates) == 0:

        # CASE 1: user rejected everything
        if state["current_branch"] is None:
            state["current_stage"] = "narrowing"
            state["rejected_branches"] = set()

            return {
                "response": "I'm not able to find a suitable path based on your selections.\nCould you tell me a bit more about your interests?"
            }

        # CASE 2: final leaf node
        final_node = nodes[state["current_branch"]]

        state["current_stage"] = "finalized"

        return {
            "response": (
                f"{final_node['name']} looks like a great match for your interests.\n"
                "Redirecting you to detailed results..."
            ),
            "final_result": {
                "id": final_node["id"],
                "name": final_node["name"],
                "description": final_node.get("description"),
                "skills": final_node.get("skills", [])
            }
        }

    # --------------------------------------------------
    # NORMAL CASE
    # --------------------------------------------------
    top1, top2 = scores[0], scores[1]

    similarity_gap = top1[1] - top2[1]

    # --------------------------------------------------
    # Step 5: ambiguity handling
    # --------------------------------------------------
    if similarity_gap < 0.05:

        A = top1[0]
        B = top2[0]

        A_diff = get_best_keyword(A, B)
        B_diff = get_best_keyword(B, A)

        state["pending_clarification"] = {
            "branch_A": A["id"],
            "branch_B": B["id"],
            "phrase_A": A_diff,
            "phrase_B": B_diff
        }

        state["candidate_branches"] = [A["id"], B["id"]]
        state["current_stage"] = "clarification"

        question = f"Would you prefer {A_diff} or {B_diff}?"

        state["last_question"] = question

        return question

    else:
        # CLEAR WINNER
        best_node = top1[0]

        state["candidate_branches"] = [best_node["id"]]
        state["confidence_score"] = similarity_gap

        state["current_stage"] = "confirmation"
        state["pending_confirmation"] = best_node["id"]

        question = f"{best_node['name']} seems to match your interests. Do you want to continue with this?"

        state["last_question"] = question

        return question


# --------------------------------------------------
# 🔥 KEYWORD DIFFERENTIATION
# --------------------------------------------------
def get_best_keyword(A, B):

    best_score = -999
    best_keyword = None

    for kw in A["keywords"]:
        kw_vec = kw["embedding"]

        sim_A = cosine(kw_vec, A["embedding"])
        sim_B = cosine(kw_vec, B["embedding"])

        score = sim_A - sim_B

        THRESHOLD = 0.05

        if score > THRESHOLD and score > best_score:
            best_score = score
            best_keyword = kw["text"]

    if best_keyword is None:
        best_keyword = A["name"]

    return best_keyword


# --------------------------------------------------
# 🔥 TREE HELPERS
# --------------------------------------------------
def get_children(parent_id, nodes):

    if parent_id is None:
        return [n for n in nodes.values() if n["parent"] is None]

    return [nodes[child_id] for child_id in nodes[parent_id]["children"]]


def get_root(node_id, nodes):

    current = node_id

    while nodes[current]["parent"] is not None:
        current = nodes[current]["parent"]

    return current