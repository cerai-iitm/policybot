import TopBar from "./components/sections/TopBar";
import RecentSection from "./components/sections/RecentSection";
import FeaturedSection from "./components/sections/FeaturedSection";

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