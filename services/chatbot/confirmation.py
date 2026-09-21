from services.chatbot.traversal import traverse


def handle_confirmation(
    user_input,
    state,
    nodes,
    model
):
    """
    Handle yes/no confirmation responses.

    Returns either:
    - a string response
    - a traversal response
    - a final-result dictionary
    """

    text = user_input.lower().strip()

    # ========================================================
    # HANDLE "NEITHER"
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

        # Reject currently presented candidates.
        candidates = list(
            state.get(
                "candidate_branches",
                []
            )
        )

        state.setdefault(
            "rejected_branches",
            set()
        ).update(candidates)

        state["candidate_branches"] = []

        state["pending_confirmation"] = None

        state["pending_clarification"] = None

        state["current_stage"] = "narrowing"

        print(
            "[DEBUG CONFIRM] rejected_branches:",
            state.get("rejected_branches")
        )

        return traverse(
            state["initial_interest"],
            state,
            nodes,
            model
        )

    # ========================================================
    # HANDLE YES
    # ========================================================

    if (
        text == "yes"
        or text.startswith("yes ")
        or text in [
            "yeah",
            "yep",
            "sure",
            "correct",
            "that's right",
            "that is right",
            "continue"
        ]
    ):

        chosen = state.get(
            "pending_confirmation"
        )

        if not chosen:
            return (
                "There is no career option "
                "waiting for confirmation."
            )

        state["current_branch"] = chosen

# Keep traversal state synchronized with the confirmed branch.
        state["current_node"] = chosen

        state["pending_confirmation"] = None

        state["current_stage"] = "narrowing"

        # Increase tree level safely.
        state["tree_level"] = (
            state.get("tree_level", 0) + 1
        )

        print(
            "[DEBUG CONFIRM] "
            "confirmed branch:",
            chosen
        )

        print(
            "[DEBUG CONFIRM] "
            "rejected_branches:",
            state.get("rejected_branches")
        )

        return traverse(
            state["initial_interest"],
            state,
            nodes,
            model
        )

    # ========================================================
    # HANDLE NO
    # ========================================================

    if (
        text == "no"
        or text.startswith("no ")
        or text in [
            "nope",
            "not really",
            "not this"
        ]
    ):

        rejected = state.get(
            "pending_confirmation"
        )

        if rejected:

            state.setdefault(
                "rejected_branches",
                set()
            ).add(rejected)

        # Remove rejected candidate.
        if (
            rejected
            and rejected in state.get(
                "candidate_branches",
                []
            )
        ):

            state[
                "candidate_branches"
            ].remove(rejected)

        state["pending_confirmation"] = None

        state["current_stage"] = "narrowing"

        # ----------------------------------------------------
        # Try another candidate that was already discovered.
        # ----------------------------------------------------

        candidates = state.get(
            "candidate_branches",
            []
        )

        if candidates:

            next_branch = candidates[0]

            state[
                "pending_confirmation"
            ] = next_branch

            state[
                "current_stage"
            ] = "confirmation"

            question = (
                f"Would you like to explore "
                f"{nodes[next_branch]['name']} "
                f"instead?"
            )

            state[
                "last_question"
            ] = question

            return question

        # ----------------------------------------------------
        # No candidate left: continue traversal.
        # ----------------------------------------------------

        print(
            "[DEBUG CONFIRM] "
            "rejected_branches:",
            state.get("rejected_branches")
        )

        return traverse(
            state["initial_interest"],
            state,
            nodes,
            model
        )

    # ========================================================
    # UNKNOWN RESPONSE
    # ========================================================

    return state.get(
        "last_question",
        "Please answer yes or no."
    )