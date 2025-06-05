import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import warnings
import re
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Element, Title, NarrativeText, ListItem, Table
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from ..config.settings import settings

logger = logging.getLogger(__name__)

# Configure pdfminer logger to suppress warnings
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# Suppress other common warnings from PDF processing libraries
warnings.filterwarnings("ignore", category=UserWarning, module="pdfminer")
warnings.filterwarnings("ignore", category=UserWarning, module="pikepdf")

class PDFProcessor:
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        # Define minimum/maximum section sizes to avoid tiny/huge chunks
        self.min_section_size = 100  # Minimum characters for a standalone section
        self.max_section_size = self.chunk_size * 1.5  # Allow sections slightly larger than chunk_size
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Extract content from PDF using a structure-aware approach that leverages
        unstructured's element classification to organize content by sections.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return []
            
        try:
            pdf_filename = Path(file_path).name
            
            # Extract elements with unstructured
            elements = partition_pdf(
                filename=file_path,
                strategy="hi_res",
                # hi_res_model_name="detectron2_onnx",
                extract_images_in_pdf=False,
                infer_table_structure=True,
                extract_image_block_types=["Table"],
                include_metadata=True,
                include_page_breaks=True,
            )
            print(elements)
            # Debug: Save elements to a text file for inspection
            debug_output_path = f"{file_path.rsplit('.', 1)[0]}_elements.txt"
            with open(debug_output_path, 'w', encoding='utf-8') as f:
                f.write(f"PDF ELEMENTS EXTRACTION DEBUG: {pdf_filename}\n")
                f.write(f"Total elements: {len(elements)}\n\n")
                
                for i, element in enumerate(elements):
                    element_type = type(element).__name__
                    element_text = str(element).strip()
                    element_page = getattr(getattr(element, "metadata", None), "page_number", "Unknown")
                    
                    f.write(f"[Element {i+1}] Type: {element_type}, Page: {element_page}\n")
                    f.write(f"{element_text}\n")
                    f.write("-" * 80 + "\n\n")
                
            logger.info(f"Elements debug info saved to {debug_output_path}")
            
            # Process elements by section rather than by page
            documents = self._group_elements_by_section(elements, pdf_filename, file_path)
            
            logger.info(f"Successfully extracted {len(documents)} sections from {pdf_filename}")
            return documents
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            return []
            
    def _group_elements_by_section(self, elements: List[Element], pdf_filename: str, file_path: str) -> List[Document]:
        """
        Group elements by section based on titles in the document.
        This leverages unstructured's element classification rather than redoing it later.
        """
        documents = []
        current_section = {"title": "Introduction", "content": [], "page": 1, "level": 0}
        current_page = 1
        
        # First pass: identify and process titles and headings
        for element in elements:
            # Update current page
            element_page = getattr(getattr(element, "metadata", None), "page_number", current_page)
            if element_page != current_page:
                current_page = element_page
            
            # Check if the element is a title/heading
            if isinstance(element, Title) or self._is_likely_heading(element):
                # If we have content in the current section, save it
                if current_section["content"] and len("\n".join([str(e) for e in current_section["content"]])) >= self.min_section_size:
                    doc = Document(
                        page_content="\n".join([str(e) for e in current_section["content"]]),
                        metadata={
                            "source": pdf_filename,
                            "page": current_section["page"],
                            "file_path": file_path,
                            "section_title": current_section["title"],
                            "hierarchy_level": current_section["level"]
                        }
                    )
                    documents.append(doc)
                
                # Determine hierarchy level
                hierarchy_level = self._determine_hierarchy_level(str(element))
                
                # Start a new section
                current_section = {
                    "title": str(element).strip(),
                    "content": [element],
                    "page": element_page,
                    "level": hierarchy_level
                }
            else:
                # Add to current section
                current_section["content"].append(element)
        
        # Don't forget the last section
        if current_section["content"] and len("\n".join([str(e) for e in current_section["content"]])) >= self.min_section_size:
            doc = Document(
                page_content="\n".join([str(e) for e in current_section["content"]]),
                metadata={
                    "source": pdf_filename,
                    "page": current_section["page"],
                    "file_path": file_path,
                    "section_title": current_section["title"],
                    "hierarchy_level": current_section["level"]
                }
            )
            documents.append(doc)
        
        return documents
    
    def _is_likely_heading(self, element: Element) -> bool:
        """
        Detect if an element is likely a heading based on formatting and content,
        even if unstructured didn't classify it as a Title.
        """
        if not isinstance(element, NarrativeText):
            return False
            
        text = str(element).strip()
        
        # Skip if too long
        if len(text) > 100:  # Headings are typically short
            return False
            
        # Common policy document heading patterns
        heading_patterns = [
            r"^([0-9]+\.)+\s+.+",  # Numbered sections like "1.2.3 Title"
            r"^[0-9]+\.\s+.+",     # Simple numbered sections like "1. Title"
            r"^(ARTICLE|SECTION|CHAPTER)\s+[IVXLCDM0-9]+",  # Legal style headings
            r"^[A-Z][A-Z\s]{4,}$"  # ALL CAPS headings (common in policies)
        ]
        
        for pattern in heading_patterns:
            if re.match(pattern, text):
                return True
                
        return False
    
    def _determine_hierarchy_level(self, title: str) -> int:
        """Determine the hierarchy level of a section title."""
        title = title.strip()
        
        # Check for main chapter/article headers
        if re.match(r"^CHAPTER|^ARTICLE", title, re.IGNORECASE):
            return 1
            
        # Check for section headers
        if re.match(r"^SECTION|^\d+\.", title, re.IGNORECASE):
            return 2
            
        # Check for subsection headers (like 1.2.3)
        if re.match(r"^\d+\.\d+\.\d+", title):
            return 3
            
        # Check for subsubsection headers (like 1.2.3.4)
        if re.match(r"^\d+\.\d+\.\d+\.\d+", title):
            return 4
            
        # Default level for other headings
        return 2
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Process documents into chunks for embedding, preserving logical sections
        when possible and only splitting large sections when necessary.
        """
        if not documents:
            return []
            
        try:
            # Sort documents by hierarchy level and page for better organization
            documents.sort(key=lambda x: (
                x.metadata.get("hierarchy_level", 999),
                x.metadata.get("page", 0)
            ))
            
            # Use RecursiveCharacterTextSplitter only when needed
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", ". ", " ", ""],
                length_function=len,
                keep_separator=True
            )
            
            chunks = []
            global_chunk_index = 0
            
            # Process each document (section)
            for i, doc in enumerate(documents):
                section_content = doc.page_content
                section_length = len(section_content)
                
                # Skip empty or tiny sections
                if section_length < self.min_section_size:
                    logger.info(f"Skipping small section: {doc.metadata.get('section_title', 'Unknown')} ({section_length} chars)")
                    continue
                
                # If the section is of reasonable size, use it directly as a chunk
                if section_length <= self.max_section_size:
                    # Use the section directly as a chunk
                    doc.metadata["chunk_index"] = 0
                    doc.metadata["global_chunk_index"] = global_chunk_index
                    doc.metadata["is_full_section"] = True  # Mark as a complete section
                    chunks.append(doc)
                    global_chunk_index += 1
                    logger.debug(f"Using section directly: {doc.metadata.get('section_title', 'Unknown')} ({section_length} chars)")
                else:
                    # Section is too large, split it
                    logger.debug(f"Splitting large section: {doc.metadata.get('section_title', 'Unknown')} ({section_length} chars)")
                    section_chunks = text_splitter.create_documents(
                        [doc.page_content], 
                        [doc.metadata]
                    )
                    
                    # Update metadata for split chunks
                    for j, chunk in enumerate(section_chunks):
                        chunk.metadata["chunk_index"] = j
                        chunk.metadata["global_chunk_index"] = global_chunk_index + j
                        chunk.metadata["is_full_section"] = False  # Mark as a partial section
                        
                        # Make sure all important metadata is preserved
                        if "section_title" not in chunk.metadata:
                            chunk.metadata["section_title"] = doc.metadata.get("section_title", "Unknown Section")
                        if "hierarchy_level" not in chunk.metadata:
                            chunk.metadata["hierarchy_level"] = doc.metadata.get("hierarchy_level", 0)
                    
                    chunks.extend(section_chunks)
                    global_chunk_index += len(section_chunks)
            
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} sections")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing sections: {str(e)}")
            return documents
            
    def process_pdf(self, file_path: str) -> List[Document]:
        """Process a PDF document end-to-end."""
        documents = self.load_pdf(file_path)
        if not documents:
            return []
            
        chunks = self.chunk_documents(documents)
        return chunks
        
    def save_upload(self, file_content: bytes, filename: str) -> str:
        upload_path = os.path.join(settings.UPLOADS_DIR, filename)
        
        try:
            with open(upload_path, "wb") as f:
                f.write(file_content)
            logger.info(f"Saved uploaded file to {upload_path}")
            return upload_path
        except Exception as e:
            logger.error(f"Error saving uploaded file: {str(e)}")
            return ""