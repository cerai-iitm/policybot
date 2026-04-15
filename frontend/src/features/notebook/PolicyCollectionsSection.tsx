import Card from "./components/Card";
import Createcard from "./components/Createcard";

import { Search, Plus } from "lucide-react";

import AiImg from "@/assets/notebookbg/ai.jpg";
import EducationImg from "@/assets/notebookbg/education.jpg";
import UnionBudgetImg from "@/assets/notebookbg/unionbudget.png";
import { NotebookListItem } from "@/types";

const defaultImg = EducationImg;

type Props = {
  notebooks: NotebookListItem[];
  active: string;
  onSelect: (id: string) => void;
};

const PolicyCollectionsSection = ({ notebooks, active, onSelect }: Props) => {
  const getNotebookImage = (title?: string) => {
    if (!title) return defaultImg.src;

    const t = title.toLowerCase();

    if (t.includes("education") || t.includes("academic"))
      return EducationImg.src;

    if (
      t.includes("digital") ||
      t.includes("governance") ||
      t.includes("cyber") ||
      t.includes("it")
    )
      return AiImg.src;

    if (t.includes("union") || t.includes("budget"))
      return UnionBudgetImg.src;

    return defaultImg.src;
  };

  return (
    <div className="mt-10 mx-30">

      {/* 🔥 TOP BAR */}
      <div className="flex items-center justify-between mb-10">

        {/* LEFT */}
        <div className="flex items-center gap-6">
          <button className="px-4 py-2 rounded-full bg-gray-200 text-sm font-medium">
            All
          </button>

          <span className="text-gray-700 text-sm">
            Featured notebooks
          </span>
        </div>

        {/* RIGHT */}
        <div className="flex items-center gap-4">

          {/* SEARCH */}
          <button aria-label="search" className="p-2 rounded-full border hover:bg-gray-100">
            <Search size={18} />
          </button>

          {/* CREATE */}
          <button className="flex items-center gap-2 bg-black text-white px-4 py-2 rounded-full text-sm font-medium">
            <Plus size={16} />
            Create new
          </button>
        </div>
      </div>

      {/* 🔥 RECENT */}
      <h2 className="text-xl font-semibold mb-6">
        Recent notebooks
      </h2>

      <div className="flex gap-6 mb-12">
        <Createcard />
      </div>

      {/* 🔥 FEATURED */}
      <h2 className="text-xl font-semibold mb-6">
        Featured notebooks
      </h2>

      <div className="flex gap-6 overflow-x-auto no-scrollbar pb-6">
        {notebooks.map((nb) => (
          <div key={nb.notebook_id} className="flex-shrink-0">
            <Card
              img={getNotebookImage(nb.title)}
              title={nb.title}
              desc={nb.description || "No description available"}
              active={active === nb.notebook_id}
              onClick={() => onSelect(nb.notebook_id)}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default PolicyCollectionsSection;