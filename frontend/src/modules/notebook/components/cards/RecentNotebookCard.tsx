import { MoreVertical } from "lucide-react";

type Props = {
  title: string;
  desc: string;
  createdAt: string;
  onClick?: () => void;
  onMenuClick?: () => void; // optional menu handler
};

const RecentNotebookCard = ({
  title,
  desc,
  createdAt,
  onClick,
  onMenuClick,
}: Props) => {
  return (
    <div
      onClick={onClick}
      className="
        relative
        w-80 h-56
        rounded-xl border border-gray-200
        bg-white
        p-5
        flex flex-col justify-between
        cursor-pointer
        transition-all duration-300 ease-out
        hover:shadow-md hover:border-gray-300
      "
    >
      {/* TOP RIGHT MENU */}
      <button
        onClick={(e) => {
          e.stopPropagation(); // prevent card click
          onMenuClick?.();
        }}
        className="
          absolute top-4 right-4
          p-1.5 rounded-md
          text-gray-400
          hover:bg-gray-100 hover:text-gray-600
          transition
        "
        aria-label="More options"
      >
        <MoreVertical size={18} />
      </button>

      {/* TOP CONTENT */}
      <div className="pr-6">
        <h3 className="text-lg font-semibold text-gray-900 leading-snug line-clamp-1">
          {title}
        </h3>

        <p className="text-sm text-gray-500 mt-2 leading-relaxed line-clamp-2">
          {desc}
        </p>
      </div>

      {/* BOTTOM */}
      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-400">
          Created on{" "}
          <span className="text-gray-500 font-medium">
            {new Date(createdAt).toLocaleDateString()}
          </span>
        </p>

       
      </div>
    </div>
  );
};

export default RecentNotebookCard;