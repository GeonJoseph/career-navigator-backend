import re
import math
from collections import Counter


# ============================================================
# TEXT PROCESSING
# ============================================================

def tokenize(text):
    if not isinstance(text, str):
        text = str(text)

    return re.findall(r"[a-z0-9]+", text.lower())


def text_vector(text):
    return Counter(tokenize(text))


def cosine_text_similarity(text_a, text_b):
    vector_a = text_vector(text_a)
    vector_b = text_vector(text_b)

    if not vector_a or not vector_b:
        return 0.0

    common_words = set(vector_a) & set(vector_b)

    dot_product = sum(
        vector_a[word] * vector_b[word]
        for word in common_words
    )

    magnitude_a = math.sqrt(
        sum(value * value for value in vector_a.values())
    )

    magnitude_b = math.sqrt(
        sum(value * value for value in vector_b.values())
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


# ============================================================
# NODE TEXT
# ============================================================

def build_node_text(node):
    name = node.get("name", "")

    description = node.get("description", "")
    if isinstance(description, list):
        description = " ".join(
            str(item) for item in description
        )

    skills = node.get("skills", [])
    if isinstance(skills, list):
        skills = " ".join(
            str(item) for item in skills
        )

    core_tasks = node.get("core_tasks", [])
    if isinstance(core_tasks, list):
        core_tasks = " ".join(
            str(item) for item in core_tasks
        )

    keywords = node.get("keywords", [])

    keyword_text = []

    for keyword in keywords:
        if isinstance(keyword, dict):
            keyword_text.append(
                keyword.get("text", "")
            )
        else:
            keyword_text.append(str(keyword))

    return " ".join([
        name,
        description,
        skills,
        core_tasks,
        " ".join(keyword_text)
    ])


# ============================================================
# CAREER PHRASES
# ============================================================

CAREER_PHRASES = {

    "software": [
        "software",
        "software development",
        "software developer",
        "software engineer",
        "software engineering"
    ],

    "programming": [
        "programming",
        "programmer",
        "coding",
        "code",
        "writing code",
        "write code",
        "developing software"
    ],

    "web": [
        "website",
        "websites",
        "web development",
        "web developer",
        "frontend",
        "front end",
        "backend",
        "back end",
        "full stack",
        "fullstack"
    ],

    "computer": [
        "computer",
        "computers",
        "computer science",
        "computing"
    ],

    "technology": [
        "technology",
        "tech",
        "technical"
    ],

    "data": [
        "data",
        "data analysis",
        "data analytics",
        "analytics",
        "data science",
        "data scientist",
        "analyzing data",
        "analyze data"
    ],

    "ai": [
        "artificial intelligence",
        "ai",
        "machine learning",
        "deep learning",
        "neural network",
        "neural networks"
    ],

    "cybersecurity": [
        "cybersecurity",
        "cyber security",
        "ethical hacking",
        "penetration testing",
        "network security",
        "information security",
        "hacking"
    ],

    "cloud": [
        "cloud",
        "cloud computing",
        "aws",
        "azure",
        "google cloud",
        "devops",
        "docker",
        "kubernetes"
    ],

    "electronics": [
        "electronics",
        "electronic",
        "circuits",
        "circuit",
        "embedded systems",
        "microcontroller",
        "robotics",
        "robot"
    ],

    "construction": [
        "construction",
        "building construction",
        "civil construction",
        "carpentry",
        "plumbing",
        "electrician",
        "welding",
        "masonry"
    ],

    "trades": [
        "skilled trade",
        "skilled trades",
        "trade work",
        "technical trade",
        "technical trade work",
        "working with tools",
        "hand tools",
        "manual work",
        "hands-on work",
        "hands on work"
    ],

    "business": [
        "business",
        "management",
        "manager",
        "entrepreneur",
        "entrepreneurship",
        "startup",
        "marketing"
    ],

    "finance": [
        "finance",
        "financial",
        "accounting",
        "investment",
        "investing",
        "banking",
        "stocks",
        "economics"
    ],

    "healthcare": [
        "healthcare",
        "health care",
        "medicine",
        "medical",
        "doctor",
        "nurse",
        "nursing",
        "patient",
        "hospital"
    ],

    "science": [
        "science",
        "scientist",
        "research",
        "laboratory",
        "physics",
        "chemistry",
        "biology"
    ],

    "design": [
        "design",
        "graphic design",
        "graphics",
        "visual design",
        "ui design",
        "ux design",
        "creative",
        "drawing"
    ],

    "media": [
        "media",
        "video",
        "film",
        "photography",
        "animation",
        "content creation",
        "editing videos"
    ],

    "law": [
        "law",
        "legal",
        "lawyer",
        "advocate",
        "court",
        "justice",
        "policy"
    ],

    "education": [
        "teaching",
        "teacher",
        "education",
        "training",
        "teaching students",
        "school",
        "learning"
    ],

    "hospitality": [
        "hotel",
        "hospitality",
        "tourism",
        "travel",
        "restaurant",
        "cooking",
        "chef"
    ],

    "agriculture": [
        "agriculture",
        "farming",
        "farmer",
        "crops",
        "plants",
        "forestry",
        "natural resources"
    ],

    "sports": [
        "sports",
        "football",
        "cricket",
        "fitness",
        "athletics",
        "coaching",
        "coach",
        "trainer"
    ]
}


# ============================================================
# KEYWORD MATCHING
# ============================================================

def keyword_match_score(user_input, node):

    text = user_input.lower().strip()
    node_name = node.get("name", "").lower()

    signal_groups = {

        "software": [
            "software",
            "coding",
            "code",
            "programming",
            "programmer",
            "write code",
            "writing code",
            "develop software",
            "software development",
            "software developer"
        ],

        "web": [
            "website",
            "websites",
            "web development",
            "web developer",
            "frontend",
            "front end",
            "backend",
            "back end",
            "full stack",
            "fullstack"
        ],

        "computer": [
            "computer",
            "computer science",
            "computing"
        ],

        "technology": [
            "technology",
            "tech",
            "technical"
        ],

        "data": [
            "data",
            "data analysis",
            "data analytics",
            "data science",
            "data scientist",
            "analyze data",
            "analysing data",
            "analyzing data"
        ],

        "ai": [
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "neural network",
            "neural networks"
        ],

        "cybersecurity": [
            "cybersecurity",
            "cyber security",
            "ethical hacking",
            "penetration testing",
            "network security",
            "information security",
            "hacking"
        ],

        "cloud": [
            "cloud computing",
            "cloud",
            "aws",
            "azure",
            "google cloud",
            "devops",
            "docker",
            "kubernetes"
        ],

        "electronics": [
            "electronics",
            "electronic",
            "circuits",
            "circuit",
            "embedded systems",
            "microcontroller",
            "robotics"
        ],

        "construction": [
            "construction",
            "construct structures",
            "building structures",
            "civil construction",
            "carpentry",
            "plumbing",
            "masonry",
            "welding"
        ],

        "trades": [
            "skilled trade",
            "skilled trades",
            "trade work",
            "technical trade",
            "technical trade work",
            "working with tools",
            "hand tools",
            "manual work",
            "hands-on work",
            "hands on work"
        ],

        "business": [
            "business",
            "management",
            "manager",
            "entrepreneur",
            "entrepreneurship",
            "startup",
            "marketing"
        ],

        "finance": [
            "finance",
            "financial",
            "accounting",
            "investment",
            "investing",
            "banking",
            "stocks",
            "economics"
        ],

        "healthcare": [
            "healthcare",
            "health care",
            "medicine",
            "medical",
            "doctor",
            "nurse",
            "nursing",
            "patient",
            "hospital"
        ],

        "science": [
            "science",
            "scientist",
            "research",
            "laboratory",
            "physics",
            "chemistry",
            "biology"
        ],

        "design": [
            "graphic design",
            "graphics",
            "visual design",
            "ui design",
            "ux design",
            "drawing"
        ],

        "media": [
            "video",
            "film",
            "photography",
            "animation",
            "content creation"
        ],

        "law": [
            "law",
            "legal",
            "lawyer",
            "advocate",
            "court",
            "justice"
        ],

        "education": [
            "teaching",
            "teacher",
            "education",
            "training",
            "teaching students"
        ],

        "hospitality": [
            "hotel",
            "hospitality",
            "tourism",
            "travel",
            "restaurant",
            "chef",
            "cooking"
        ],

        "agriculture": [
            "agriculture",
            "farming",
            "farmer",
            "crops",
            "forestry"
        ],

        "sports": [
            "sports",
            "football",
            "cricket",
            "fitness",
            "athletics",
            "coach",
            "trainer"
        ]
    }

    branch_signals = {

        "engineering & technology": {
            "software",
            "web",
            "computer",
            "technology",
            "data",
            "ai",
            "cybersecurity",
            "cloud",
            "electronics"
        },

        "skilled trades & construction": {
            "construction",
            "trades"
        },

        "business & management": {
            "business"
        },

        "finance & economics": {
            "finance"
        },

        "healthcare & life sciences": {
            "healthcare"
        },

        "science & research": {
            "science"
        },

        "arts, media & design": {
            "design",
            "media"
        },

        "law & public policy": {
            "law"
        },

        "education & training": {
            "education"
        },

        "hospitality, tourism & services": {
            "hospitality"
        },

        "agriculture & natural resources": {
            "agriculture"
        },

        "sports, fitness & recreation": {
            "sports"
        }
    }

    matched_signals = set()

    for signal_name, phrases in signal_groups.items():

        for phrase in phrases:

            if phrase in text:
                matched_signals.add(signal_name)
                break

    print(
        "[DEBUG] Matched signals:",
        sorted(matched_signals)
    )

    relevant_signals = branch_signals.get(
        node_name,
        set()
    )

    matching_signals = (
        matched_signals & relevant_signals
    )

    score = 0.0

    # Strong career-specific signal
    if matching_signals:

        score += 0.65

        if len(matching_signals) >= 2:
            score += 0.20

        if len(matching_signals) >= 3:
            score += 0.10

    # Exact node name
    if node_name and node_name in text:
        score += 0.30

    # --------------------------------------------------------
    # Keyword overlap
    # --------------------------------------------------------

    user_words = set(
        tokenize(user_input)
    )

    ignored_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "with",
        "for",
        "to",
        "of",
        "in",
        "on",
        "i",
        "me",
        "my",
        "like",
        "enjoy",
        "love",
        "interested",
        "interest",
        "building"
    }

    user_words = {
        word
        for word in user_words
        if word not in ignored_words
    }

    overlap_score = 0.0

    for keyword in node.get("keywords", []):

        if isinstance(keyword, dict):
            keyword_text = keyword.get(
                "text",
                ""
            )
        else:
            keyword_text = str(keyword)

        keyword_words = set(
            tokenize(keyword_text)
        )

        keyword_words = {
            word
            for word in keyword_words
            if word not in ignored_words
        }

        overlap = user_words & keyword_words

        if overlap:
            overlap_score += (
                len(overlap) * 0.05
            )

    score += min(
        overlap_score,
        0.20
    )

    return min(score, 1.0)


# ============================================================
# CAREER RESULT
# ============================================================

def build_career_result(
    node_id,
    node,
    state
):
    """
    Build the final career result when a leaf node
    has been reached.
    """

    state["current_branch"] = node_id
    state["current_node"] = node_id

    state["candidate_branches"] = []
    state["pending_confirmation"] = None
    state["pending_clarification"] = None

    state["current_stage"] = "completed"

    description = node.get(
        "description",
        ""
    )

    skills = node.get(
        "skills",
        []
    )

    core_tasks = node.get(
        "core_tasks",
        []
    )

    return {
        "type": "career_result",
        "career": node.get(
            "name",
            ""
        ),
        "description": description,
        "skills": skills,
        "core_tasks": core_tasks
    }


# ============================================================
# TRAVERSAL
# ============================================================

def traverse(
    user_input,
    state,
    nodes,
    model=None
):

    current_node_id = state.get(
        "current_node"
    )

    rejected = state.get(
        "rejected_branches",
        set()
    )

    # --------------------------------------------------------
    # Determine candidate branches
    # --------------------------------------------------------

    if (
        current_node_id
        and current_node_id in nodes
    ):

        candidate_ids = nodes[
            current_node_id
        ].get(
            "children",
            []
        )

    else:

        candidate_ids = get_root(
            nodes
        )

    # Remove rejected branches
    candidate_ids = [
        node_id
        for node_id in candidate_ids
        if node_id not in rejected
    ]

    print(
        f"[DEBUG] Input: {user_input}"
    )

    print(
        f"[DEBUG] Rejected: {rejected}"
    )

    print(
        f"[DEBUG] Candidates: {candidate_ids}"
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Leaf node reached
    # --------------------------------------------------------

    if not candidate_ids:

        if (
            current_node_id
            and current_node_id in nodes
        ):

            node = nodes[
                current_node_id
            ]

            print(
                "[DEBUG] Leaf node reached:",
                node.get("name", "")
            )

            return build_career_result(
                current_node_id,
                node,
                state
            )

        state["candidate_branches"] = []
        state["pending_confirmation"] = None
        state["pending_clarification"] = None

        return (
            "I couldn't find a suitable career branch. "
            "Please tell me more about your interests."
        )

    # --------------------------------------------------------
    # Score candidates
    # --------------------------------------------------------

    scored_candidates = []

    for node_id in candidate_ids:

        node = nodes[node_id]

        node_text = build_node_text(
            node
        )

        text_similarity = (
            cosine_text_similarity(
                user_input,
                node_text
            )
        )

        keyword_bonus = (
            keyword_match_score(
                user_input,
                node
            )
        )

        final_score = (
            text_similarity * 0.45
            +
            keyword_bonus * 0.55
        )

        scored_candidates.append(
            (
                node_id,
                final_score,
                text_similarity,
                keyword_bonus
            )
        )

        print(
            f"[DEBUG] {node['name']}: "
            f"{final_score:.4f} "
            f"(text={text_similarity:.4f}, "
            f"keyword={keyword_bonus:.4f})"
        )

    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if not scored_candidates:

        return (
            "I couldn't find a suitable career branch. "
            "Please tell me more about your interests."
        )

    # --------------------------------------------------------
    # Sort candidates
    # --------------------------------------------------------

    scored_candidates.sort(
        key=lambda item: item[1],
        reverse=True
    )

    top_id = scored_candidates[0][0]
    top_score = scored_candidates[0][1]

    print(
        f"[DEBUG] Top: "
        f"{nodes[top_id]['name']} "
        f"{top_score:.4f}"
    )

    # --------------------------------------------------------
    # Only one candidate
    # --------------------------------------------------------

    if len(scored_candidates) == 1:

        state["candidate_branches"] = [
            top_id
        ]

        state["pending_confirmation"] = (
            top_id
        )

        state["current_stage"] = (
            "confirmation"
        )

        question = (
            f"{nodes[top_id]['name']} "
            "seems to match your interests. "
            "Do you want to continue with this?"
        )

        state["last_question"] = question

        return question

    # --------------------------------------------------------
    # Second candidate
    # --------------------------------------------------------

    second_id = scored_candidates[1][0]
    second_score = scored_candidates[1][1]

    gap = (
        top_score
        -
        second_score
    )

    print(
        f"[DEBUG] Second: "
        f"{nodes[second_id]['name']} "
        f"{second_score:.4f}"
    )

    print(
        f"[DEBUG] Gap: {gap:.4f}"
    )

    # --------------------------------------------------------
    # Ambiguous result
    # --------------------------------------------------------

    if gap < 0.08:

        state["candidate_branches"] = [
            top_id,
            second_id
        ]

        state["pending_clarification"] = {

            "branch_A": top_id,

            "branch_B": second_id,

            "phrase_A": nodes[
                top_id
            ]["name"],

            "phrase_B": nodes[
                second_id
            ]["name"]
        }

        state["current_stage"] = (
            "clarification"
        )

        question = (
            f"Would you prefer "
            f"{nodes[top_id]['name']} "
            f"or "
            f"{nodes[second_id]['name']}?"
        )

        state["last_question"] = question

        return question

    # --------------------------------------------------------
    # Clear winner
    # --------------------------------------------------------

    state["candidate_branches"] = [
        top_id
    ]

    state["pending_confirmation"] = (
        top_id
    )

    state["current_stage"] = (
        "confirmation"
    )

    question = (
        f"{nodes[top_id]['name']} "
        "seems to match your interests. "
        "Do you want to continue with this?"
    )

    state["last_question"] = question

    return question


# ============================================================
# BEST KEYWORD
# ============================================================

def get_best_keyword(A, B):

    A_keywords = A.get(
        "keywords",
        []
    )

    B_keywords = B.get(
        "keywords",
        []
    )

    best_A = ""
    best_B = ""

    best_score = -1.0

    for keyword_A in A_keywords:

        if isinstance(keyword_A, dict):
            text_A = keyword_A.get(
                "text",
                ""
            )
        else:
            text_A = str(
                keyword_A
            )

        if not text_A:
            continue

        for keyword_B in B_keywords:

            if isinstance(keyword_B, dict):
                text_B = keyword_B.get(
                    "text",
                    ""
                )
            else:
                text_B = str(
                    keyword_B
                )

            if not text_B:
                continue

            similarity = (
                cosine_text_similarity(
                    text_A,
                    text_B
                )
            )

            difference = (
                1.0 - similarity
            )

            if difference > best_score:

                best_score = difference

                best_A = text_A
                best_B = text_B

    return best_A, best_B


# ============================================================
# ROOT FUNCTIONS
# ============================================================

def get_root(nodes):

    return [
        node_id
        for node_id, node in nodes.items()
        if (
            node.get("parent") is None
            or node.get("level") == 1
        )
    ]


def get_root_node(nodes):

    roots = get_root(nodes)

    if not roots:
        return None

    return roots[0]


# ============================================================
# TREE HELPERS
# ============================================================

def get_children(
    node_id,
    nodes
):

    if node_id not in nodes:
        return []

    return nodes[node_id].get(
        "children",
        []
    )


def get_parent(
    node_id,
    nodes
):

    if node_id not in nodes:
        return None

    return nodes[node_id].get(
        "parent"
    )


def get_node(
    node_id,
    nodes
):

    return nodes.get(
        node_id
    )


def get_descendants(
    node_id,
    nodes
):

    descendants = []

    if node_id not in nodes:
        return descendants

    children = nodes[node_id].get(
        "children",
        []
    )

    for child_id in children:

        descendants.append(
            child_id
        )

        descendants.extend(
            get_descendants(
                child_id,
                nodes
            )
        )

    return descendants