import os
from utils.config_loader import load_config
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from utils.custom_exception import DocumentPortalException

from logger.custom_logger import CustomLogger
import sys
import json
logger = CustomLogger().get_custom_logger(__file__)


class ApiKeyManager:
    REQUIRED_KEYS = ["GROQ_API_KEY", "GOOGLE_API_KEY"]

    def __init__(self):
        self.api_keys = {}
        raw = os.getenv("API_KEYS")

        if raw:
            try:
                parsed = json.loads(raw)
                if not isinstance(parsed, dict):
                    raise ValueError("API_KEYS is not a valid JSON object")
                self.api_keys = parsed
                logger.info("Loaded API_KEYS from ECS secret")
            except Exception as e:
                logger.warning("Failed to parse API_KEYS as JSON", error=str(e))

        # Fallback to individual env vars
        for key in self.REQUIRED_KEYS:
            if not self.api_keys.get(key):
                env_val = os.getenv(key)
                if env_val:
                    self.api_keys[key] = env_val
                    logger.info(f"Loaded {key} from individual env var")

        # Final check
        missing = [k for k in self.REQUIRED_KEYS if not self.api_keys.get(k)]
        if missing:
            logger.error("Missing required API keys", missing_keys=missing)
            raise DocumentPortalException("Missing API keys", sys)

        logger.info("API keys loaded", keys={k: v[:6] + "..." for k, v in self.api_keys.items()})


    def get(self, key: str) -> str:
        val = self.api_keys.get(key)
        if not val:
            raise KeyError(f"API key for {key} is missing")
        return val

class ModelLoader():
    """
    Load Models
    """
    def __init__(self):
        load_dotenv()
        self.config_path = os.path.join(os.environ.get("BASE_PATH"), "config/config.yaml")
        self._validate_env()
        self.config = load_config(self.config_path)
        self.api_key_mgr = ApiKeyManager()
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
                                              max_output_tokens=max_output_tokens, google_api_key=self.api_key_mgr.get("GOOGLE_API_KEY"))
            return llm
        if  provider=="groq":
            llm = ChatGroq(model=model_name,
                                temperature=temperature, api_key=self.api_key_mgr.get("GROQ_API_KEY"))
            return llm
            
        logger.info(f"{provider} llm has been loaded successfully")
    
    def load_embeddings(self):
        """
        Load and return the embedding model.
        """
        try:
            logger.info("Loading embedding model...")
            model_name = self.config["embedding_model"]["model_name"]
            return GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=self.api_key_mgr.get("GOOGLE_API_KEY"))
        except Exception as e:
            logger.error("Error loading embedding model", error=str(e))
            raise DocumentPortalException("Failed to load embedding model", sys)
    
    def load_vector_store(self):
        pass
    


if __name__ == "__main__":
    model_loader = ModelLoader()
    model_loader.load_llm()