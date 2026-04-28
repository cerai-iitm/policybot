"use client";

import { Suspense } from "react";
import MainLayout from "../../features/layout/MainLayout";

export default function ConfigPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <MainLayout isAdmin={true} />
    </Suspense>
  );
}