from langchain_google_vertexai import ChatVertexAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
import traceback
from datetime import datetime, timezone
from src.main.constants import DefaultLLMConfig
from src.main.exceptions.common_exception import CustomException
from src.main.config.logger import get_logger
from src.main.config.langfuse_config import LangfuseConfig
from typing import Optional, Dict, Any

logger = get_logger(__name__)


def initialize_google_genai_llm(
    model_name: str = DefaultLLMConfig.LLM_MODEL_NAME,
    api_key: Optional[str] = None,
    temperature: float = DefaultLLMConfig.LLM_TEMPERATURE,
    max_output_tokens: Optional[int] = DefaultLLMConfig.LLM_MAX_TOKENS,
    top_p: float = DefaultLLMConfig.LLM_TOP_P,
    **kwargs
) -> ChatGoogleGenerativeAI:
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.error(
                    "API key not provided and GOOGLE_API_KEY env var not set",
                    extra={
                        'user': 'system',
                        'action': 'initialize_google_genai_llm',
                        'timestamp': timestamp,
                        'location': f'{__name__}.initialize_google_genai_llm'
                    }
                )
                raise CustomException(
                    detail="api_key must be provided or GOOGLE_API_KEY environment variable must be set",
                    status_code=400
                )


        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            **kwargs
        )


        return llm

    except CustomException:
        raise

    except Exception as e:
        logger.error(
            f"Unexpected error initializing Google AI Studio LLM: {str(e)}\n{traceback.format_exc()}",
            extra={
                'user': 'system',
                'action': 'initialize_google_genai_llm',
                'timestamp': timestamp,
                'location': f'{__name__}.initialize_google_genai_llm'
            }
        )
        raise CustomException(
            detail=f"Failed to initialize Google AI Studio LLM: {str(e)}",
            status_code=500
        )


def initialize_vertex_ai_llm(
    model_name: str = DefaultLLMConfig.LLM_MODEL_NAME,
    project_id: Optional[str] = None,
    location: str = DefaultLLMConfig.LLM_LOCATION,
    temperature: float = DefaultLLMConfig.LLM_TEMPERATURE,
    max_output_tokens: Optional[int] = DefaultLLMConfig.LLM_MAX_TOKENS,
    top_p: float = DefaultLLMConfig.LLM_TOP_P,
    credentials: Optional[Any] = None,
    **kwargs
) -> ChatVertexAI:
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        if project_id is None:
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            if not project_id:
                logger.error(
                    "Project ID not provided and GOOGLE_CLOUD_PROJECT env var not set",
                    extra={
                        'user': 'system',
                        'action': 'initialize_vertex_ai_llm',
                        'timestamp': timestamp,
                        'location': f'{__name__}.initialize_vertex_ai_llm'
                    }
                )
                raise CustomException(
                    detail="project_id must be provided or GOOGLE_CLOUD_PROJECT environment variable must be set",
                    status_code=400
                )

        if temperature < 0 or temperature > 1:
            logger.error(
                f"Invalid temperature value: {temperature}",
                extra={
                    'user': 'system',
                    'action': 'initialize_vertex_ai_llm',
                    'timestamp': timestamp,
                    'location': f'{__name__}.initialize_vertex_ai_llm'
                }
            )
            raise CustomException(
                detail=f"Temperature must be between 0 and 1, got {temperature}",
                status_code=400
            )

        if max_output_tokens and max_output_tokens <= 0:
            logger.error(
                f"Invalid max_output_tokens value: {max_output_tokens}",
                extra={
                    'user': 'system',
                    'action': 'initialize_vertex_ai_llm',
                    'timestamp': timestamp,
                    'location': f'{__name__}.initialize_vertex_ai_llm'
                }
            )
            raise CustomException(
                detail=f"max_output_tokens must be positive, got {max_output_tokens}",
                status_code=400
            )

        llm_config = ChatVertexAI(
            model_name=model_name,
            project=project_id,
            location=location,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            streaming=False,
            credentials=credentials,
            **kwargs
        )

        return llm_config

    except CustomException:
        raise

    except Exception as e:
        logger.error(
            f"Unexpected error initializing Vertex AI LLM: {str(e)}\n{traceback.format_exc()}",
            extra={
                'user': 'system',
                'action': 'initialize_vertex_ai_llm',
                'timestamp': timestamp,
                'location': f'{__name__}.initialize_vertex_ai_llm'
            }
        )
        raise CustomException(
            detail=f"Failed to initialize Vertex AI LLM: {str(e)}",
            status_code=500
        )

def create_llm_node(
    llm: Optional[ChatVertexAI] = None,
    model_name: str = DefaultLLMConfig.LLM_MODEL_NAME,
    **llm_kwargs
):
    timestamp = datetime.now(timezone.utc).isoformat()

    try:

        if llm is None:
            llm = initialize_vertex_ai_llm(model_name=model_name, **llm_kwargs)

        def llm_node(state: Dict[str, Any]) -> Dict[str, Any]:

            node_timestamp = datetime.now(timezone.utc).isoformat()

            try:

                messages = state.get("messages", [])

                if not messages:
                    logger.warning(
                        "No messages found in state",
                        extra={
                            'user': 'system',
                            'action': 'llm_node_invoke',
                            'timestamp': node_timestamp,
                            'location': f'{__name__}.llm_node'
                        }
                    )

                response = llm.invoke(messages)

                return {"messages": [response]}

            except Exception as e:
                logger.error(
                    f"Error in LLM node invocation: {str(e)}\n{traceback.format_exc()}",
                    extra={
                        'user': 'system',
                        'action': 'llm_node_invoke',
                        'timestamp': node_timestamp,
                        'location': f'{__name__}.llm_node'
                    }
                )
                raise CustomException(
                    detail=f"LLM node invocation failed: {str(e)}",
                    status_code=500
                )


        return llm_node

    except CustomException:
        raise

    except Exception as e:
        logger.error(
            f"Error creating LLM node: {str(e)}\n{traceback.format_exc()}",
            extra={
                'user': 'system',
                'action': 'create_llm_node',
                'timestamp': timestamp,
                'location': f'{__name__}.create_llm_node'
            }
        )
        raise CustomException(
            detail=f"Failed to create LLM node: {str(e)}",
            status_code=500
        )


async def call_llm_with_config(
    prompt: str,
    user_query: str,
    llm_model_config: Optional[Dict[str, Any]] = None,
    trace_name: Optional[str] = None,
    trace_metadata: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> str:
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        if not prompt or not isinstance(prompt, str):
            logger.error(
                f"Invalid prompt: {type(prompt)}",
                extra={
                    'user': 'system',
                    'action': 'call_llm_with_config',
                    'timestamp': timestamp,
                    'location': f'{__name__}.call_llm_with_config'
                }
            )
            raise CustomException(
                detail="Prompt must be a non-empty string",
                status_code=400
            )

        if not user_query or not isinstance(user_query, str):
            logger.error(
                f"Invalid user_query: {type(user_query)}",
                extra={
                    'user': 'system',
                    'action': 'call_llm_with_config',
                    'timestamp': timestamp,
                    'location': f'{__name__}.call_llm_with_config'
                }
            )
            raise CustomException(
                detail="User query must be a non-empty string",
                status_code=400
            )

        if llm_model_config is None:
            llm_model_config = {}

        model_name = llm_model_config.get("llm_model_name", DefaultLLMConfig.LLM_MODEL_NAME)
        temperature = llm_model_config.get("temperature", DefaultLLMConfig.LLM_TEMPERATURE)
        top_p = llm_model_config.get("top_p", DefaultLLMConfig.LLM_TOP_P)
        max_output_tokens = llm_model_config.get("max_output_tokens", DefaultLLMConfig.LLM_MAX_TOKENS)

        api_key = os.environ.get('GOOGLE_API_KEY')
        use_genai = api_key is not None and api_key.strip() != ""

        langfuse_handler = LangfuseConfig.get_callback_handler()
        callbacks = []

        if langfuse_handler:
            if trace_name:
                langfuse_handler.trace_name = trace_name or "llm_call"

            if trace_metadata:
                langfuse_handler.metadata = trace_metadata

            if user_id:
                langfuse_handler.user_id = user_id

            if session_id:
                langfuse_handler.session_id = session_id

            callbacks.append(langfuse_handler)


        if use_genai:
            llm = initialize_google_genai_llm(
                model_name=model_name,
                api_key=api_key,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                top_p=top_p
            )
        else:
            project_id = llm_model_config.get("project_id", None)
            location = llm_model_config.get("location", DefaultLLMConfig.LLM_LOCATION)

            llm = initialize_vertex_ai_llm(
                model_name=model_name,
                project_id=project_id,
                location=location,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                top_p=top_p
            )

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=user_query)
        ]

        if callbacks:
            response = llm.invoke(messages, config={"callbacks": callbacks})
        else:
            response = llm.invoke(messages)

        if not response:
            logger.error(
                "LLM returned empty response",
                extra={
                    'user': 'system',
                    'action': 'call_llm_with_config',
                    'timestamp': timestamp,
                    'location': f'{__name__}.call_llm_with_config'
                }
            )
            raise CustomException(
                detail="LLM returned empty response",
                status_code=500
            )

        content = response.content if hasattr(response, 'content') else str(response)

        if isinstance(content, list):
            text_parts = []
            for part in content:
                if hasattr(part, 'text'):
                    text_parts.append(part.text)
                elif isinstance(part, str):
                    text_parts.append(part)
                else:
                    text_parts.append(str(part))
            result = '\n'.join(text_parts)
        elif isinstance(content, str):
            result = content
        elif hasattr(content, 'text'):
            result = content.text
        else:
            result = str(content)

        if langfuse_handler:
            LangfuseConfig.flush()

        return result

    except CustomException:
        raise

    except Exception as e:
        logger.error(
            f"Unexpected error in LLM call: {str(e)}\n{traceback.format_exc()}",
            extra={
                'user': 'system',
                'action': 'call_llm_with_config',
                'timestamp': timestamp,
                'location': f'{__name__}.call_llm_with_config'
            }
        )
        raise CustomException(
            detail=f"Failed to call LLM: {str(e)}",
            status_code=500
        )







