import Arrowright from "../../assets/arrow.png"

type CardProps = {
  img: string
  title: string
  desc: string
  active?: boolean
  onClick?: () => void
}

const Card = ({ img, title, desc, active = false, onClick }: CardProps) => {
  return (
    <div
      className={`
        relative overflow-hidden rounded-xl
        aspect-[5/4] w-[22rem] max-w-full
        transition-all duration-300 ease-out
        ${active ? "scale-[1.04] -translate-y-2" : "scale-100"}
      `}
    >
      {/* CLICK LAYER */}
      <button
      aria-label="button"
        onClick={onClick}
        className="absolute inset-0 z-20 cursor-pointer"
      />

      {/* IMAGE */}
      <img
        src={img}
        alt={title}
        className="absolute inset-0 h-full w-full object-cover"
      />

      {/* OVERLAY */}
      <div
        className={`
          absolute inset-0 pointer-events-none
          ${active ? "bg-slate-900/60 shadow-xl" : "bg-slate-900/45"}
        `}
      />

      {/* CONTENT */}
      <div className="absolute inset-0 pointer-events-none flex flex-col justify-end p-5 gap-2">
        <h3 className="text-white text-base font-semibold drop-shadow-lg">
          {title}
        </h3>

        <p className="text-gray-200 text-xs line-clamp-2">
          {desc}
        </p>

        <img src={Arrowright} alt="" className="w-4 h-4 mt-1" />
      </div>
    </div>
  )
}

export default Card
