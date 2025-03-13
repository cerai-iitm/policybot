from pathlib import Path
import PyPDF2
import hashlib

class PDFLoader:
  def load(self, source: str):
      path = Path(source)
      if not path.exists():
          raise ValueError(f"PDF file not found: {source}")
      
      text_content = ""
      metadata = {}

      with open(path, 'rb') as file:
          pdf_reader = PyPDF2.PdfReader(file)
          metadata = {
              "total_pages": len(pdf_reader.pages),
              "file_name": path.name,
              "file_size": path.stat().st_size
          }

          for page_num, page in enumerate(pdf_reader.pages, 1):
              text = page.extract_text()
              if text.strip():
                #   text_content += f"\n\n=== Page {page_num} ===\n\n"
                  text_content += text

      doc_id = hashlib.sha256(str(path).encode()).hexdigest()[:16]

      return {"content": text_content.strip(), "meta_data": {"doc_id": doc_id, **metadata}}