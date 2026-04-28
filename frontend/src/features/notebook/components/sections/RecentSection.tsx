import CreateWorkspaceCard from "../cards/CreateWorkspaceCard";
import RecentNotebookCard from "../cards/RecentNotebookCard";
import { NotebookListItem } from "@/lib/types/notebook";

type Props = {
  recentNotebooks?: NotebookListItem[]; // 👈 make optional
  onSelect: (id: string) => void;
};

const RecentSection = ({ recentNotebooks = [], onSelect }: Props) => {
  return (
    <>
      <h2 className="text-xl font-semibold mb-6">
        Recent Workspaces
      </h2>

      <div className="flex gap-6 mb-12 overflow-x-auto no-scrollbar">

        <CreateWorkspaceCard />

        {recentNotebooks.map((nb) => (
          <div key={nb.notebook_id} className="shrink-0">
            <RecentNotebookCard
              title={nb.title}
              desc={nb.description || "No description available"}
              createdAt={nb.created_at}
              onClick={() => onSelect(nb.notebook_id)}
            />
          </div>
        ))}

      </div>
    </>
  );
};

export default RecentSection;