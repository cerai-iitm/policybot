
import { PdfItem } from "@/lib/types/pdf";

export interface SidebarProps {
  sources: PdfItem[];
  checkedPdfs: string[];

  onTogglePdf: (pdfId: string) => void;
  onSelectPdf: (pdfId: string) => void;
  onDeletePdf: (pdfId: string) => void;
  onSelectAll: () => void;

  collapsed: boolean;
  onToggleCollapse: () => void;
  onUploadPdf: (file: File) => void;
}