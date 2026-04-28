import Image from "next/image";
import logo from "@/assets/logo.png";


interface Props {
  onCollapse: () => void;
}

export default function SidebarHeader({ onCollapse }: Props) {
  return (
    <>
      <div className="flex items-center justify-between">
        <Image alt="Buddi logo" src={logo} className="h-5 w-auto" />
      </div>

     
    </>
  );
}