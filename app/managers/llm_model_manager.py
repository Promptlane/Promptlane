from app.db.models.llm_model import LLMModel
from app.managers.base_manager import BaseManager

class LLMModelManager(BaseManager):
    def __init__(self, db_session=None):
        super().__init__(LLMModel, db_session)

    def get_all_models(self):
        return self.get_multi()

    def get_models_by_provider(self, provider: str):
        return self.filter(provider=provider)

    def get_model_by_id(self, model_id: str):
        return self.get_by_field("model_id", model_id)
