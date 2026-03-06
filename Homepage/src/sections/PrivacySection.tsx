import privacy from '../assets/privacy.png'

const PrivacySection = (): JSX.Element => {
  return (
    <section className="py-24 sm:py-44 px-6 bg-[#F8F8FA] text-center overflow-hidden">

      {/* TITLE */}
      <h2 className="text-2xl sm:text-4xl font-normal text-black font-inter">
        Privacy & Responsible Use
      </h2>

      {/* DESCRIPTION */}
      <p className="max-w-3xl mx-auto mt-4 sm:mt-6 text-base sm:text-lg text-black font-['Source_Serif_4'] mb-12 sm:mb-16">
        Documents uploaded or explored within PolicyBot are not used to train models
        and are not shared outside the user’s workspace. Policy documents remain
        accessible only within their intended context.
      </p>

      {/* VISUAL CONTAINER */}
      <div className="flex items-center justify-center">
        <img 
          src={privacy} 
          alt="Privacy Illustration" 
          className="w-72 sm:w-96 h-auto"
        />
      </div>

      {/* CUSTOM ANIMATIONS */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-8px); }
        }
      `}</style>

    </section>
  )
}

export default PrivacySection
