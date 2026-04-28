import Arrowright from "@/assets/arrow copy.png";

type Props = {
  img: string;
  title: string;
  desc: string;
  active?: boolean;
  onClick?: () => void;
};

const NotebookCard = ({ img, title, desc, active = false, onClick }: Props) => {
  return (
    <div className="relative overflow-hidden rounded-xl w-80 h-56 transition-all duration-300 ease-out">

      <button
        aria-label="open workspace"
        onClick={onClick}
        className="absolute inset-0 z-20 cursor-pointer"
      />

      <img src={img} alt={title} className="absolute inset-0 h-full w-full object-cover" />

      <div className={`absolute inset-0 ${active ? "bg-black/60" : "bg-black/45"}`} />

      <div className="absolute inset-0 flex flex-col justify-end p-5 gap-2 text-white">
        <h3 className="text-lg font-semibold">{title}</h3>

        <p className="text-sm text-gray-200 line-clamp-2">
          {desc}
        </p>

        <img src={Arrowright.src} alt="" className="w-4 h-4 mt-1" />
      </div>
    </div>
  );
};

export default NotebookCard;