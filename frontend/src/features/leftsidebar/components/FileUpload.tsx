
import Image from "next/image";
import addicon from "@/assets/add.png";

const FileUpload = () => {
  return (
    <button
      className="w-full flex items-center justify-center bg-slate-100  rounded-lg h-12 text-sm font-medium text-slate-700 hover:bg-slate-200 transition"
    >
      <Image src={addicon} alt="" className="w-3 h-3 mr-3" />
      Add sources
    </button>
  );
};

export default FileUpload;