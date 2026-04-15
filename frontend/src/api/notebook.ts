// src/lib/notebook.ts

export function resolveNotebookId(
  urlNotebookId?: string | null,
): string {
  // 1️⃣ URL has highest priority (production)
  if (urlNotebookId && urlNotebookId.trim() !== "") {
    return urlNotebookId;
  }

  // 2️⃣ Dev fallback
  const devNotebookId =
    process.env.NEXT_PUBLIC_DEV_NOTEBOOK_ID;

  if (devNotebookId && devNotebookId.trim() !== "") {
    return devNotebookId;
  }

  // 3️⃣ Hard fail (better than silent bugs)
  throw new Error(
    "Notebook ID not found: provide via URL or NEXT_PUBLIC_DEV_NOTEBOOK_ID",
  );
}
