import Navbar from "../sections/Navbar"
import WhatItDoes from "../sections/WhatItDoes"
import PolicyCollections from "../sections/PolicyCollections"
import BringYourOwn from "../sections/BringYourOwn"
import PrivacySection from "../sections/PrivacySection"
import FAQSection from "../sections/FAQSection"
import Footer from "../sections/Footer"
import Reveal from "../sections/Reveal"
import { Link } from "react-router-dom"

const Home = () => {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      {/* Hero Section */}
      <Reveal>
       <div className="flex flex-col items-center justify-center text-center px-6 sm:px-8 mt-24 sm:mt-32">

<h1 className="text-3xl sm:text-5xl lg:text-6xl font-semibold leading-snug sm:leading-tight">
  <span className="block sm:inline">Understand Policies.</span>{" "}
  <span className="block sm:inline">With Evidence.</span>
</h1>



  <p className="mt-6 max-w-2xl sm:max-w-3xl lg:max-w-4xl text-base sm:text-lg lg:text-xl text-black font-['Source_Serif_4']">
    PolicyBot helps you explore government and legal policy documents
    by asking questions and getting answers directly grounded in the
    original text, with clear citations.
  </p>

  <Link to="/notebook" className="w-full sm:w-auto">
   <button 
   className="mt-12 sm:mt-16 bg-primary text-white px-7 sm:px-10 py-3 sm:py-4 rounded-2xl text-base sm:text-lg hover:scale-105 transition duration-300 shadow-md hover:shadow-lg">
      Try PolicyBot
    </button>
  </Link>

</div>

      </Reveal>

 <Reveal>
  <section id="what-it-does">
    <WhatItDoes />
  </section>
</Reveal>

<Reveal>
  <section id="collections">
    <PolicyCollections />
  </section>
</Reveal>

<Reveal>
  <section id="bring-your-own">
    <BringYourOwn />
  </section>
</Reveal>

<Reveal>
  <section id="privacy">
    <PrivacySection />
  </section>
</Reveal>

<Reveal>
  <section id="faq">
    <FAQSection />
  </section>
</Reveal>

      <Reveal><Footer /></Reveal>
    </div>
  )
}

export default Home
