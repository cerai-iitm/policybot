import Image from "next/image";

interface Props {
  iconSrc: string;
  onToggle: () => void;
}

export default function SelectAllRow({ iconSrc, onToggle }: Props) {
  return (
    <div className="flex items-center justify-between px-5 pt-8 pb-2">
      <span className="text-sm font-medium text-slate-700">
        Select all sources
      </span>

      <button aria-label="button" onClick={onToggle} className="p-1">
        <Image 
          src={iconSrc}
          alt="select all"
          width={20}   // ✅ REQUIRED
          height={20}  // ✅ REQUIRED
          className="cursor-pointer"
        />
      </button>
    </div>
  );
}