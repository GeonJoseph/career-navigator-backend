from services.chatbot.traversal import (
    cosine_text_similarity,
    build_node_text
)


def handle_clarification(
    user_input,
    state,
    nodes,
    model=None
):
    """
    Handle a clarification question between two
    career branches.
    """

    clarification = state.get(
        "pending_clarification"
    )

    if not clarification:
        return None

    A_id = clarification["branch_A"]
    B_id = clarification["branch_B"]

    phrase_A = clarification["phrase_A"]
    phrase_B = clarification["phrase_B"]

    text = user_input.lower().strip()

    # ========================================================
    # REJECT BOTH
    # ========================================================

    if any(
        phrase in text
        for phrase in [
            "neither",
            "none",
            "not these",
            "don't like both",
            "dont like both"
        ]
    ):

        state.setdefault(
            "rejected_branches",
            set()
        ).update(
            [
                A_id,
                B_id
            ]
        )

        state["pending_clarification"] = None

        state["candidate_branches"] = []

        state["pending_confirmation"] = None

        state["current_stage"] = "narrowing"

        return None

    # ========================================================
    # DIRECT OPTION A
    # ========================================================

    if phrase_A.lower() in text:

        chosen = A_id

    # ========================================================
    # DIRECT OPTION B
    # ========================================================

    elif phrase_B.lower() in text:

        chosen = B_id

    # ========================================================
    # LIGHTWEIGHT SIMILARITY FALLBACK
    # ========================================================

    else:

        A = nodes[A_id]
        B = nodes[B_id]

        A_text = build_node_text(A)
        B_text = build_node_text(B)

        sim_A = cosine_text_similarity(
            user_input,
            A_text
        )

        sim_B = cosine_text_similarity(
            user_input,
            B_text
        )

        print(
            f"[DEBUG] Clarification similarity "
            f"{A['name']}: {sim_A:.4f}"
        )

        print(
            f"[DEBUG] Clarification similarity "
            f"{B['name']}: {sim_B:.4f}"
        )

        chosen = (
            A_id
            if sim_A >= sim_B
            else B_id
        )

    # ========================================================
    # MOVE TO CONFIRMATION
    # ========================================================

    state["pending_clarification"] = None

    state["current_stage"] = "confirmation"

    state["pending_confirmation"] = chosen

    question = (
        f"{nodes[chosen]['name']} seems to match "
        "your interests. Do you want to "
        "continue with this?"
    )

    state["last_question"] = question

    return chosen