"use client";


import { useRouter } from "next/navigation";
import Navbar from "@/modules/homepage/Navbar"
import WhatItDoes from "@/modules/homepage/WhatItDoes"
import PolicyCollections from "@/modules/homepage/PolicyCollections"
import BringYourOwn from "@/modules/homepage/BringYourOwn"
import PrivacySection from "@/modules/homepage/PrivacySection"
import FAQSection from "@/modules/homepage/FAQSection"
import Footer from "@/modules/homepage/Footer"
import Reveal from "@/modules/homepage/Reveal"
import { useAuth } from "@/lib/hooks/useAuth";

export default function HomePage() {

  const { loginDemo, loading } = useAuth();

  const handleDemo = async () => {
  try {
    await loginDemo();
    router.push("/notebook");
  } catch (err) {
    console.error("Demo login failed", err);
  }
};


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

  
<div className="mt-12 flex items-center justify-center gap-4">
  {/* Demo */}
  <button
    onClick={handleDemo}
    disabled={loading}
    className="px-8 py-4 rounded-xl border border-gray-300 text-gray-700 bg-white hover:bg-gray-100 transition"
  >
    Explore Demo
  </button>

  {/* Primary */}
  <button
    onClick={() => router.push("/notebook")}
    className="px-8 py-4 rounded-xl bg-primary text-white hover:scale-105 transition"
  >
    Get Started
  </button>
</div>

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