import { Upload, MessageCircleQuestion, Telescope } from "lucide-react";

const BringYourOwn: React.FC = () => {
  return (
    <section className="py-20 sm:py-32 px-6 bg-white">

      {/* TITLE */}
      <div className="text-center mb-16 sm:mb-32">
        <h2 className="text-2xl sm:text-4xl font-normal text-black font-inter">
          Bring Your Own Policy Documents
        </h2>

        <p className="mt-4 sm:mt-6 max-w-3xl mx-auto text-base sm:text-lg text-black font-['Source_Serif_4']">
          In addition to preloaded policy collections, PolicyBot allows users to work
          with their own documents. You can upload policy files, guidelines,
          regulations, or internal documents and organize them into private
          collections for exploration.
        </p>
      </div>

      {/* ================= MOBILE VERSION ================= */}
      <div className="sm:hidden max-w-md mx-auto">

        {/* STEP 1 */}
        <div className="flex items-start gap-5">
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 bg-[#e3e6f0] rounded-full flex items-center justify-center">
              <Upload size={24} className="text-primary" />
            </div>
            <div className="w-px h-16 border-l-2 border-dashed border-gray-300 mt-4"></div>
          </div>

          <div>
            <h3 className="text-base font-medium">Upload</h3>
            <p className="mt-2 text-sm text-neutral-500">
              Start with curated public policies or upload your own documents.
            </p>
          </div>
        </div>

        {/* STEP 2 */}
        <div className="flex items-start gap-5 mt-8">
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 bg-[#e3e6f0] rounded-full flex items-center justify-center">
              <MessageCircleQuestion size={24} className="text-primary" />
            </div>
            <div className="w-px h-16 border-l-2 border-dashed border-gray-300 mt-4"></div>
          </div>

          <div>
            <h3 className="text-base font-medium">Ask</h3>
            <p className="mt-2 text-sm text-neutral-500">
              Ask questions from the document and get answers in simple and accessible language.
            </p>
          </div>
        </div>

        {/* STEP 3 */}
      {/* STEP 3 */}
<div className="flex items-start gap-5 mt-8">
  <div className="flex flex-col items-center">
    <div className="w-16 h-16 bg-[#e3e6f0] rounded-full flex items-center justify-center">
      <Telescope size={24} className="text-primary" />
    </div>
  </div>

  <div>
    <h3 className="text-base font-medium">Explore</h3>
    <p className="mt-2 text-sm text-neutral-500">
      PolicyBot understands context and delivers precise answers with exact citations.
    </p>
  </div>
</div>


      </div>

      {/* ================= DESKTOP VERSION (UNCHANGED) ================= */}
      <div className="hidden sm:flex relative max-w-6xl mx-auto items-center justify-between">

        {/* CURVE 1 */}
        <svg
          className="absolute left-[25%] top-[20%]"
          width="180"
          height="60"
          viewBox="0 0 180 60"
          fill="none"
        >
          <path
            d="M10 30 Q90 60 170 30"
            stroke="#9ca3af"
            strokeWidth="2"
            strokeDasharray="6 6"
            fill="transparent"
          />
        </svg>

        {/* CURVE 2 */}
        <svg
          className="absolute right-[25%] top-[20%]"
          width="180"
          height="60"
          viewBox="0 0 180 60"
          fill="none"
        >
          <path
            d="M10 30 Q90 0 170 30"
            stroke="#9ca3af"
            strokeWidth="2"
            strokeDasharray="6 6"
            fill="transparent"
          />
        </svg>

        {/* STEP 1 */}
        <div className="flex flex-col items-center text-center w-1/3 z-10">
          <div className="w-32 h-32 bg-[#e3e6f0] rounded-full flex items-center justify-center mb-6">
            <Upload size={36} className="text-primary" />
          </div>
          <h3 className="text-lg font-medium">Upload</h3>
          <p className="mt-3 text-md font-normal text-neutral-500 max-w-xs">
            Start with curated public policies or upload your own documents.
          </p>
        </div>

        {/* STEP 2 */}
        <div className="flex flex-col items-center text-center w-1/3 z-10">
          <div className="w-32 h-32 bg-[#e3e6f0] rounded-full flex items-center justify-center mb-6">
            <MessageCircleQuestion size={36} className="text-primary" />
          </div>
          <h3 className="text-lg font-medium">Ask</h3>
          <p className="mt-3 text-md font-normal text-neutral-500 max-w-xs">
            Ask questions from the document and get answers in simple and accessible language.
          </p>
        </div>

        {/* STEP 3 */}
        <div className="flex flex-col items-center text-center w-1/3 z-10">
          <div className="w-32 h-32 bg-[#e3e6f0] rounded-full flex items-center justify-center mb-6">
            <Telescope size={36} className="text-primary" />
          </div>
          <h3 className="text-lg font-medium">Explore</h3>
          <p className="mt-3 text-md font-normal text-neutral-500 max-w-xs">
            PolicyBot understands context and delivers precise answers with exact citations.
          </p>
        </div>

      </div>

    </section>
  );
};

export default BringYourOwn;
