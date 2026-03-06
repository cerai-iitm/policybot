const Footer = (): JSX.Element => {
  return (
    <footer className="bg-[#1F3DB8] text-white pt-16 sm:pt-20">

      {/* TOP SECTION */}
      <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row 
                      items-start sm:items-start 
                      justify-between gap-12 sm:gap-16 text-left">

        {/* LEFT BIG LOGO TEXT */}
        <div>
          <h2
            className="
              text-[48px] leading-[48px] sm:text-[96px] sm:leading-[88px]
              font-black text-white

         transition-all duration-300 ease-out
transform sm:hover:scale-[1.05]

sm:hover:bg-gradient-to-r
sm:hover:from-cyan-300 sm:hover:via-blue-400 sm:hover:to-purple-500
sm:hover:bg-[length:300%_300%]
sm:hover:bg-clip-text sm:hover:text-transparent
sm:hover:[animation:gradient_4s_ease_infinite]

cursor-default sm:cursor-pointer

            "
          >
            Policy <br /> Bot
          </h2>
        </div>

        {/* RIGHT LINKS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-10 sm:gap-20 text-base sm:text-lg">

          {/* Column 1 */}
          <div className="space-y-3 sm:space-y-4">
            <a  href="#what-it-does" className="block relative
              after:absolute after:left-0 after:-bottom-1
              after:h-[2px] after:w-full after:bg-white
              after:scale-x-0 after:origin-left
              after:transition-transform after:duration-300
              hover:after:scale-x-100">
              Overview
            </a>

            <a href="#collections" className="block relative
              after:absolute after:left-0 after:-bottom-1
              after:h-[2px] after:w-full after:bg-white
              after:scale-x-0 after:origin-left
              after:transition-transform after:duration-300
              hover:after:scale-x-100">
              Policy Notebooks
            </a>

            <a  href="#bring-your-own" className="block relative
              after:absolute after:left-0 after:-bottom-1
              after:h-[2px] after:w-full after:bg-white
              after:scale-x-0 after:origin-left
              after:transition-transform after:duration-300
              hover:after:scale-x-100">
              How It Works
            </a>

            <a  href="#faq" className="block relative
              after:absolute after:left-0 after:-bottom-1
              after:h-[2px] after:w-full after:bg-white
              after:scale-x-0 after:origin-left
              after:transition-transform after:duration-300
              hover:after:scale-x-100">
              FAQ
            </a>
          </div>

          {/* Column 2 */}
     
        </div>

      </div>

      {/* DIVIDER */}
      <div className="border-t border-white/40 mt-12 sm:mt-16"></div>

      {/* BOTTOM COPYRIGHT */}
      <div className="text-left sm:text-center px-6 py-6 text-xs sm:text-sm">
        © PolicyBot — All rights reserved
      </div>

    </footer>
  )
}

export default Footer
