import { BrowserRouter, Routes, Route } from "react-router-dom"
import Home from "./pages/Home"
import Notebook from "./pages/Notebook"

function App() {
  return (
    <BrowserRouter basename="/policybot">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/notebook" element={<Notebook />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
