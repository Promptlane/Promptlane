from sqlalchemy import Column, String, Integer, Float, Text
from ...db.models.base import BaseModel

class LLMModel(BaseModel):
    __tablename__ = 'llm_models'

    model_id = Column(String(100), unique=True, nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    context_length = Column(Integer, nullable=True)
    completion_length = Column(Integer, nullable=True)
    prompt_price = Column(Float, nullable=True)
    completion_price = Column(Float, nullable=True)
    tags = Column(String(200), nullable=True)
    model_type = Column(String(50), nullable=False, default="text")

    def __repr__(self):
        return f"<LLMModel(model_id='{self.model_id}', provider='{self.provider}', name='{self.name}')>"
