import { useState } from "react"
import { FaGithub, FaBars, FaTimes } from "react-icons/fa"
import logo from "./../assets/logo.png"
import { Link } from "react-router-dom"

const Navbar = (): JSX.Element => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <nav className="sticky top-0 z-50 flex justify-between items-center px-12 py-6 bg-white/90 backdrop-blur-md">

        {/* Logo */}
        <Link
            to="/"
           
          >
        <img
          src={logo}
          alt="PolicyBot"
          className="h-6 w-auto"
        />
</Link>
        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-10">

          <Link
            to="/"
            className="relative text-gray-800 font-medium transition duration-300 hover:text-primary group"
          >
            Overview
            <span className="absolute left-0 -bottom-1 w-0 h-[2px] bg-primary transition-all duration-300 group-hover:w-full"></span>
          </Link>

          <Link
            to="/notebook"
            className="relative text-gray-800 font-medium transition duration-300 hover:text-primary group"
          >
            Policy Notebooks
            <span className="absolute left-0 -bottom-1 w-0 h-[2px] bg-primary transition-all duration-300 group-hover:w-full"></span>
          </Link>

          <a
            href="https://github.com/cerai-iitm/policybot.git"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Open PolicyBot GitHub repository"
            title="GitHub"
          >
            <FaGithub className="text-xl text-gray-700 cursor-pointer transition duration-300 hover:scale-125 hover:text-primary" />
          </a>

          <Link to="/notebook">
            <button className="border border-gray-400 px-6 py-2 rounded-xl transition duration-300 hover:bg-primary hover:text-white hover:scale-105">
              Get Started
            </button>
          </Link>

        </div>

        {/* Mobile Hamburger */}
        <button
        type="button"
        aria-label="Open mobile menu"
          className="md:hidden text-2xl text-gray-800"
          onClick={() => setIsOpen(true)}
        >
          <FaBars />
        </button>
      </nav>

      {/* Mobile Fullscreen Menu */}
      <div
        className={`fixed inset-0 bg-white z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex justify-between items-center px-6 py-6 border-b">
          <img src={logo} alt="PolicyBot" className="h-6 w-auto" />
          <button
          type="button"          aria-label="Close mobile menu"
            onClick={() => setIsOpen(false)}
            className="text-2xl text-gray-800"
          >
            <FaTimes />
          </button>
        </div>

        <div className="flex flex-col gap-8 px-6 pt-12 text-left">

          <Link
            to="/"
            onClick={() => setIsOpen(false)}
            className="text-xl font-medium text-gray-800"
          >
            Overview
          </Link>

          <Link
            to="/notebook"
            onClick={() => setIsOpen(false)}
            className="text-xl font-medium text-gray-800"
          >
            Policy Notebooks
          </Link>

          <a
            href="https://github.com/cerai-iitm/policybot.git"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 text-xl font-medium text-gray-800"
          >
            <FaGithub />
            GitHub
          </a>

          <Link
            to="/notebook"
            onClick={() => setIsOpen(false)}
          >
            <button className="mt-4 w-full box-border border border-gray-400 px-6 py-3 rounded-xl transition duration-300 hover:bg-primary hover:text-white">

              Get Started
            </button>
          </Link>

        </div>
      </div>
    </>
  )
}

export default Navbar
