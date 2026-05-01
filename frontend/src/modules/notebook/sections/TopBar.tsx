import { Search, Plus } from "lucide-react";

const TopBar = () => {
  return (
    <div className="flex items-center justify-between mb-10">

      <div className="flex items-center gap-6">
        <button className="px-4 py-2 rounded-full bg-gray-200 text-sm font-medium">
          All
        </button>

     
      </div>

      <div className="flex items-center gap-4">

        <button
          aria-label="search"
          className="p-2 rounded-full border hover:bg-gray-100"
        >
          <Search size={18} />
        </button>

        <button className="flex items-center gap-2 bg-black text-white px-4 py-2 rounded-full text-sm font-medium">
          <Plus size={16} />
          Create Workspace
        </button>

      </div>
    </div>
  );
};

export default TopBar;