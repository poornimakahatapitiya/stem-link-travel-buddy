from fastapi import status, APIRouter
from fastapi.exceptions import HTTPException
from typing import Optional, Dict, Any
from src.main.config.logger import get_logger
from src.main.config import ENDPOINTS
from src.main.constants import (COMMON_ERROR_UNEXPECTED_ERROR, INTERNAL_SERVER_ERROR,
                                COMMON_EXECUTION_ERROR)
from src.main.exceptions.common_exception import CustomException
from src.main.models.v1 import ResponseModel,GenericAgentRequestModel
from src.main.services.v1 import call_generic_agent

logger = get_logger(__name__)
router = APIRouter(prefix=ENDPOINTS.generic_answer)
@router.post("/answer", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def answer_generation(payload: GenericAgentRequestModel):
    try:
        user_query = payload.user_query
        prompt = payload.prompt
        llm_config: Optional[Dict[str, Any]] = payload.llm_model_config.model_dump() if payload.llm_model_config else None
        api_key = payload.api_key

        response = await call_generic_agent(user_query=user_query, prompt=prompt, llm_model_config=llm_config,
                                            api_key=api_key)


        if response is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": COMMON_EXECUTION_ERROR}
            )
        response_data = response

        return ResponseModel(success=True, data=response_data)

    except CustomException as customException:
        logger.error(f"Generic Answer Generation Error: {str(customException.detail)}", exc_info=True)
        raise HTTPException(
            status_code=customException.status_code,
            detail={"message": str(customException.detail)}
        )
    except Exception as generalException:
        logger.error(f"{COMMON_ERROR_UNEXPECTED_ERROR}: {str(generalException)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": INTERNAL_SERVER_ERROR}
        )