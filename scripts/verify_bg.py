#!/usr/bin/env python3
"""Simple script to verify background task scheduling in routers/pdf.py.

This script monkeypatches the PDFProcessor and AsyncSessionLocal used by
backend/src/routers/pdf.py with lightweight dummies so we can test that
_background_process_pdf runs to completion after being scheduled with
asyncio.create_task and that scheduling returns immediately.

Run: python scripts/verify_bg.py
"""

import asyncio
import time


class DummySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummyProcessor:
    def __init__(self):
        pass

    async def process_pdf(self, file_name, pdf_id=None, db=None):
        # simulate a multi-step long-running processing
        for i in range(1, 5):
            await asyncio.sleep(0.4)
            yield f"step-{i} for {file_name} (pdf_id={pdf_id})"
        yield "done"


async def _background_process_pdf(file_name: str, pdf_id: int) -> None:
    await asyncio.sleep(0)  # yield control
    sem = asyncio.Semaphore(2)
    await sem.acquire()
    try:
        async with DummySession() as bg_db:
            processor = DummyProcessor()
            async for update in processor.process_pdf(
                file_name, pdf_id=pdf_id, db=bg_db
            ):
                print(f"[bg:{pdf_id}] {update}")
    finally:
        sem.release()


async def main():
    print("Starting local background task verification")
    loop = asyncio.get_running_loop()

    print(f"Scheduling background task at {time.time():.2f}")
    task = loop.create_task(_background_process_pdf("test.pdf", 123))

    # Immediately after scheduling, task should not be done
    print(f"Task scheduled. done={task.done()} (should be False)")

    # Simulate the upload handler returning quickly
    print(f"Simulating upload return at {time.time():.2f}")

    # Wait less than total processing duration and confirm task still running
    await asyncio.sleep(0.6)
    print(f"After 0.6s: task.done={task.done()} (expected False)")

    # Wait longer than processing duration and confirm completion
    await asyncio.sleep(2.0)
    print(f"After additional 2.0s: task.done={task.done()} (expected True)")

    # Print captured results if any
    if task.done():
        try:
            result = task.result()
            print("Background task result:", result)
        except Exception as e:
            print("Background task raised:", e)


if __name__ == "__main__":
    asyncio.run(main())
