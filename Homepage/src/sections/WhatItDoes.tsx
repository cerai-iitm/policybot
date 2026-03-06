import chatUI from "../assets/ChatUI.png";



const WhatItDoes: React.FC = () => {
  return (
    <section className="bg-white py-20 sm:py-[118px] px-6">

      {/* TITLE */}
      <div className="text-center">
        <h2 className="text-2xl sm:text-3xl lg:text-4xl font-normal text-black font-inter">
          What PolicyBot Does
        </h2>
        <p className="mt-4 text-base sm:text-lg text-black font-['Source_Serif_4']">
          PolicyBot is designed to help people understand policy documents
        </p>
      </div>

      {/* MAIN VISUAL CONTAINER */}
      <div className="relative mt-12 sm:mt-[88px] mx-auto w-full max-w-[1248px]">

        {/* SOFT BLUE BACKGROUND */}
        <div className="absolute inset-0 bg-blue-800/10 rounded-2xl" />

        {/* IMAGE */}
       <div className="relative pt-2 sm:pt-6 flex justify-center px-2 sm:px-0">

          <img
            src={chatUI}
            alt="PolicyBot UI"
            className="w-full max-w-[1197px] h-auto rounded-lg"
          />
        </div>

        {/* BOTTOM FADE */}
        <div className="absolute bottom-0 left-0 right-0 h-40 sm:h-96
          bg-gradient-to-b from-slate-50/0 via-white/80 to-white
          pointer-events-none rounded-b-2xl" />

      </div>

      {/* INFO CARD */}
      <div className="mt-12 sm:mt-18 flex justify-center px-4 sm:px-0">
        <div className="w-full max-w-[731px] p-5 sm:p-6 bg-slate-50 rounded-xl outline outline-1 outline-slate-200">
         <p className="text-center text-sm sm:text-lg text-slate-600 font-['Source_Serif_4'] leading-6 sm:leading-7">

            PolicyBot lets users ask questions in plain language and receive answers
            that are strictly grounded in the original policy text. Every response
            includes clear source citations, making it easy to verify information
            and avoid misinterpretation.
          </p>
        </div>
      </div>

    </section>
  );
};

export default WhatItDoes;
