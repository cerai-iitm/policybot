type Props = {
  title: string
  description: string
  meta?: string
}

const TopicRow = ({ title, description, meta }: Props) => {
  return (
    <div
      className="
        border border-gray-200 
        rounded-2xl 
        p-5 sm:p-6
        flex flex-col sm:flex-row 
        sm:justify-between sm:items-center
        gap-6 sm:gap-4
        bg-white
      "
    >
      {/* TEXT SECTION */}
      <div className="space-y-3 sm:space-y-2 max-w-3xl">

        <h3 className="font-semibold text-lg sm:text-lg leading-snug">
          {title}
        </h3>

        <p className="text-sm sm:text-base text-gray-600 leading-relaxed">
          {description}
        </p>

        {meta && (
          <p className="text-xs sm:text-sm text-gray-400 pt-1">
            {meta}
          </p>
        )}

      </div>

      {/* CTA SECTION */}
      <div className="pt-2 sm:pt-0">
        <button
          className="
            bg-primary text-white 
            px-5 py-2.5
            rounded-xl
            text-sm sm:text-base
            w-full sm:w-auto
            font-medium
            transition-all duration-200
            active:scale-[0.98]
          "
        >
          Explore →
        </button>
      </div>
    </div>
  )
}

export default TopicRow
