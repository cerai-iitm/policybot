export type SidebarItem = {
  filename: string;
  pdf_id: string;
  processing_status: string;
  uploaded_at: string;
};

export interface SidebarProps {
  sources: SidebarItem[];
  checkedPdfs: string[];

  onTogglePdf: (filename: string) => void;
  onSelectPdf: (filename: string) => void;
  onDeletePdf: (pdfId: string, filename: string) => void;
  onSelectAll: () => void;

  // ✅ NEW
  collapsed: boolean;
  onToggleCollapse: () => void;
}