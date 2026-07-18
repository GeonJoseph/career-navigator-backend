from services.chatbot.clarification import handle_clarification
from services.chatbot.confirmation import handle_confirmation
from services.chatbot.traversal import traverse

from services.chatbot.intent import detect_intent
from services.chatbot.knowledge import handle_description, handle_skills
from services.chatbot.web import handle_web_query


def process_input(user_input, state, nodes, model):

    # --------------------------------------------------
    # 🔥 HANDLE INTEREST EDIT MODE FIRST (NO INTENT DETECTION)
    # --------------------------------------------------
    if state["interest_edit_mode"]:

        text = user_input.lower()

        # Step 1: choose option
        if state["interest_edit_choice"] is None:

            if text.strip() == "1" or "remove all" in text:
                state["interest_edit_choice"] = "reset"

                state["initial_interest"] = ""
                state["rejected_branches"] = set()

                return "All previous interests removed. Please enter your new interests."

            elif text.strip() == "2" or "add" in text:
                state["interest_edit_choice"] = "add"

                return "Please enter your new interests."

            else:
                return "Please choose:\n1) Remove all previously entered interests\n2) Add new interests"

        # Step 2: user enters interests
        else:

            if state["interest_edit_choice"] == "reset":
                state["initial_interest"] = user_input

            elif state["interest_edit_choice"] == "add":
                state["initial_interest"] += " " + user_input

            # reset navigation
            state["current_branch"] = None
            state["pending_confirmation"] = None
            state["pending_clarification"] = None
            state["candidate_branches"] = []
            state["current_stage"] = "narrowing"

            # exit edit mode
            state["interest_edit_mode"] = False
            state["interest_edit_choice"] = None

            result = traverse(state["initial_interest"], state, nodes, model)

            if isinstance(result, dict):
                return result

            return {"response": result}

    # --------------------------------------------------
    # ✅ store initial interest once
    # --------------------------------------------------
    if state["initial_interest"] is None or state["initial_interest"] == "start":
        state["initial_interest"] = user_input

    # --------------------------------------------------
    # 🔥 STEP 1: detect MULTIPLE intents
    # --------------------------------------------------
    intents = detect_intent(user_input)

    print(f"[DEBUG] Input: {user_input}")
    print(f"[DEBUG] Detected intents: {intents}")

    # --------------------------------------------------
    # 🔥 INTEREST EDIT REQUEST (TRIGGER)
    # --------------------------------------------------
    if "INTEREST_EDIT_REQUEST" in intents:

        state["interest_edit_mode"] = True
        state["interest_edit_choice"] = None

        question = (
            "Would you like to:\n"
            "1) Remove all previously entered interests\n"
            "2) Add new interests"
        )

        state["last_question"] = question
        return {"response": question}

    responses = []
    knowledge_responses = []
    navigation_responses = []

    # --------------------------------------------------
    # 1️⃣ HANDLE DOMAIN RESPONSE FIRST (state update)
    # --------------------------------------------------
    if "DOMAIN_RESPONSE" in intents:

        if state["current_stage"] == "clarification":
            chosen = handle_clarification(user_input, state, nodes, model)

            if chosen is None:
                result = traverse(state["initial_interest"], state, nodes, model)

                if isinstance(result, dict):
                    return result

                return {"response": result}

            question = f"{nodes[chosen]['name']} seems to match your interests. Do you want to continue with this?"
            state["last_question"] = question
            return {"response": question}

        elif state["current_stage"] == "confirmation":
            confirmation_response = handle_confirmation(user_input, state, nodes, model)

            # 🔥 ALWAYS preserve dict responses (final_result)
            if isinstance(confirmation_response, dict):
                return confirmation_response

            # 🔥 WRAP string properly
            return {"response": confirmation_response}

    # --------------------------------------------------
    # 2️⃣ HANDLE KNOWLEDGE / WEB (after state update)
    # --------------------------------------------------
    if "DESCRIPTION_QUERY" in intents:
        knowledge_responses.append(handle_description(user_input, state, nodes))

    if "SKILL_QUERY" in intents:
        knowledge_responses.append(handle_skills(state, nodes))

    if "OTHER_QUERY" in intents:
        knowledge_responses.append(handle_web_query(user_input))

    # --------------------------------------------------
    # 3️⃣ CONTINUE NAVIGATION (if DOMAIN happened)
    # --------------------------------------------------
    if "DOMAIN_RESPONSE" in intents and state["current_stage"] == "narrowing":
        next_question = traverse(state["initial_interest"], state, nodes, model)

        if isinstance(next_question, dict):
            return next_question  # must include final_result

        navigation_responses.append(next_question)

    # --------------------------------------------------
    # 4️⃣ DEFAULT BEHAVIOR (no DOMAIN intent)
    # --------------------------------------------------
    if "DOMAIN_RESPONSE" not in intents and not knowledge_responses:

        if state["current_stage"] == "confirmation":
            return handle_confirmation(user_input, state, nodes, model)

        elif state["current_stage"] == "narrowing":
            result = traverse(state["initial_interest"], state, nodes, model)

            if isinstance(result, dict):
                return result

            return {"response": result}

    # --------------------------------------------------
    # 5️⃣ FINAL RESPONSE
    # --------------------------------------------------

    # 🔥 If user asked a question → answer FIRST, then resume flow
    if knowledge_responses:
        response = "\n\n".join(knowledge_responses)

        if state.get("last_question"):
            response = response + "\n\n" + state["last_question"]

        return {"response": response}

    # 🔥 Otherwise continue navigation normally
    # 🔥 HANDLE DICT RESPONSES (final_result case)
    for res in navigation_responses:
        if isinstance(res, dict):
            return res

    # normal string flow
    final_text = "\n\n".join(navigation_responses)

    return {
        "response": final_text if final_text else "Let's continue."
    }