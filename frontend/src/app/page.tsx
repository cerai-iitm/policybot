"use client";

import { Suspense } from "react";
import MainLayout from "./components/MainLayout";

export default function Home() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <MainLayout isAdmin={false} />
    </Suspense>
  );
}
