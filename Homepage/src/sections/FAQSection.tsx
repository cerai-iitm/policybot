import { useState } from "react"
import { Plus, X } from "lucide-react"

type FAQ = {
  question: string
  answer: string
}

const faqs: FAQ[] = [
  {
    question: "What types of documents can I use with PolicyBot?",
    answer:
      "PolicyBot is designed for policy-related documents such as laws, regulations, government guidelines, institutional rules, and similar official texts. You can explore both preloaded policy collections and your own uploaded policy documents, organized into private collections for structured exploration."
  },
  {
    question: "Are PolicyBot’s answers always cited?",
    answer:
      "Yes, the bot provides answers from the source document(s) and provides the citation(s) for users to go back to the source for verification."
  },
  {
    question: "Does PolicyBot use my documents to train models?",
    answer:
      "No, the bot does not use the documents provided to train models."
  },
  {
    question: "Is PolicyBot giving legal advice?",
    answer:
      "No, the bot is not designed to provide legal advice. We recommend consulting an expert for legal advice."
  },
  {
    question: "Is the application open source?",
    answer:
      "Yes, the link to the source code is provided here"
  }
]

const FAQSection = (): JSX.Element => {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  return (
    <section className="bg-white py-20 sm:py-32 px-6">

      {/* TITLE */}
      <div className="max-w-6xl mx-auto mb-12 sm:mb-20">
        <h2 className="text-2xl sm:text-4xl font-normal text-black leading-tight">
          Frequently <br className="hidden sm:block" /> Asked Questions
        </h2>
      </div>

      {/* FAQ LIST */}
      <div className="max-w-6xl mx-auto space-y-4">

        {faqs.map((faq, index) => {
          const isOpen = openIndex === index

          return (
            <div
              key={index}
              className="bg-white border border-stone-300 rounded-[10px]"
            >
              {/* QUESTION ROW */}
           <button
  onClick={() =>
    setOpenIndex(isOpen ? null : index)
  }
  className="w-full flex items-start justify-between
    px-5 sm:px-10 py-4 sm:py-6 text-left"
>
  <span className="flex-1 pr-4 text-base sm:text-xl font-semibold text-black">
    {faq.question}
  </span>

  <span className="shrink-0 mt-1">
    {isOpen ? (
      <X size={18} className="text-black" />
    ) : (
      <Plus size={18} className="text-black" />
    )}
  </span>
</button>


              {/* ANSWER */}
              <div
                className={`overflow-hidden transition-all duration-300 ease-out ${
                  isOpen ? "max-h-96 px-5 sm:px-10 pb-6 sm:pb-8" : "max-h-0"
                }`}
              >
                <p className="text-sm sm:text-base font-medium text-black font-['Source_Serif_4'] leading-7 sm:leading-8">
                  {faq.answer}
                  {faq.question === "Is the application open source?" && (
                    <>
                      {" "}
                      <a
                        href="https://github.com/cerai-iitm/policybot.git"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="underline underline-offset-4 hover:text-blue-600"
                      >
                        https://github.com/cerai-iitm/policybot.git
                      </a>
                    </>
                  )}
                </p>
              </div>
            </div>
          )
        })}

      </div>
    </section>
  )
}

export default FAQSection
