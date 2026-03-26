import Card from "../components/ui/Card"
import { NotebookListItem } from "@/lib/interfaces";
import AiImg from "@/assets/notebookbg/ai.jpg";
import EducationImg from "@/assets/notebookbg/education.jpg";
import UnionBudgetImg from "@/assets/notebookbg/unionbudget.png";

// default image used when no match
const defaultImg = EducationImg;

type Props = {
  notebooks: NotebookListItem[]
  active: string
  onSelect: (id: string) => void
}

const PolicyCollectionsSection = ({ notebooks, active, onSelect }: Props) => {
  const getNotebookImage = (title?: string) => {
    if (!title) return defaultImg
    const t = title.toLowerCase()
    if (t.includes("education") || t.includes("academic")) return EducationImg
    if (t.includes("digital") || t.includes("governance") || t.includes("cyber") || t.includes("it")) return AiImg
    if (t.includes("union") || t.includes("budget")) return UnionBudgetImg
    return defaultImg
  }

  return (
    <div className="mt-10">
      <div className="px-12">
        <h2 className="text-2xl font-semibold mb-6">
          Policy Collections
        </h2>
      </div>

      <div className="w-screen overflow-x-hidden overflow-y-visible">

     <div className="flex gap-6 overflow-x-auto flex-nowrap pb-8 pt-4 no-scrollbar px-12 items-end">
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
    </div>
  )
}

export default PolicyCollectionsSection
