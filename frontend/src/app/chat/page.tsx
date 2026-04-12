"use client";

import { Suspense } from "react";
import MainLayout from "../../features/chat/layout/MainLayout";

function ChatContent() {
  return <MainLayout />;
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-screen">Loading...</div>}>
      <ChatContent />
    </Suspense>
  );
}