import { Plus } from "lucide-react";

type Props = {
  onClick?: () => void;
  disabled?: boolean;
};

const CreateWorkspaceCard = ({ onClick,disabled }: Props) => {
  return (
    <div
  onClick={!disabled ? onClick : undefined}
  className={`min-w-80 h-56 rounded-xl border border-gray-300 flex flex-col items-center justify-center transition
    ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer hover:shadow-md"}
  `}
>
      <div className="w-14 h-14 rounded-full bg-gray-200 flex items-center justify-center mb-4">
        <Plus className="text-blue-600" size={24} />
      </div>

      <p className="text-gray-800 font-medium text-base">
        Create a new workspace
      </p>
    </div>
  );
};

export default CreateWorkspaceCard;