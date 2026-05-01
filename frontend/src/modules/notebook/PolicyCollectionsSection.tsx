import TopBar from "./sections/TopBar";
import RecentSection from "./sections/RecentSection";
import FeaturedSection from "./sections/FeaturedSection";

import { NotebookListItem } from "@/lib/types/notebook";

type Props = {
  notebooks: NotebookListItem[];
  recentNotebooks: NotebookListItem[]; 
  active: string;
  onSelect: (id: string) => void;
};

const PolicyCollectionsSection = ({ notebooks, active, onSelect,recentNotebooks, }: Props) => {
  return (
    <div className="mt-10 mx-30">

      <TopBar />

       <RecentSection
        recentNotebooks={recentNotebooks}
        onSelect={onSelect}
      />

      

    </div>
  );
};

export default PolicyCollectionsSection;