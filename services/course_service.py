import re

# ────────────────────────────────────────────────────────────────
# Curated list of REAL courses with real URLs
# ────────────────────────────────────────────────────────────────
COURSES = [
    # ── Data & Analytics ──
    {
        "title": "Google Data Analytics Professional Certificate",
        "provider": "Coursera",
        "url": "https://www.coursera.org/professional-certificates/google-data-analytics",
        "category": "Data Analytics",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["data", "analytics", "data analyst", "google", "spreadsheets", "sql", "tableau", "statistics"]
    },
    {
        "title": "Data Analysis with Python",
        "provider": "freeCodeCamp",
        "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/",
        "category": "Data Analytics",
        "level": "Intermediate",
        "is_free": True,
        "keywords": ["data", "python", "analysis", "pandas", "numpy", "matplotlib"]
    },
    {
        "title": "The Complete SQL Bootcamp",
        "provider": "Udemy",
        "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/",
        "category": "Data Analytics",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["sql", "database", "data", "queries", "postgresql"]
    },
    {
        "title": "Statistics and Probability",
        "provider": "Khan Academy",
        "url": "https://www.khanacademy.org/math/statistics-probability",
        "category": "Data Analytics",
        "level": "Beginner",
        "is_free": True,
        "keywords": ["statistics", "probability", "math", "data", "analytics"]
    },

    # ── Programming & Software Development ──
    {
        "title": "CS50: Introduction to Computer Science",
        "provider": "Harvard (edX)",
        "url": "https://www.edx.org/learn/computer-science/harvard-university-cs50-s-introduction-to-computer-science",
        "category": "Computer Science",
        "level": "Beginner",
        "is_free": True,
        "keywords": ["computer science", "programming", "software", "c", "python", "web", "developer"]
    },
    {
        "title": "100 Days of Code: The Complete Python Pro Bootcamp",
        "provider": "Udemy",
        "url": "https://www.udemy.com/course/100-days-of-code/",
        "category": "Programming",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["python", "programming", "coding", "software", "developer", "backend"]
    },
    {
        "title": "The Odin Project - Full Stack JavaScript",
        "provider": "The Odin Project",
        "url": "https://www.theodinproject.com/paths/full-stack-javascript",
        "category": "Web Development",
        "level": "Beginner",
        "is_free": True,
        "keywords": ["javascript", "fullstack", "full stack", "web", "frontend", "backend", "developer", "node"]
    },
    {
        "title": "Java Programming and Software Engineering Fundamentals",
        "provider": "Coursera (Duke University)",
        "url": "https://www.coursera.org/specializations/java-programming",
        "category": "Programming",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["java", "programming", "software", "engineering", "developer", "backend"]
    },

    # ── Web Development ──
    {
        "title": "The Complete Web Developer Bootcamp",
        "provider": "Udemy",
        "url": "https://www.udemy.com/course/the-complete-web-development-bootcamp/",
        "category": "Web Development",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["web", "html", "css", "javascript", "react", "node", "frontend", "developer"]
    },
    {
        "title": "Responsive Web Design Certification",
        "provider": "freeCodeCamp",
        "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
        "category": "Web Development",
        "level": "Beginner",
        "is_free": True,
        "keywords": ["web", "html", "css", "responsive", "design", "frontend"]
    },
    {
        "title": "React - The Complete Guide",
        "provider": "Udemy",
        "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/",
        "category": "Web Development",
        "level": "Intermediate",
        "is_free": False,
        "keywords": ["react", "javascript", "frontend", "web", "redux", "developer", "ui"]
    },

    # ── AI & Machine Learning ──
    {
        "title": "Machine Learning by Andrew Ng",
        "provider": "Coursera (Stanford)",
        "url": "https://www.coursera.org/learn/machine-learning",
        "category": "Machine Learning",
        "level": "Intermediate",
        "is_free": False,
        "keywords": ["machine learning", "ai", "artificial intelligence", "ml", "data science", "algorithms"]
    },
    {
        "title": "Deep Learning Specialization",
        "provider": "Coursera (deeplearning.ai)",
        "url": "https://www.coursera.org/specializations/deep-learning",
        "category": "AI / Deep Learning",
        "level": "Advanced",
        "is_free": False,
        "keywords": ["deep learning", "ai", "neural network", "tensorflow", "machine learning"]
    },
    {
        "title": "Fast.ai — Practical Deep Learning for Coders",
        "provider": "fast.ai",
        "url": "https://course.fast.ai/",
        "category": "AI / Deep Learning",
        "level": "Intermediate",
        "is_free": True,
        "keywords": ["deep learning", "ai", "python", "machine learning", "neural network", "coder"]
    },
    {
        "title": "AI For Everyone",
        "provider": "Coursera (deeplearning.ai)",
        "url": "https://www.coursera.org/learn/ai-for-everyone",
        "category": "Artificial Intelligence",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["ai", "artificial intelligence", "machine learning", "business", "non-technical"]
    },

    # ── UI/UX Design ──
    {
        "title": "Google UX Design Professional Certificate",
        "provider": "Coursera",
        "url": "https://www.coursera.org/professional-certificates/google-ux-design",
        "category": "UX Design",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["ux", "ui", "design", "user experience", "user interface", "figma", "wireframe"]
    },
    {
        "title": "The Complete App Design Course — UX, UI and Design Thinking",
        "provider": "Udemy",
        "url": "https://www.udemy.com/course/the-complete-app-design-course-ux-and-ui-design/",
        "category": "UX Design",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["ux", "ui", "design", "app", "user experience", "wireframe", "prototype"]
    },

    # ── Graphic Design & Creative ──
    {
        "title": "Graphic Design Specialization",
        "provider": "Coursera (CalArts)",
        "url": "https://www.coursera.org/specializations/graphic-design",
        "category": "Graphic Design",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["graphic", "design", "visual", "typography", "creative", "adobe", "illustrator"]
    },
    {
        "title": "Canva Design School",
        "provider": "Canva",
        "url": "https://www.canva.com/designschool/",
        "category": "Graphic Design",
        "level": "Beginner",
        "is_free": True,
        "keywords": ["graphic", "design", "canva", "visual", "content", "creative", "social media"]
    },

    # ── Digital Marketing ──
    {
        "title": "Google Digital Marketing & E-commerce Certificate",
        "provider": "Coursera",
        "url": "https://www.coursera.org/professional-certificates/google-digital-marketing-ecommerce",
        "category": "Digital Marketing",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["marketing", "digital", "seo", "social media", "ecommerce", "ads", "google"]
    },
    {
        "title": "HubSpot Digital Marketing Course",
        "provider": "HubSpot Academy",
        "url": "https://academy.hubspot.com/courses/digital-marketing",
        "category": "Digital Marketing",
        "level": "Beginner",
        "is_free": True,
        "keywords": ["marketing", "digital", "content", "social media", "seo", "inbound"]
    },

    # ── Business & Finance ──
    {
        "title": "Financial Markets by Robert Shiller",
        "provider": "Coursera (Yale)",
        "url": "https://www.coursera.org/learn/financial-markets-global",
        "category": "Finance",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["finance", "financial", "markets", "investment", "banking", "economics", "accounting"]
    },
    {
        "id": "c2",
        "title": "Data Science and Machine Learning",
        "provider": "Coursera",
        "url": "https://www.coursera.org/specializations/data-science",
        "rating": 4.8,
        "duration": "6 months",
        "category": "Data Science",
        "is_free": False,
        "keywords": ["data", "science", "machine", "learning", "ai", "python", "analyst", "analytics"]
    },
    {
        "title": "Business Foundations Specialization",
        "provider": "Coursera (Wharton)",
        "url": "https://www.coursera.org/specializations/wharton-business-foundations",
        "category": "Business",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["business", "management", "operations", "accounting", "marketing", "analyst"]
    },
    {
        "title": "Excel Skills for Business Specialization",
        "provider": "Coursera (Macquarie University)",
        "url": "https://www.coursera.org/specializations/excel",
        "category": "Business Tools",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["excel", "spreadsheet", "business", "data", "analyst", "accounting", "chartered"]
    },

    # ── Cybersecurity ──
    {
        "title": "Google Cybersecurity Professional Certificate",
        "provider": "Coursera",
        "url": "https://www.coursera.org/professional-certificates/google-cybersecurity",
        "category": "Cybersecurity",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["cybersecurity", "security", "network", "hacking", "firewall", "linux"]
    },

    # ── Cloud & DevOps ──
    {
        "title": "AWS Cloud Practitioner Essentials",
        "provider": "AWS (Coursera)",
        "url": "https://www.coursera.org/learn/aws-cloud-practitioner-essentials",
        "category": "Cloud Computing",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["aws", "cloud", "devops", "server", "infrastructure", "deployment"]
    },
    {
        "title": "Google Cloud Fundamentals: Core Infrastructure",
        "provider": "Coursera (Google)",
        "url": "https://www.coursera.org/learn/gcp-fundamentals",
        "category": "Cloud Computing",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["google cloud", "cloud", "infrastructure", "devops", "gcp"]
    },

    # ── Mobile Development ──
    {
        "title": "The Complete Flutter Development Bootcamp with Dart",
        "provider": "Udemy",
        "url": "https://www.udemy.com/course/flutter-bootcamp-with-dart/",
        "category": "Mobile Development",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["mobile", "flutter", "dart", "app", "android", "ios", "developer"]
    },
    {
        "title": "Android Basics with Compose",
        "provider": "Google (Android Developers)",
        "url": "https://developer.android.com/courses/android-basics-compose/course",
        "category": "Mobile Development",
        "level": "Beginner",
        "is_free": True,
        "keywords": ["android", "mobile", "kotlin", "app", "developer", "compose"]
    },

    # ── Blockchain ──
    {
        "title": "Blockchain Specialization",
        "provider": "Coursera (University at Buffalo)",
        "url": "https://www.coursera.org/specializations/blockchain",
        "category": "Blockchain",
        "level": "Intermediate",
        "is_free": False,
        "keywords": ["blockchain", "cryptocurrency", "ethereum", "smart contract", "solidity", "web3"]
    },

    # ── Photography & Film ──
    {
        "title": "Photography Basics and Beyond",
        "provider": "Coursera (Michigan State)",
        "url": "https://www.coursera.org/specializations/photography-basics",
        "category": "Photography",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["photography", "camera", "photo", "image", "creative", "visual"]
    },
    {
        "title": "Film Production — Creating the Short Film",
        "provider": "Coursera (Michigan State)",
        "url": "https://www.coursera.org/specializations/filmmaking",
        "category": "Film",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["film", "director", "production", "cinema", "storytelling", "video"]
    },

    # ── Fashion & Interior ──
    {
        "title": "Fashion Design: Start to Finish",
        "provider": "Udemy",
        "url": "https://www.udemy.com/course/fashion-design-from-start-to-finish/",
        "category": "Fashion",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["fashion", "design", "clothing", "textile", "apparel", "designer"]
    },
    {
        "title": "Interior Design Fundamentals",
        "provider": "Udemy",
        "url": "https://www.udemy.com/course/interior-design-101/",
        "category": "Interior Design",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["interior", "design", "furniture", "space", "room", "decor", "architecture"]
    },

    # ── Healthcare ──
    {
        "title": "Anatomy Specialization",
        "provider": "Coursera (University of Michigan)",
        "url": "https://www.coursera.org/specializations/anatomy",
        "category": "Healthcare",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["anatomy", "medical", "health", "biology", "surgeon", "doctor", "medicine"]
    },
    {
        "title": "Public Health Specialization",
        "provider": "Coursera (Johns Hopkins)",
        "url": "https://www.coursera.org/specializations/public-health",
        "category": "Public Health",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["public health", "health", "epidemiology", "community", "disease", "prevention"]
    },
    {
        "title": "Dental Medicine",
        "provider": "Coursera (University of Pennsylvania)",
        "url": "https://www.coursera.org/learn/dental-medicine",
        "category": "Healthcare",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["dental", "dentist", "oral", "teeth", "health", "medicine"]
    },

    # ── Robotics & Engineering ──
    {
        "title": "Robotics Specialization",
        "provider": "Coursera (University of Pennsylvania)",
        "url": "https://www.coursera.org/specializations/robotics",
        "category": "Robotics",
        "level": "Intermediate",
        "is_free": False,
        "keywords": ["robotics", "robot", "automation", "engineering", "mechanical", "control"]
    },

    # ── Environmental Science ──
    {
        "title": "Environmental Science & Sustainability",
        "provider": "Coursera (University of Illinois)",
        "url": "https://www.coursera.org/specializations/environmental-science",
        "category": "Environmental Science",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["environment", "climate", "sustainability", "ecology", "science", "green"]
    },

    # ── Content Creation & Animation ──
    {
        "title": "Content Strategy for Professionals",
        "provider": "Coursera (Northwestern)",
        "url": "https://www.coursera.org/specializations/content-strategy",
        "category": "Content Creation",
        "level": "Intermediate",
        "is_free": False,
        "keywords": ["content", "creator", "writing", "strategy", "media", "marketing"]
    },
    {
        "title": "Introduction to Animation",
        "provider": "Khan Academy",
        "url": "https://www.khanacademy.org/computing/pixar",
        "category": "Animation",
        "level": "Beginner",
        "is_free": True,
        "keywords": ["animation", "animator", "pixar", "motion", "graphic", "3d", "creative"]
    },

    # ── Teaching & Education ──
    {
        "title": "Foundations of Teaching for Learning Specialization",
        "provider": "Coursera (Commonwealth Education Trust)",
        "url": "https://www.coursera.org/specializations/foundations-teaching",
        "category": "Education",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["teaching", "teacher", "education", "learning", "pedagogy", "classroom"]
    },

    # ── Project Management ──
    {
        "title": "Google Project Management Professional Certificate",
        "provider": "Coursera",
        "url": "https://www.coursera.org/professional-certificates/google-project-management",
        "category": "Project Management",
        "level": "Beginner",
        "is_free": False,
        "keywords": ["project", "management", "operations", "agile", "scrum", "manager"]
    },
]


# ────────────────────────────────────────────────────────────────
# Stopwords to ignore during matching
# ────────────────────────────────────────────────────────────────
STOPWORDS = {
    "and", "or", "the", "is", "a", "an", "with", "to", "for", "of",
    "in", "on", "at", "by", "i", "am", "like", "want", "interested",
    "need", "learn", "about", "be", "my", "me", "do", "can", "how",
}


def _clean(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text.lower())


def search_courses(query: str, max_results: int = 8):
    """Match courses to a query using keyword relevance scoring."""
    query_clean = _clean(query)
    query_words = [w for w in query_clean.split() if w not in STOPWORDS]

    if not query_words:
        # Return a diverse mix if no meaningful query
        return COURSES[:max_results]

    scored = []
    for course in COURSES:
        score = 0
        kw_str = " ".join(course["keywords"])

        for word in query_words:
            # Exact keyword match
            if word in course["keywords"]:
                score += 5
            # Partial match in keywords string
            elif word in kw_str:
                score += 3
            # Match in title
            if word in course["title"].lower():
                score += 4
            # Match in category
            if word in course["category"].lower():
                score += 2

        if score > 0:
            scored.append((course, score))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    results = []
    for course, _score in scored[:max_results]:
        results.append({
            "title": course["title"],
            "provider": course["provider"],
            "url": course["url"],
            "category": course["category"],
            "level": course["level"],
            "is_free": course["is_free"],
        })

    # If nothing matched, return top courses
    if not results:
        for course in COURSES[:max_results]:
            results.append({
                "title": course["title"],
                "provider": course["provider"],
                "url": course["url"],
                "category": course["category"],
                "level": course["level"],
                "is_free": course["is_free"],
            })

    return results
