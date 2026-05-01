"use client"

import { X } from "lucide-react"

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
  isDanger = false
}: ModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">

      {/* 🔹 BACKDROP */}
      <div
        className="absolute inset-0 bg-black/10"
        onClick={onCancel}
      />

      {/* 🔹 MODAL */}
      <div className="relative w-full max-w-md mx-4 bg-white rounded-2xl shadow-xl border border-gray-100 p-6 animate-in fade-in zoom-in-95">

        {/* HEADER */}
        <div className="flex items-start justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {title}
          </h2>

          <button
            onClick={onCancel}
            className="p-1.5 rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition"
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
            aria-label="input"
            value={inputValue}
            onChange={(e) => onInputChange?.(e.target.value)}
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
            "
            placeholder="Enter name..."
          />
        )}

        {/* ACTIONS */}
        <div className="flex justify-end gap-3 pt-2">
          <button
            onClick={onCancel}
            className="
              px-4 py-2
              rounded-lg
              text-sm font-medium
              border border-gray-300
              text-gray-700
              hover:bg-gray-100
              transition
            "
          >
            {cancelText}
          </button>

          <button
            onClick={onConfirm}
            className={`
              px-4 py-2
              rounded-lg
              text-sm font-medium
              text-white
              transition
              ${
                isDanger
                  ? "bg-red-600 hover:bg-red-700"
                  : "bg-blue-600 hover:bg-blue-700"
              }
            `}
          >
            {confirmText}
          </button>
        </div>

      </div>
    </div>
  )
}