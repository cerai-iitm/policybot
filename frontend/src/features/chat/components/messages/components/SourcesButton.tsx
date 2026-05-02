"use client";

import { FiFile } from "react-icons/fi";

const SourcesButton = ({ onClick }: { onClick: () => void }) => {
  return (
    <button
      onClick={onClick}
      className="mt-6 flex items-center gap-2 px-3 py-2 rounded-full border border-slate-300 bg-white text-sm text-slate-600 hover:bg-slate-100 cursor-pointer"
    >
      <FiFile size={14} />
      Sources
    </button>
  );
};

export default SourcesButton;