import Arrowright from "../assets/arrow.png";
import { Link, useNavigate } from "react-router-dom";
import { useEffect, useRef } from "react";
import EducationImg from "../assets/notebookbg/education.jpg";
import UnionBudgetImg from "../assets/notebookbg/unionbudget.png";
import AiImg from "../assets/notebookbg/ai.jpg";


/* =========================
   MAIN SECTION
========================= */

const PolicyCollections = (): JSX.Element => {
  const mobileCards = [
    {
      img: EducationImg,
      title: "Education & Academic Policies",
      desc: "Policies related to education systems and learning frameworks.",
      keyword: "education",
    },

    {
      img: AiImg,
      title: "Digital Governance & IT",
      desc: "Digital governance, cybersecurity, and e-government policies.",
      keyword: "digital",
    },
    {
      img: UnionBudgetImg,
      title: "Union Budget 2026-2027",
      desc: "Government budget allocations and reforms shaping the education sector.",
      keyword: "budget",
    },
  ];

  const loopCards = [...mobileCards, ...mobileCards];

  const rowRef = useRef<HTMLDivElement>(null);

  /* =========================
     AUTO + SWIPE LOGIC
  ========================= */

  const navigate = useNavigate();

  const openNotebooksFor = (keyword?: string) => {
    if (keyword) navigate(`/notebook?preferred=${encodeURIComponent(keyword)}`);
    else navigate("/notebook");
  };

  useEffect(() => {
    const container = rowRef.current;
    if (!container) return;

    let animationFrame: number;
    let position = 0;
    let isDragging = false;
    let startX = 0;
    let dragStart = 0;
    const speed = 0.35;

    /* ---------- AUTO SCROLL ---------- */

    const animate = () => {
      if (!isDragging) {
        position -= speed;

       const halfWidth = container.scrollWidth / 2;

if (position <= -halfWidth) {
  position += halfWidth;
} else if (position >= 0) {
  position -= halfWidth;
}

        container.style.transform = `translate3d(${position}px,0,0)`;
      }

      animationFrame = requestAnimationFrame(animate);
    };

    animationFrame = requestAnimationFrame(animate);

    /* ---------- TOUCH EVENTS ---------- */

    const onTouchStart = (e: TouchEvent) => {
      isDragging = true;
      startX = e.touches[0].clientX;
      dragStart = position;
    };

    const onTouchMove = (e: TouchEvent) => {
      if (!isDragging) return;
      const currentX = e.touches[0].clientX;
      const delta = currentX - startX;
      position = dragStart + delta;
      container.style.transform = `translate3d(${position}px,0,0)`;
    };

    const onTouchEnd = () => {
      isDragging = false;

      // keep infinite loop seamless
    const halfWidth = container.scrollWidth / 2;

if (position <= -halfWidth) {
  position += halfWidth;
}

    };

    container.addEventListener("touchstart", onTouchStart);
    container.addEventListener("touchmove", onTouchMove);
    container.addEventListener("touchend", onTouchEnd);

    return () => {
      cancelAnimationFrame(animationFrame);
      container.removeEventListener("touchstart", onTouchStart);
      container.removeEventListener("touchmove", onTouchMove);
      container.removeEventListener("touchend", onTouchEnd);
    };
  }, []);

  return (
    <section className="py-20 sm:py-32 px-6 bg-slate-50 overflow-hidden">

      {/* TITLE */}
      <div className="text-center mb-12 sm:mb-20">
        <h2 className="text-2xl sm:text-3xl lg:text-4xl font-normal text-black font-inter">
          Preloaded Policy Collections
        </h2>
        <p className="mt-4 text-base sm:text-lg text-black font-['Source_Serif_4'] max-w-2xl mx-auto">
          PolicyBot includes a growing collection of preloaded policy notebooks,
          each centered around widely used and important public policies.
        </p>
      </div>

      {/* ================= MOBILE CAROUSEL ================= */}
      <div className="md:hidden w-screen relative left-1/2 right-1/2 -ml-[50vw] -mr-[50vw] overflow-hidden">

        <div
          ref={rowRef}
          className="flex gap-6 w-max px-6 will-change-transform cursor-grab active:cursor-grabbing"
        >
          {loopCards.map((card, index) => (
            <div key={index} className="min-w-[384px]">
              <button
                type="button"
                aria-label={`Open notebooks for ${card.title}`}
                onClick={() => openNotebooksFor(card.keyword)}
                className="p-0 m-0 border-0 bg-transparent"
              >
                <Card img={card.img} title={card.title} desc={card.desc} />
              </button>
            </div>
          ))}
        </div>

        {/* BUTTON */}
        <div className="text-center mt-12 px-6">
          <Link to="/notebook">
            <button className="border border-gray-400 px-6 py-3 rounded-xl transition duration-300 hover:bg-primary hover:text-white hover:scale-105">
              Explore More
            </button>
          </Link>
        </div>
      </div>

      {/* ================= DESKTOP GRID ================= */}
      <div className="hidden md:block max-w-6xl mx-auto">

        <div className="grid md:grid-cols-3 gap-8">
            <button
              type="button"
              aria-label="Open notebooks for Digital Governance & IT"
              onClick={() => openNotebooksFor("digital")}
              className="p-0 m-0 border-0 bg-transparent"
            >
              <Card
                img={AiImg}
                title="Digital Governance & IT"
                desc="Digital governance, cybersecurity, and e-government policies."
              />
            </button>
            <button
              type="button"
              aria-label="Open notebooks for Education & Academic Policies"
              onClick={() => openNotebooksFor("education")}
              className="p-0 m-0 border-0 bg-transparent"
            >
              <Card
                img={EducationImg}
                title="Education & Academic Policies"
                desc="Policies related to education systems and learning frameworks."
              />
            </button>
            <button
              type="button"
              aria-label="Open notebooks for Union Budget 2026-2027"
              onClick={() => openNotebooksFor("budget")}
              className="p-0 m-0 border-0 bg-transparent"
            >
              <Card
                img={UnionBudgetImg}
                title="Union Budget 2026-2027"
                desc="National budget allocations, fiscal strategies, and sector-wide policy reforms."
              />
            </button>
   
        </div>

       

        <div className="text-center mt-16">
          <Link to="/notebook">
            <button className="border border-gray-400 px-6 py-3 rounded-xl transition duration-300 hover:bg-primary hover:text-white hover:scale-105">
              Explore More
            </button>
          </Link>
        </div>
      </div>
    </section>
  );
};

/* =========================
   CARD
========================= */

type CardProps = {
  img: string;
  title: string;
  desc: string;
};

const Card = ({ img, title, desc }: CardProps): JSX.Element => {
  return (
    <div className="w-96 h-80 relative cursor-pointer group overflow-hidden rounded-[10px] will-change-transform">
      <img
        src={img}
        alt={title}
        className="w-96 h-80 absolute inset-0 object-cover
        transition-transform duration-500 ease-out
        group-hover:scale-105 will-change-transform"
      />
      <div className="absolute inset-0 bg-slate-900/60 rounded-[10px]" />
      <h3 className="absolute left-[25px] top-[150px] w-80 text-white text-base font-semibold font-inter">
        {title}
      </h3>
      <p className="absolute left-[25px] top-[184px] w-80 text-gray-200 text-xs leading-5">
        {desc}
      </p>
      <img
        src={Arrowright}
        alt="Arrow Right"
        className="absolute left-[28px] top-[246px] w-5 h-5"
      />
    </div>
  );
};

export default PolicyCollections;
