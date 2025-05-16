import os
import json
from ...config import NodeConfig
from ...logging import info_timer
from ...storage import genid
from ...utils.document_loader import DocumentLoader




class INIT_pipeline():
    def __init__(self, config:NodeConfig):
        
        self.config = config
        self.documents_path = []
        self.document_loader = DocumentLoader()
        
    @property
    def document_path_hash(self):
        if self.documents_path is None:
            raise ValueError('Document path is not loaded')
        else:
            return genid(''.join(self.documents_path),"sha256")
    
    def check_folder_structure(self):
        if not os.path.exists(self.config.main_folder):
            raise ValueError(f'Main folder {self.config.main_folder} does not exist')
        
        if not os.path.exists(self.config.input_folder):
            raise ValueError(f'Input folder {self.config.input_folder} does not exist')
        
    def load_files(self):
        supported_extensions = {
            'mixed': ['.txt', '.md', '.pdf', '.csv', '.xlsx', '.xls', '.docx', '.pptx'],
            'txt': ['.txt'],
            'md': ['.md'],
            'pdf': ['.pdf'],
            'csv': ['.csv'],
            'excel': ['.xlsx', '.xls'],
            'docx': ['.docx'],
            'pptx': ['.pptx']
        }
        
        # Get the list of extensions to check based on config
        if self.config.docu_type in supported_extensions:
            extensions = supported_extensions[self.config.docu_type]
        else:
            # Default to txt and md if unsupported type
            extensions = [f'.{self.config.docu_type}']
            
        for file in os.listdir(self.config.input_folder):
            file_extension = os.path.splitext(file)[1].lower()
            if file_extension in extensions:
                file_path = os.path.join(self.config.input_folder, file)
                self.documents_path.append(file_path)
                    
        if len(self.documents_path) == 0:
            raise ValueError(f'No files found in {self.config.input_folder} with extensions {extensions}')
    
    def check_increment(self):
        if not os.path.exists(self.config.document_hash_path):
            self.save_document_hash()
            return False
        else:
            with open(self.config.document_hash_path,'r') as f:
                file = json.load(f)
            previous_hash = file['document_path_hash']
            if previous_hash == self.document_path_hash:
                return False
            else:
                return True
            
    def save_document_hash(self):
        os.makedirs(os.path.dirname(self.config.document_hash_path), exist_ok=True)
        with open(self.config.document_hash_path,'w') as f:
            json.dump({'document_path_hash':self.document_path_hash,'document_path':self.documents_path},f)
     
   
    @info_timer(message='Init Pipeline')
    async def main(self):
        self.check_folder_structure()
        self.load_files()
        if self.check_increment():
            self.save_document_hash()
            return True
        else:
            return False
        
        
        
