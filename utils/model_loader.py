import os
from utils.config_loader import load_config
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from utils.custom_exception import DocumentPortalException

from logger.custom_logger import CustomLogger
import sys
logger = CustomLogger().get_custom_logger(__file__)

class ModelLoader():
    """
    Load Models
    """
    def __init__(self):
        load_dotenv()
        self.config_path = os.path.join(os.environ.get("BASE_PATH"), "config/config.yaml")
        self._validate_env()
        self.config = load_config(self.config_path)
        logger.info("Model Loader Initialized")

    def _validate_env(self):
        required_keys=["GROQ_API_KEY","GOOGLE_API_KEY"]
        missing_keys = [key for key in required_keys if os.environ.get(key) is None]
        if missing_keys:
            logger.info(f"Environment keys are missing.{missing_keys}")
            raise ValueError(f"Environment keys are missing.{missing_keys}")
        logger.info("Environment keys are validated")
    
    def load_llm(self):
        logger.info("Loading LLM")
        llm_config = self.config["llm"]
        provider_name = os.environ.get("LLM_PROVIDER","google")
        provider_config = llm_config[provider_name]
        provider = llm_config[provider_name]["provider"]
        model_name = provider_config["model_name"]
        temperature = provider_config["temperature"]
        max_output_tokens = provider_config["max_output_tokens"]
        if provider=="google":
            llm = ChatGoogleGenerativeAI(model=model_name,
                                              temperature=temperature,
                                              max_output_tokens=max_output_tokens)
            return llm
        if  provider=="groq":
            llm = ChatGroq(model=model_name,
                                temperature=temperature)
            return llm
            
        logger.info(f"{provider} llm has been loaded successfully")
    
    def load_embeddings(self):
        """
        Load and return the embedding model.
        """
        try:
            logger.info("Loading embedding model...")
            model_name = self.config["embedding_model"]["model_name"]
            return GoogleGenerativeAIEmbeddings(model=model_name)
        except Exception as e:
            logger.error("Error loading embedding model", error=str(e))
            raise DocumentPortalException("Failed to load embedding model", sys)
    
    def load_vector_store(self):
        pass
    


if __name__ == "__main__":
    model_loader = ModelLoader()
    model_loader.load_llm()