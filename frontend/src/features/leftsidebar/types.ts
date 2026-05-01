
import { PdfItem } from "@/lib/types/pdf";

export interface SidebarProps {
  title: string;
  notebookId: string;
  onUpdateTitle: (newTitle: string) => Promise<void>;
  sources: PdfItem[];
  checkedPdfs: string[];

  onTogglePdf: (pdfId: string) => void;
  onSelectPdf: (pdfId: string) => void;
  onDeletePdf: (pdfId: string) => void;
  onSelectAll: () => void;

  collapsed: boolean;
  onToggleCollapse: () => void;
  onUploadPdf: (file: File) => void;
  onOpenProcessing: (item: any) => void;
  onRenamePdf?: (id: string, name: string) => void;
  autoOpenUpload?: boolean;
}