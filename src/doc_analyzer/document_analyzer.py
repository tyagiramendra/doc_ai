import os
import sys
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from utils.model_loader import ModelLoader
from model.models import *
from utils.custom_exception import DocumentPortalException
from prompt.prompt_library import PROMPT_REGISTRY
from logger.custom_logger import CustomLogger

logger = CustomLogger().get_custom_logger(__file__)

class DocumentAnalyzer:
    """
    Analyzes documents using a pre-trained model.
    Automatically logs all actions and supports session-based organization.
    """
    def __init__(self):
        try:
            self.model_loader = ModelLoader()
            self.llm = self.model_loader.load_llm()
            self.parser = JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser  = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
            self.prompt = PROMPT_REGISTRY.get("document_analysis")
        except Exception as e:
            logger.info("An error occured while initializing the DocumentAnalyzer class")
            raise DocumentPortalException(e, sys)
    

    def analyze_document(self, document_text: str):
        try:
            chain = self.prompt | self.llm | self.fixing_parser
            response = chain.invoke({
                    "format_instructions": self.parser.get_format_instructions(),
                    "document_text": document_text
                })
            return response
        
        except Exception as e:
            logger.info("An error occured while analyzing the document")
            raise DocumentPortalException(e, sys)

