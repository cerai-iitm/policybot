import { useMemo, useState } from "react"
import { FirstNotebookPDFItem } from "@/lib/interfaces"
import TopicRow from "./TopicRow"

type Props = {
  pdfs: FirstNotebookPDFItem[]
  loading: boolean
  title: string
  notebookId?: string
}

const PolicyTopicsSection = ({ pdfs, loading, title, notebookId }: Props) => {
  const [search, setSearch] = useState("")

  const filteredPdfs = useMemo(() => {
    if (!search.trim()) return pdfs

    return pdfs.filter((pdf) =>
      pdf.filename.toLowerCase().includes(search.toLowerCase())
    )
  }, [pdfs, search])

  const handleExplore = () => {
    if (notebookId) {
      window.location.href = `/policybot/chat?notebookid=${notebookId}`
    }
  }

  return (
    <div className="px-12 sm:px-12 mt-6">

      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">

        <div>
          <h2 className="text-xl sm:text-2xl font-semibold">
            {title || "Policies"}
          </h2>
          <p className="text-sm sm:text-base text-gray-500 mt-1">
            Topics
          </p>
        </div>

        <input
          type="text"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border rounded-lg px-4 py-2 w-full sm:w-64 text-sm sm:text-base"
        />
      </div>

      <div className="mt-6 sm:mt-8 flex flex-col gap-4 sm:gap-6">

        {loading && (
          <div className="text-sm sm:text-base text-gray-500">
            Loading PDFs...
          </div>
        )}

        {!loading && pdfs.length === 0 && (
          <div className="text-sm sm:text-base text-gray-400">
            No documents found.
          </div>
        )}

        {!loading && pdfs.length > 0 && filteredPdfs.length === 0 && (
          <div className="text-sm sm:text-base text-gray-400">
            No matching results.
          </div>
        )}

        {!loading && filteredPdfs.map((pdf) => (
          <TopicRow
            key={pdf.pdf_id}
            title={pdf.filename}
            description={pdf.summary ?? "Explore this policy document to understand key provisions, regulatory structure, and implementation framework."}
            onExplore={handleExplore}
          />
        ))}

      </div>
    </div>
  )
}

export default PolicyTopicsSection
