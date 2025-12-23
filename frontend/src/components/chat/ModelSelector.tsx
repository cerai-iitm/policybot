"use client";

import React, { useEffect, useState } from "react";
import { withBase } from "@/lib/url";

const API_GET = "/api/get-models";
const API_SET = "/api/set-model";

// Helper function to map backend model IDs to human-readable names

export default function ModelSelector() {
  const [models, setModels] = useState<string[]>([]);
  const [selected, setSelected] = useState<string>("");

  // Fetch supported models on mount
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(withBase(API_GET));
        if (!res.ok) {
          console.error("Failed to fetch models:", res.statusText);
          return;
        }
        const data = await res.json();
        const list = data?.supported_models || [];
        if (!mounted) return;
        setModels(list);
        if (list.length > 0) setSelected((prev) => prev || list[0].name);
      } catch (e) {
        console.error("Error fetching models:", e);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  // Call backend to set model when the selection changes
  const setModelOnServer = async (modelId: string) => {
    try {
      const body = JSON.stringify({ model_name: modelId });

      const res = await fetch(withBase(API_SET), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: body.toString(),
      });

      if (!res.ok) {
        const text = await res.text();
        console.error("Failed to set model:", res.status, text);
      }
    } catch (e) {
      console.error("Error setting model:", e);
    }
  };

  // When user changes selection -> update local state and backend
  const handleChange: React.ChangeEventHandler<HTMLSelectElement> = async (
    e
  ) => {
    const newModelId = e.target.value;
    const newModelName = newModelId;
    setSelected(newModelName);
    await setModelOnServer(newModelId);
  };

  return (
    <div
      className="ml-2 relative flex flex-col items-start"
      title="Select model"
    >
      <div className="relative w-full">
        <select
          value={selected}
          onChange={handleChange}
          className="h-5 text-text bg-bg-light border border-border-muted rounded-md shadow-sm hover:shadow-md focus:ring-2 focus:ring-offset-2 focus:ring-primary outline-none px-3 text-sm min-w-[80px] mr-4 appearance-none"
          aria-label="Model selector"
        >
          {models.length === 0 ? (
            <option value="">Loading...</option>
          ) : (
            models.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))
          )}
        </select>
      </div>
    </div>
  );
}
