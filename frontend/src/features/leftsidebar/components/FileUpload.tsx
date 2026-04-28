import Image from "next/image";
import fileicon from "@/assets/file.png";
import addicon from "@/assets/add.png";

const FileUpload = ({ collapsed }: { collapsed?: boolean }) => {
 if (collapsed) {
  return (
    <div className="flex justify-center items-center py-4">
      <div className="w-10 h-10 min-w-10 min-h-10 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center transition shrink-0">
  <Image src={addicon} alt="add" width={12} height={12} />
</div>
    </div>
  );
}

  return (
    <button className="w-full h-28 rounded-xl bg-slate-100 hover:bg-slate-200 transition flex flex-col items-center justify-center gap-2">
      <div className="w-10 h-10 flex items-center justify-center">
        <Image src={fileicon} alt="add" className="w-5 opacity-80" />
      </div>

      <p className="text-sm font-medium text-slate-700">
        Add sources
      </p>
    </button>
  );
};


export default FileUpload;