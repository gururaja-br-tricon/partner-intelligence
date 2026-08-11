import asyncio
import os
import sys

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ),
)

from app.config import settings
from app.orchestrator.orchestrator import Orchestrator

DEMO_QUESTIONS = [
    "Which partners are most likely to grow?",
    "Which technologies are gaining momentum in Texas?",
    "Which partners should I recruit, and which regions should I prioritize for them?",
]


async def main():
    orchestrator = Orchestrator(mcp_url=settings.mcp_url)

    for index, question in enumerate(DEMO_QUESTIONS, start=1):
        print("\n" + "=" * 80)
        print(f"DEMO QUESTION {index}: {question}")
        print("=" * 80)

        answer = await orchestrator.answer(question)

        print(f"\nRoutes: {orchestrator.last_route}")
        print(f"Cache hit: {orchestrator.last_cache_hit}")

        print("\nANSWER:\n", answer)


if __name__ == "__main__":
    asyncio.run(main())