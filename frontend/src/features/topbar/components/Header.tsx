"use client";

import Image from "next/image";
import Link from "next/link";
import logo from "@/assets/logo.png";

interface Props {
  onCollapse: () => void;
}

export default function SidebarHeader({ onCollapse }: Props) {
  return (
    <div className="flex items-center justify-between">

      {/* ✅ CLICKABLE LOGO */}
      <Link href="/notebook" className="flex items-center">
        <Image
          alt="Buddi logo"
          src={logo}
          className="h-4.5 md:h-5 w-auto cursor-pointer"
          priority
        />
      </Link>

    </div>
  );
}