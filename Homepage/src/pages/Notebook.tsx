import { useEffect, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import Navbar from "../sections/Navbar"
import PolicyCollectionsSection from "../notebook/PolicyCollectionsSection"
import PolicyTopicsSection from "../notebook/PolicyTopicsSection"
import { listNotebooks, listPdfs } from "@/lib/router"
import { NotebookListItem, FirstNotebookPDFItem } from "@/lib/interfaces"

const Notebook = () => {
  const [notebooks, setNotebooks] = useState<NotebookListItem[]>([])
  const [activeCollection, setActiveCollection] = useState<string>("")
  const [pdfs, setPdfs] = useState<FirstNotebookPDFItem[]>([])
  const [loading, setLoading] = useState(false)

  // 🔹 Load notebooks on mount (and handle optional preferred query param)
  const location = useLocation()
  const navigate = useNavigate()
  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const preferred = params.get("preferred")

    const fetchNotebooks = async () => {
      try {
        const data = await listNotebooks()

        setNotebooks(data.notebooks)
        // Attempt to auto-select a notebook matching the preferred keyword
        if (preferred) {
          const pref = preferred.toLowerCase()
          const matcher = (title = "") => {
            const t = title.toLowerCase()
            if (pref === "education") return t.includes("education") || t.includes("academic")
            if (pref === "digital") return t.includes("digital") || t.includes("governance") || t.includes("cyber") || t.includes("it")
            if (pref === "budget") return t.includes("union") || t.includes("budget")
            return false
          }

          const match = data.notebooks.find((n) => matcher(n.title))
          if (match) {
            setActiveCollection(match.notebook_id)
          } else if (data.first_notebook_id) {
            // fallback if preferred didn't match
            setActiveCollection(data.first_notebook_id)
          }

          // Clean the URL: remove the preferred query param after we've used it
          navigate(location.pathname, { replace: true })
          return
        }

        // Fallback to existing behavior when no preferred param
        if (data.first_notebook_id) {
          setActiveCollection(data.first_notebook_id)
        }
      } catch (err) {
        console.error("Failed to load notebooks", err)
      }
    }

    fetchNotebooks()
  }, [location.search])

  // 🔹 Load PDFs when active notebook changes
  useEffect(() => {
    if (!activeCollection) return

    const fetchPdfs = async () => {
      try {
        setLoading(true)
        const data = await listPdfs(activeCollection)

        const cleanSummary = (s?: string | null) => {
          if (!s) return s
          // collapse repeated whitespace/newlines and trim
          return s.replace(/\s+/g, " ").trim()
        }

        setPdfs(
          data.pdfs.map((p) => ({
            ...p,
            summary: cleanSummary(p.summary) ?? p.summary,
          }))
        )
      } catch (err) {
        console.error("Failed to load PDFs", err)
      } finally {
        setLoading(false)
      }
    }

    fetchPdfs()
  }, [activeCollection])

const activeNotebookTitle =
  notebooks.find(n => n.notebook_id === activeCollection)?.title || ""

return (
  <div className="min-h-screen bg-white">
    <Navbar />

    <PolicyCollectionsSection
      notebooks={notebooks}
      active={activeCollection}
      onSelect={setActiveCollection}
    />

    <PolicyTopicsSection
      pdfs={pdfs}
      loading={loading}
      title={activeNotebookTitle}
      notebookId={activeCollection}
    />
  </div>
)

}

export default Notebook
