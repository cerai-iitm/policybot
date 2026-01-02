"use client";

import React from "react";

interface Model {
  id: string;
  name: string;
}

interface ModelSelectorProps {
  models: Model[];
  selected: string;
  onChange: (modelId: string) => void;
}

export default function ModelSelector({
  models,
  selected,
  onChange,
}: ModelSelectorProps) {
  const handleChange: React.ChangeEventHandler<HTMLSelectElement> = (e) => {
    const newModelId = e.target.value;
    onChange(newModelId);
  };

  // Show error state if no models provided
  const displayModels =
    models.length === 0
      ? [{ id: "", name: "Error loading models" }]
      : models;

  return (
    <div
      className="ml-2 relative flex flex-col items-start"
      title="Select model for queries"
    >
      <div className="relative w-full">
        <select
          value={selected}
          onChange={handleChange}
          disabled={models.length === 0}
          className="h-5 text-text bg-bg-light border border-border-muted rounded-md shadow-sm hover:shadow-md focus:ring-2 focus:ring-offset-2 focus:ring-primary outline-none px-3 text-sm min-w-[120px] mr-4 appearance-none disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Model selector"
        >
          {displayModels.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
