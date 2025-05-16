import os
import pandas as pd
from typing import List, Dict, Any, Optional, Union

class DocumentLoader:
    """
    A utility class for loading different document types into text format 
    for the NodeRAG system. Uses docling for document processing and chunking.
    
    Supported formats:
    - PDF
    - CSV
    - Excel
    - Text files
    - Markdown
    - DOCX
    - PPTX
    """
    
    def __init__(self):
        try:
            import docling
            self.docling = docling
        except ImportError:
            raise ImportError("Please install docling: pip install docling")
            
    def load_document(self, file_path: str) -> str:
        """
        Load a document from a file path and convert it to text.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Extracted text from the document
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Let docling handle different file types
        try:
            doc = self.docling.Document(file_path)
            return doc.text
        except Exception as e:
            # Fallback to traditional methods if docling fails
            if file_extension == '.csv':
                return self.load_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                return self.load_excel(file_path)
            elif file_extension in ['.txt', '.md']:
                return self.load_text(file_path)
            else:
                raise ValueError(f"Failed to process file {file_path}: {str(e)}")
    
    def load_csv(self, file_path: str, return_format: str = 'text') -> Union[str, pd.DataFrame]:
        """
        Load a CSV file and convert it to text or return as DataFrame.
        
        Args:
            file_path: Path to the CSV file
            return_format: 'text' or 'dataframe'
            
        Returns:
            Text representation of the CSV or pandas DataFrame
        """
        df = pd.read_csv(file_path)
        
        if return_format == 'dataframe':
            return df
        else:
            return df.to_string()
    
    def load_excel(self, file_path: str, return_format: str = 'text') -> Union[str, Dict[str, pd.DataFrame]]:
        """
        Load an Excel file and convert it to text or return as DataFrame.
        
        Args:
            file_path: Path to the Excel file
            return_format: 'text' or 'dataframe'
            
        Returns:
            Text representation of the Excel file or dict of DataFrames
        """
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        if return_format == 'dataframe':
            return {sheet: pd.read_excel(file_path, sheet_name=sheet) for sheet in sheet_names}
        else:
            text = ""
            for sheet in sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet)
                text += f"Sheet: {sheet}\n"
                text += df.to_string() + "\n\n"
            return text
    
    def load_text(self, file_path: str) -> str:
        """
        Load a text file and return its contents.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Contents of the text file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def chunk_document(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Chunk a document text using docling's semantic chunker
        
        Args:
            text: Document text to chunk
            chunk_size: Target size in characters for each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        try:
            doc = self.docling.Document.from_text(text)
            chunks = doc.chunks(
                chunker=self.docling.chunking.SemanticChunker(
                    target_chunk_size=chunk_size,
                    overlap=overlap
                )
            )
            return [chunk.text for chunk in chunks]
        except Exception as e:
            # Fallback to a simple chunking method if docling chunking fails
            return self._simple_chunk_text(text, chunk_size, overlap)
    
    def _simple_chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        A simple text chunking method as fallback
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + chunk_size, text_len)
            
            # If we're not at the end, try to find a good breaking point
            if end < text_len:
                # Look for paragraph or sentence breaks
                for separator in ['\n\n', '\n', '. ', '! ', '? ']:
                    pos = text.rfind(separator, start, end)
                    if pos != -1:
                        end = pos + len(separator)
                        break
            
            # Add the chunk
            chunks.append(text[start:end])
            
            # Move to next chunk with overlap
            start = max(start, end - overlap)
        
        return chunks 