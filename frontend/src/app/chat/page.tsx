"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import MainLayout from "../../features/layout/MainLayout";

function ChatContent() {
  const searchParams = useSearchParams();
  const notebookId = searchParams.get("notebook_id");

  return <MainLayout notebookId={notebookId} />;
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-screen">Loading...</div>}>
      <ChatContent />
    </Suspense>
  );
}