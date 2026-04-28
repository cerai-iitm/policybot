"use client";

import React from "react";

interface Props {
  title: string;
  subtitle?: string;
  pageNo: string;
  content: string;
}

const CitationCard: React.FC<Props> = ({
  title,
  subtitle,
  pageNo,
  content,
}) => {
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