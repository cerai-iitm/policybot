"use client";

import React from "react";
import Image from "next/image";

import Iconone from "@/assets/cerai.png";
import Icontwo from "@/assets/iiit.png";
import Iconthree from "@/assets/wsai.png";

const TopBrandBar = () => {
  return (
    <div>
      <div
        className="
          flex items-center justify-evenly
          w-36 md:w-44
          h-10 md:h-12
          gap-1 md:gap-0
        "
      >

        <a
          href="https://cerai.iitm.ac.in/"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Open CeRAI website"
          title="CeRAI"
        >
          <Image
            src={Iconone}
            alt="CeRAI logo"
            className="
              h-4 md:h-5
              w-auto
              cursor-pointer
              transition duration-300
              hover:scale-110
            "
          />
        </a>

        <a
          href="https://www.iitm.ac.in/"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Open IIT Madras website"
          title="IIT Madras"
        >
          <Image
            src={Icontwo}
            alt="IIT Madras logo"
            className="
              h-4 md:h-5
              w-4 md:w-5
              cursor-pointer
              transition duration-300
              hover:scale-110
            "
          />
        </a>

        <a
          href="https://wsai.iitm.ac.in/"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Open WSAI website"
          title="WSAI"
        >
          <Image
            src={Iconthree}
            alt="WSAI logo"
            className="
              h-4 md:h-5
              w-4 md:w-5
              cursor-pointer
              transition duration-300
              hover:scale-110
            "
          />
        </a>

      </div>
    </div>
  );
};

export default TopBrandBar;