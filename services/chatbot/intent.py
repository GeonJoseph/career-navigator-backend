from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# --------------------------------------------------
# 🔥 MAIN ENTRY FUNCTION
# --------------------------------------------------
def detect_intent(user_input):

    try:
        intents = detect_intent_llm(user_input)

    except Exception as e:
        print("⚠️ Groq failed → using rule fallback:", e)
        intents = detect_intent_rules(user_input)

    # 🔥 CRITICAL: ALWAYS APPLY OVERRIDE
    intents = apply_interest_edit_override(user_input, intents)

    return intents


# --------------------------------------------------
# 🔥 LLM (KEEP YOUR ORIGINAL PROMPT)
# --------------------------------------------------
def detect_intent_llm(user_input):

    prompt = f"""
You are an intent classifier for a career guidance chatbot.

Classify the user message into one or more of these labels:

DOMAIN_RESPONSE
DESCRIPTION_QUERY
SKILL_QUERY
OTHER_QUERY

A message can contain more than one intents.

Strict rules:

1. If the user is answering a question or choosing between options → DOMAIN_RESPONSE  
   Examples:
   - "yes"
   - "I prefer backend"
   - "building software applications"

2. If the user is asking what a field or branch mean → DESCRIPTION_QUERY  
   Examples:
   - "What is machine learning?"
   - "Explain backend development"

3. If the user asks about skills required → SKILL_QUERY  
   Examples:
   - "What skills are needed?"
   - "What do I need to learn?"

4. If the user asks about salary, companies, demand, or real-world data or anything which is not included in the other three intents → OTHER_QUERY  
   Examples:
   - "How much does it pay?"
   - "Best companies for this?"
   - "What is the scope for this job in India?"

Important:
- If the message contains a QUESTION, it is NOT DOMAIN_RESPONSE
- Questions must be classified as DESCRIPTION_QUERY, SKILL_QUERY or OTHER_QUERY

Return:
- ONLY the labels
- If multiple, separate by comma
- NO explanation
- NO extra text

Examples:

Input: I like coding
Output: DOMAIN_RESPONSE

Input: What is machine learning?
Output: DESCRIPTION_QUERY

Input: What does training decision making agents involve?
Output: OTHER_QUERY

Input: Yes. What skills do I need?
Output: DOMAIN_RESPONSE, SKILL_QUERY

Input: How much does it pay?
Output: OTHER_QUERY

---

Input: {user_input}
Output:
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    result = response.choices[0].message.content.strip()

    return parse_intents(result)


# --------------------------------------------------
# 🔥 RULE FALLBACK
# --------------------------------------------------
def detect_intent_rules(user_input):

    text = user_input.lower()
    intents = []

    if any(x in text for x in ["what is", "define", "explain"]):
        intents.append("DESCRIPTION_QUERY")

    if any(x in text for x in ["skills", "requirements"]):
        intents.append("SKILL_QUERY")

    if any(x in text for x in ["salary", "pay", "earn"]):
        intents.append("OTHER_QUERY")

    if any(x in text for x in [
        "change my interests",
        "edit my interests",
        "modify my interests",
        "add interests",
        "remove interests"
    ]):
        intents.append("INTEREST_EDIT_REQUEST")

    if not intents:
        intents.append("DOMAIN_RESPONSE")

    return intents


# --------------------------------------------------
# 🔥 PARSER
# --------------------------------------------------
def parse_intents(response):

    response = response.upper()
    parts = [p.strip() for p in response.split(",")]

    intents = []

    for p in parts:
        if "DOMAIN" in p:
            intents.append("DOMAIN_RESPONSE")
        elif "DESCRIPTION" in p:
            intents.append("DESCRIPTION_QUERY")
        elif "SKILL" in p:
            intents.append("SKILL_QUERY")
        elif "OTHER" in p:
            intents.append("OTHER_QUERY")

    if not intents:
        intents = ["DOMAIN_RESPONSE"]

    return intents


# --------------------------------------------------
# 🔥 OVERRIDE (KEEP THIS)
# --------------------------------------------------
def apply_interest_edit_override(user_input, intents):

    text = user_input.lower()

    if (
        ("interest" in text or "interests" in text)
        and any(word in text for word in ["change", "modify", "edit", "update", "add", "remove"])
    ):
        if "INTEREST_EDIT_REQUEST" not in intents:
            intents.append("INTEREST_EDIT_REQUEST")

        if "DOMAIN_RESPONSE" in intents:
            intents.remove("DOMAIN_RESPONSE")

    return intents