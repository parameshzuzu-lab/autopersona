import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from sqlalchemy.future import select
from app.core.database import init_db, AsyncSessionLocal
from app.models import PublishedPosts, RejectedTopics, Persona, SchedulerStatus, ExecutionLog, Memory
from app.services.autonomous_scheduler import run_autonomous_cycle

async def main():
    print("1. Initializing DB schema...")
    await init_db()
    print("[SUCCESS] DB tables initialized!")
    
    print("2. Running 1 cycle of autonomous AI scheduler...")
    await run_autonomous_cycle()
    print("[SUCCESS] Autonomous cycle completed successfully!")

    print("\n--- DATABASE VERIFICATION METRICS ---")
    async with AsyncSessionLocal() as db:
        persona = (await db.execute(select(Persona))).scalars().first()
        posts = (await db.execute(select(PublishedPosts))).scalars().all()
        rejections = (await db.execute(select(RejectedTopics))).scalars().all()
        memories = (await db.execute(select(Memory))).scalars().all()
        status = (await db.execute(select(SchedulerStatus))).scalars().first()
        logs = (await db.execute(select(ExecutionLog))).scalars().all()

        print(f"Persona Name: {persona.name if persona else 'None'}")
        print(f"Total Published Posts: {len(posts)}")
        if posts:
            safe_title = posts[-1].title.encode('ascii', errors='replace').decode('ascii')
            safe_content = posts[-1].content[:180].encode('ascii', errors='replace').decode('ascii')
            print(f"Latest Post Title: {safe_title}")
            print(f"Latest Post Content Preview:\n{safe_content}\n")
        print(f"Total Rejected Topics: {len(rejections)}")
        if rejections:
            safe_reason = rejections[-1].rejection_reason.encode('ascii', errors='replace').decode('ascii')
            print(f"Latest Rejection Reason: {safe_reason}")
        print(f"Total Persona Memories: {len(memories)}")
        print(f"Scheduler State: {status.status if status else 'None'} | Total Runs: {status.total_runs if status else 0}")
        print(f"Execution Audit Logs Count: {len(logs)}")

if __name__ == "__main__":
    asyncio.run(main())
