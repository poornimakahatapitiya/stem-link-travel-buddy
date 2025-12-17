from typing import Optional, Dict, Any
import os
from datetime import datetime, timezone
from src.main.utils.langgraph_utils import call_llm_with_config
from src.main.config.logger import get_logger
from src.main.exceptions.common_exception import CustomException
import traceback

logger = get_logger(__name__)


async def call_generic_agent(
    prompt: str,
    user_query: str,
    api_key: str,
    llm_model_config: Optional[Dict[str, Any]] = None,
    trace_name: Optional[str] = None,
    trace_metadata: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> str:
    """
    Calls the LLM with the given prompt and user query using Google AI Studio API key.
    Includes optional Langfuse tracing for observability.

    Args:
        prompt: System prompt to guide the LLM behavior
        user_query: The user's input query
        api_key: Google AI Studio API key for authentication
        llm_model_config: Optional configuration for the LLM
        trace_name: Optional name for Langfuse trace
        trace_metadata: Optional metadata for the trace
        user_id: Optional user ID for tracking
        session_id: Optional session ID for grouping traces

    Returns:
        str: The LLM's response content
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        if not api_key or not isinstance(api_key, str):
            logger.error(
                "Invalid or missing API key",
                extra={
                    'user': 'system',
                    'action': 'call_generic_agent',
                    'timestamp': timestamp,
                    'location': f'{__name__}.call_generic_agent'
                }
            )
            raise CustomException(
                detail="API key must be a non-empty string",
                status_code=400
            )

        original_api_key = os.environ.get('GOOGLE_API_KEY')
        os.environ['GOOGLE_API_KEY'] = api_key

        try:
            # Prepare trace metadata
            if trace_metadata is None:
                trace_metadata = {}

            trace_metadata.update({
                "model_config": llm_model_config or {},
                "timestamp": timestamp,
                "service": "generic_agent"
            })

            response = await call_llm_with_config(
                prompt=prompt,
                user_query=user_query,
                llm_model_config=llm_model_config,
                trace_name=trace_name or "generic_agent_call",
                trace_metadata=trace_metadata,
                user_id=user_id,
                session_id=session_id
            )

            return response

        finally:
            if original_api_key is not None:
                os.environ['GOOGLE_API_KEY'] = original_api_key
            elif 'GOOGLE_API_KEY' in os.environ:
                del os.environ['GOOGLE_API_KEY']

    except CustomException:
        raise

    except Exception as e:
        logger.error(
            f"Unexpected error in generic agent call: {str(e)}\n{traceback.format_exc()}",
            extra={
                'user': 'system',
                'action': 'call_generic_agent',
                'timestamp': timestamp,
                'location': f'{__name__}.call_generic_agent'
            }
        )
        raise CustomException(
            detail=f"Failed to call generic agent: {str(e)}",
            status_code=500
        )

