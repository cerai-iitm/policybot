import { useEffect, useState } from "react"
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

  // 🔹 Load notebooks on mount
  useEffect(() => {
    const fetchNotebooks = async () => {
      try {
        const data = await listNotebooks()

        setNotebooks(data.notebooks)

        if (data.first_notebook_id) {
          setActiveCollection(data.first_notebook_id)
        }
      } catch (err) {
        console.error("Failed to load notebooks", err)
      }
    }

    fetchNotebooks()
  }, [])

  // 🔹 Load PDFs when active notebook changes
  useEffect(() => {
    if (!activeCollection) return

    const fetchPdfs = async () => {
      try {
        setLoading(true)
        const data = await listPdfs(activeCollection)
        setPdfs(data.pdfs)
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
    />
  </div>
)

}

export default Notebook
