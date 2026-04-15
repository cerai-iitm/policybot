import { Plus } from "lucide-react";

type CardProps = {
  onClick?: () => void;
};

const Createcard = ({ onClick }: CardProps) => {
  return (
    <div
      onClick={onClick}
      className="
        w-80 h-52
        rounded-xl border border-gray-300
        flex flex-col items-center justify-center
        cursor-pointer
        hover:shadow-md transition
      "
    >
      {/* PLUS ICON */}
      <div className="w-14 h-14 rounded-full bg-gray-200 flex items-center justify-center mb-4">
        <Plus className="text-blue-600" size={24} />
      </div>

      <p className="text-gray-800 font-medium text-base">
        Create new notebook
      </p>
    </div>
  );
};

export default Createcard;