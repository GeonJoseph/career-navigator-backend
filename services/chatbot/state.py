def create_initial_state():
    return {
        "current_stage": "narrowing",
        "current_branch": None,
        "current_node": None,
        "candidate_branches": [],
        "pending_clarification": None,
        "pending_confirmation": None,
        "tree_level": 0,
        "clarification_count": 0,
        "confidence_score": 0.0,
        "initial_interest": None,
        "last_question": None,

        # 🔥 NEW
        "interest_edit_mode": False,
        "interest_edit_choice": None,

        # 🔥 IMPORTANT for your filtering logic
        "rejected_branches": set()
    }