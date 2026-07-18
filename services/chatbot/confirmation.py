from services.chatbot.traversal import traverse, get_root


def handle_confirmation(user_input, state, nodes, model):

    text = user_input.lower()

    # --------------------------------------------------
    # 🔥 HANDLE "NEITHER"
    # --------------------------------------------------
    if any(x in text for x in ["neither", "none", "not these", "don't like both"]):

        clar = state.get("pending_clarification")

        if clar:
            rejected = [
                get_root(clar["branch_A"], nodes),
                get_root(clar["branch_B"], nodes)
            ]
        else:
            rejected = list(state.get("candidate_branches", []))

        # store globally rejected branches
        state.setdefault("rejected_branches", set()).update(rejected)

        state["candidate_branches"] = []
        state["pending_confirmation"] = None

        # 🔥 IMPORTANT: clear clarification state
        state["pending_clarification"] = None

        state["current_stage"] = "narrowing"

        print("[DEBUG CONFIRM] rejected_branches:", state.get("rejected_branches"))

        return traverse(state["initial_interest"], state, nodes, model)

    # --------------------------------------------------
    # 🔥 HANDLE YES
    # --------------------------------------------------
    elif "yes" in text:
        chosen = state["pending_confirmation"]

        state["current_branch"] = chosen
        state["pending_confirmation"] = None
        state["current_stage"] = "narrowing"
        state["tree_level"] += 1

        print("[DEBUG CONFIRM] rejected_branches:", state.get("rejected_branches"))

        return traverse(state["initial_interest"], state, nodes, model)

    # --------------------------------------------------
    # 🔥 HANDLE NO (single rejection)
    # --------------------------------------------------
    elif "no" in text:
        rejected = state["pending_confirmation"]

        if rejected in state["candidate_branches"]:
            state["candidate_branches"].remove(rejected)

        state.setdefault("rejected_branches", set()).add(rejected)

        state["pending_confirmation"] = None
        state["current_stage"] = "narrowing"

        # try next candidate if available
        if state["candidate_branches"]:
            next_branch = state["candidate_branches"][0]

            state["pending_confirmation"] = next_branch
            state["current_stage"] = "confirmation"

            question = f"Would you like to explore {nodes[next_branch]['name']} instead?"

            state["last_question"] = question
            return question

        print("[DEBUG CONFIRM] rejected_branches:", state.get("rejected_branches"))

        return traverse(state["initial_interest"], state, nodes, model)

    # --------------------------------------------------
    # 🔥 IGNORE OTHER INPUTS
    # --------------------------------------------------
    else:
        return state.get("last_question", "Please answer yes or no.")