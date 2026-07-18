from services.chatbot.utils import cosine


def handle_clarification(user_input, state, nodes, model):

    clarification = state["pending_clarification"]

    A_id = clarification["branch_A"]
    B_id = clarification["branch_B"]

    phrase_A = clarification["phrase_A"]
    phrase_B = clarification["phrase_B"]

    text = user_input.lower()

    # --------------------------------------------------
    # 🔥 CASE 0: reject both options
    # --------------------------------------------------
    if any(x in text for x in ["neither", "none", "not these", "don't like both"]):
        rejected = [A_id, B_id]

        state.setdefault("rejected_branches", set()).update(rejected)

        state["pending_clarification"] = None
        state["candidate_branches"] = []
        state["pending_confirmation"] = None
        state["current_stage"] = "narrowing"

        return None

    # --------------------------------------------------
    # 🔥 CASE 1: direct phrase match
    # --------------------------------------------------
    if phrase_A in text:
        chosen = A_id

    elif phrase_B in text:
        chosen = B_id

    else:
        # --------------------------------------------------
        # 🔥 CASE 2: fallback → semantic similarity
        # --------------------------------------------------
        user_vec = model.encode(user_input, normalize_embeddings=True)

        A = nodes[A_id]
        B = nodes[B_id]

        sim_A = cosine(user_vec, A["embedding"])
        sim_B = cosine(user_vec, B["embedding"])

        chosen = A_id if sim_A > sim_B else B_id

    # --------------------------------------------------
    # 🔥 MOVE TO CONFIRMATION
    # --------------------------------------------------
    state["pending_clarification"] = None
    state["current_stage"] = "confirmation"
    state["pending_confirmation"] = chosen

    question = f"{nodes[chosen]['name']} seems to match your interests. Do you want to continue with this?"

    state["last_question"] = question

    return chosen