"use client";


import { useRouter } from "next/navigation";
import Navbar from "@/features/homepage/Navbar"
import WhatItDoes from "@/features/homepage/WhatItDoes"
import PolicyCollections from "@/features/homepage/PolicyCollections"
import BringYourOwn from "@/features/homepage/BringYourOwn"
import PrivacySection from "@/features/homepage/PrivacySection"
import FAQSection from "@/features/homepage/FAQSection"
import Footer from "@/features/homepage/Footer"
import Reveal from "@/features/homepage/Reveal"


export default function HomePage() {
  const router = useRouter();

   return (
    <div className="min-h-screen bg-white">
      <Navbar />

      {/* Hero Section */}
      <Reveal>
       <div className="flex flex-col items-center justify-center text-center px-6 sm:px-8 mt-24 sm:mt-32">

<h1 className="text-3xl sm:text-5xl lg:text-6xl font-semibold leading-snug sm:leading-tight text-black">
  <span className="block sm:inline">Understand Policies.</span>{" "}
  <span className="block sm:inline">With Evidence.</span>
</h1>



  <p className="mt-6 max-w-2xl sm:max-w-3xl lg:max-w-4xl text-base sm:text-lg lg:text-xl text-black font-['Source_Serif_4']">
    PolicyBot helps you explore government and legal policy documents
    by asking questions and getting answers directly grounded in the
    original text, with clear citations.
  </p>

  
   <button
          onClick={() => router.push("/login")}
          className="mt-12 bg-primary text-white px-8 py-4 rounded-xl hover:scale-105 transition"
        >
          Try PolicyBot
        </button>

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
  );
}