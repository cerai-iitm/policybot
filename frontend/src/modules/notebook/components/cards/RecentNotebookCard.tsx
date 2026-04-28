type Props = {
  title: string;
  desc: string;
  createdAt: string;
  onClick?: () => void;
};

const RecentNotebookCard = ({
  title,
  desc,
  createdAt,
  onClick,
}: Props) => {
  return (
    <div
      onClick={onClick}
      className="
        w-80 h-52
        rounded-xl border border-gray-200
        p-5
        flex flex-col justify-between
        cursor-pointer
        hover:shadow-sm hover:border-gray-300
        transition
        bg-white
      "
    >
      {/* TOP */}
      <div>
        <h3 className="text-base font-semibold text-gray-900 line-clamp-1">
          {title}
        </h3>

        <p className="text-sm text-gray-500 mt-2 line-clamp-2">
          {desc}
        </p>
      </div>

      {/* BOTTOM */}
      <div className="text-xs text-gray-400">
        Created on {new Date(createdAt).toLocaleDateString()}
      </div>
    </div>
  );
};

export default RecentNotebookCard;