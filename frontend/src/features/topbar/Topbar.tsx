// FILE: D:\buddi\Policybot\frontend\src\features\topbar\Topbar.tsx

"use client";

import Header from "./components/Header";
import TopBrandBar from "./components/TopBrandBar";
import ProfileDropdown from "./components/ProfileDropdown";

export default function Topbar() {
  const handleCollapse = () => {
    // reserved for sidebar collapse if needed later
  };

  return (
    <header
      className="
        w-full 
        bg-[#F1F5F9]
        flex items-center justify-between
        px-12 py-2
      "
    >
      {/* Left side - Logo / Brand */}
      <div className="flex items-center">
        <Header onCollapse={handleCollapse} />
      </div>

      {/* Right side */}
      <div className="flex items-center gap-2">
        <TopBrandBar />
        <ProfileDropdown />
      </div>
    </header>
  );
}