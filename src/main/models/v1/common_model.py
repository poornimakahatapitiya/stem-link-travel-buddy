from pydantic import BaseModel, Field

from typing import Optional, Any, Dict, List



class ResponseModel(BaseModel):
    success: bool=Field(True,description="Indicates if the request was successful")
    data: Any =Field(None,description="Holds the main response data")
    error: Optional[dict] = Field(None,description="Contains error details if any")

class ErrorResponseModel(BaseModel):
    success: bool = Field(True, description="Indicates if the request was successful")
    error: dict= Field(..., description="Contains error details")

class LLMModelConfigModel(BaseModel):
    temperature: Optional[float] = Field(0.1, description="Temperature setting for the LLM")
    top_p: Optional[float] = Field(1.0, description="Top-p sampling value")
    top_k: Optional[int] = Field(None, description="Top-k sampling value")
    candidate_count: Optional[int] = Field(None, description="Number of response candidates to generate")
    max_output_tokens: Optional[int] = Field(8192, description="Maximum output tokens for the response")
    frequency_penalty: Optional[float] = Field(0.0, description="Frequency penalty for the LLM")
    presence_penalty: Optional[float] = Field(0.0, description="Presence penalty for the LLM")
    stop_sequences: Optional[List[str]] = Field(None, description="Stop sequences for the LLM")
    response_logprobs: Optional[bool] = Field(None, description="Include log probabilities in response")
    logprobs: Optional[int] = Field(None, description="Number of log probabilities to include")
    response_mime_type: Optional[str] = Field(None, description="MIME type for response format")
    response_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for structured response")
    routing_config: Optional[Dict[str, Any]] = Field(None, description="Routing configuration for model selection")
    seed: Optional[int] = Field(None, description="Random seed for reproducible outputs")
    audio_timestamp: Optional[bool] = Field(None, description="Include timestamps in audio responses")
    response_modalities: Optional[List[str]] = Field(None, description="Response modalities (e.g., text, audio)")
    media_resolution: Optional[str] = Field(None, description="Resolution setting for media processing")
    speech_config: Optional[Dict[str, Any]] = Field(None, description="Configuration for speech synthesis")
    function_calling_config: Optional[Dict[str, Any]] = Field(None, description="Function calling configuration")
    retrieval_config: Optional[Dict[str, Any]] = Field(None, description="Retrieval configuration for RAG")
    safety_config: Optional[List[Dict[str, Any]]] = Field(None, description="Safety configuration list")
    stream: Optional[bool] = Field(False, description="Enable streaming responses")
    llm_model_name: str = Field(..., description="Name of the LLM model")


class AiRequestModel(BaseModel):
    prompt:str= Field(...,description="The prompt or query provided by the user")
    user_query:str= Field(...,description="The original user query before any processing")
    llm_model_config: LLMModelConfigModel= Field(...,description="Configuration settings for the LLM model")
    api_key: Optional[str] = Field(None,description="API key for authentication if required")