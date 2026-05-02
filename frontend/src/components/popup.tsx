"use client"

import { X, Loader2 } from "lucide-react"

interface ModalProps {
  isOpen: boolean
  title: string
  description?: string
  showInput?: boolean
  inputValue?: string
  onInputChange?: (val: string) => void
  confirmText?: string
  cancelText?: string
  onConfirm: () => void
  onCancel: () => void
  isDanger?: boolean
  isLoading?: boolean   // ✅ NEW
}

export default function CommonModal({
  isOpen,
  title,
  description,
  showInput = false,
  inputValue = "",
  onInputChange,
  confirmText = "Save",
  cancelText = "Cancel",
  onConfirm,
  onCancel,
  isDanger = false,
  isLoading = false     // ✅ NEW
}: ModalProps) {
  if (!isOpen) return null


  const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === "Enter" && !isLoading) {
    e.preventDefault();
    onConfirm();
  }
};


  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">

      {/* 🔹 BACKDROP */}
      <div
        className={`absolute inset-0 bg-black/10 ${isLoading ? "pointer-events-none" : ""}`}
        onClick={!isLoading ? onCancel : undefined} // ❌ block close when loading
      />

      {/* 🔹 MODAL */}
      <div className="relative w-full max-w-md mx-4 bg-white rounded-2xl shadow-xl border border-gray-100 p-6 animate-in fade-in zoom-in-95">

        {/* HEADER */}
        <div className="flex items-start justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {title}
          </h2>

          <button
            onClick={!isLoading ? onCancel : undefined}
            disabled={isLoading}
            className="p-1.5 rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition disabled:opacity-50"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>

        {/* DESCRIPTION */}
        {description && (
          <p className="text-sm text-gray-500 mb-4 leading-relaxed">
            {description}
          </p>
        )}

        {/* INPUT */}
        {showInput && (
          <input
            autoFocus
            disabled={isLoading} // ✅ disable while loading
            aria-label="input"
            value={inputValue}
            onChange={(e) => onInputChange?.(e.target.value)}
            onKeyDown={handleKeyDown} 
            className="
              w-full
              border border-gray-300
              rounded-lg
              px-3 py-2
              mb-5
              text-sm
              focus:outline-none
              focus:ring-2
              focus:ring-blue-500
              focus:border-transparent
              transition
              disabled:opacity-60 disabled:cursor-not-allowed
            "
            placeholder="Enter name..."
          />
        )}

        {/* ACTIONS */}
        <div className="flex justify-end gap-3 pt-2">
          <button
            onClick={onCancel}
            disabled={isLoading} // ✅ disable
            className="
              px-4 py-2
              rounded-lg
              text-sm font-medium
              border border-gray-300
              text-gray-700
              hover:bg-gray-100
              transition
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            {cancelText}
          </button>

          <button
            onClick={onConfirm}
            disabled={isLoading} // ✅ prevent spam clicks
            className={`
              flex items-center justify-center gap-2
              px-4 py-2
              rounded-lg
              text-sm font-medium
              text-white
              transition
              disabled:opacity-70 disabled:cursor-not-allowed
              ${
                isDanger
                  ? "bg-red-600 hover:bg-red-700"
                  : "bg-blue-600 hover:bg-blue-700"
              }
            `}
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Processing...
              </>
            ) : (
              confirmText
            )}
          </button>
        </div>

      </div>
    </div>
  )
}