"use client";

import { useSearchParams } from "next/navigation";
import { resolveNotebookId } from "@/lib/notebook";

export function useNotebookId(): string {
  const searchParams = useSearchParams();

  // matches: ?notebookid=xyz
  const urlNotebookId = searchParams.get("notebookid");

  return resolveNotebookId(urlNotebookId);
}
