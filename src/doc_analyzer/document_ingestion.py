import os
import fitz
from datetime import datetime
import uuid
import os

from utils.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
import uuid
import sys

class DocumentHandler:
    """
    Load and save documents.
    """
    def __init__(self, dir_path: str = None, session_id: str = None):
        try:
            self.logger = CustomLogger().get_custom_logger(__name__)
            self.logger.info("Initializing document handler")
            self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_path = os.path.join(os.getcwd(),"data/analyzer_docs/",self.session_id)
            self.session_id = session_id
            os.makedirs(self.session_path, exist_ok=True)
            self.logger.info("Session has been created.")
        except Exception as e:
            self.logger.info("An error occured while trying to inialize ocument handler")
            raise DocumentPortalException(e,sys)

    def read_data(self,pdf_path: str):
        try:
            text_chunks = []
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text_chunks.append(page.get_text())
            text = "\n".join(text_chunks)
            self.logger.info("PDF read successfully", pdf_path=pdf_path, session_id=self.session_id, pages=len(text_chunks))
            return text
        except Exception as e:
            self.logger.info("An error occured while trying to read document")
            raise DocumentPortalException(e,sys)
    

    def save_data(self, uploaded_file):
        try:
            filename = uploaded_file.filename
            file_path = os.path.join(self.session_path, filename)
            if not filename.lower().endswith(".pdf"):
                raise DocumentPortalException("Invalid file type. Only PDFs are allowed.",sys)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            self.logger.info("Document has been saved.")
            return file_path
        except Exception as e:
            self.logger.info("An error occured while trying to save document")
            raise DocumentPortalException(e,sys)
        
if __name__ == "__main__":
    print("Document Handler Test")
    from pathlib import Path
    from io import BytesIO
    
    pdf_path=r"D:/projects/llmops/document_portal/data/analyzer_docs/attention_all_youneed.pdf"
    class DummnyFile:
        def __init__(self,file_path):
            self.filename = Path(file_path).name
            self._file_path = file_path
        def getbuffer(self):
            return open(self._file_path, "rb").read()
        
    dummy_pdf = DummnyFile(pdf_path)
    
    doc_handler = DocumentHandler()
    saved_file=doc_handler.save_data(dummy_pdf)
    content=doc_handler.read_data(saved_file)
    print("PDF Content:")
    print(content[:500])  # Print first 500 characters of the PDF content