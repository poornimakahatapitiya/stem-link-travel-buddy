import os
from typing import Optional
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from src.main.config.logger import get_logger

logger = get_logger(__name__)

class LangfuseConfig:
    _instance: Optional[Langfuse] = None
    _callback_handler: Optional[CallbackHandler] = None
    _enabled: bool = False

    @classmethod
    def initialize(
        cls,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        host: Optional[str] = None,
        enabled: bool = True
    ) -> None:
        if not enabled:
            logger.info("Langfuse tracing is disabled")
            cls._enabled = False
            return

        public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        host = host or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if not public_key or not secret_key:
            logger.warning(
                "Langfuse credentials not found. Tracing will be disabled. "
                "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables."
            )
            cls._enabled = False
            return

        try:
            cls._instance = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host
            )

            cls._callback_handler = CallbackHandler(
                public_key=public_key,
                secret_key=secret_key,
                host=host
            )

            cls._enabled = True
            logger.info(f"Langfuse initialized successfully. Host: {host}")

        except Exception as e:
            logger.error(f"Failed to initialize Langfuse: {e}")
            cls._enabled = False

    @classmethod
    def get_callback_handler(cls) -> Optional[CallbackHandler]:
        if not cls._enabled:
            return None

        if cls._callback_handler is None:
            cls.initialize()

        return cls._callback_handler

    @classmethod
    def get_client(cls) -> Optional[Langfuse]:
        if not cls._enabled:
            return None

        if cls._instance is None:
            cls.initialize()

        return cls._instance

    @classmethod
    def is_enabled(cls) -> bool:
        return cls._enabled

    @classmethod
    def flush(cls) -> None:
        if cls._instance and cls._enabled:
            try:
                cls._instance.flush()
                logger.debug("Langfuse traces flushed")
            except Exception as e:
                logger.error(f"Failed to flush Langfuse traces: {e}")


def init_langfuse():
    enabled = os.getenv("LANGFUSE_ENABLED", "true").lower() in ("true", "1", "yes")
    LangfuseConfig.initialize(enabled=enabled)


init_langfuse()

