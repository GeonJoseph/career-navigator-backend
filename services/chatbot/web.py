import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def handle_web_query(query):

    try:
        response = client.search(
            query=query,
            search_depth="basic"
        )

        # --------------------------------------------------
        # 🔥 1️⃣ Best answer (if available)
        # --------------------------------------------------
        if response.get("answer"):
            return response["answer"]

        # --------------------------------------------------
        # 🔥 2️⃣ Fallback to search results
        # --------------------------------------------------
        results = response.get("results", [])

        if not results:
            return "I couldn't find a clear answer."

        # return top result
        return results[0].get("content", "No useful information found.")

    except Exception as e:
        print("⚠️ Tavily error:", e)
        return "Something went wrong while searching."