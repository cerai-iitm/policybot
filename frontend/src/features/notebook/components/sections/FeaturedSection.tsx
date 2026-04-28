import NotebookCard from "../cards/NotebookCard";
import { NotebookListItem } from "@/lib/types//notebook";
import { getNotebookImage } from "../../utils/getNotebookImage";

type Props = {
  notebooks: NotebookListItem[];
  active: string;
  onSelect: (id: string) => void;
};

const FeaturedSection = ({ notebooks, active, onSelect }: Props) => {
  return (
    <>
      <h2 className="text-xl font-semibold mb-6">
        Featured Workspaces
      </h2>

      <div className="flex gap-6 overflow-x-auto no-scrollbar pb-6">
        {notebooks.map((nb) => (
          <div key={nb.notebook_id} className="shrink-0">
            <NotebookCard
              img={getNotebookImage(nb.title)}
              title={nb.title}
              desc={nb.description || "No description available"}
              active={active === nb.notebook_id}
              onClick={() => onSelect(nb.notebook_id)}
            />
          </div>
        ))}
      </div>
    </>
  );
};

export default FeaturedSection;