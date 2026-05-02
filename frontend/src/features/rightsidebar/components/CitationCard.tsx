"use client";
import Image from "next/image";
import React from "react";
import citation from "@/assets/citation.png";

interface Props {
  title: string;
  subtitle?: string;
  pageNo: string;
  content: string;
  collapsed?: boolean; // ✅ include here
   onClick?: () => void;
}

const CitationCard: React.FC<Props> = ({
  title,
  subtitle,
  pageNo,
  content,
  collapsed,
  onClick
}) => {




 if (collapsed) {
  return (
    <div onClick={onClick} className="flex justify-center items-center">
      <div className="w-10 h-10 min-w-10 min-h-10 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center transition shrink-0 cursor-pointer">
        <Image   src={citation} alt="citation" width={14} height={14} />
      </div>
    </div>
  );
}


  return (
    <div className="w-full bg-[#F4F6F8] border border-[#E7EBF0] rounded-xl overflow-hidden">
      
      {/* HEADER */}
      <div className="flex items-start justify-between px-5 pt-4">
        <div>
          <h3 className="text-sm font-medium text-[#1F2937] leading-5">
            {title}
          </h3>
          {subtitle && (
            <p className="text-xs text-[#4B5563] leading-5">
              {subtitle}
            </p>
          )}
        </div>

        <div className="bg-slate-300 text-xs font-medium text-[#1F2937] px-3 py-1 rounded-full">
          Page {pageNo}
        </div>
      </div>

      {/* DIVIDER */}
      <div className="border-t border-white mt-3"></div>

      {/* CONTENT */}
      <div className="px-5 py-4">
        <p className="text-sm text-[#334155] leading-6">
          {content}
        </p>
      </div>
    </div>
  );
};

export default CitationCard;