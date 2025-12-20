"""
Datadog configuration module for APM tracing and monitoring.
"""
import os
from typing import Optional
from src.main.config.config_loader import get_config_value


def get_logger(name):
    from src.main.config.logger import get_logger as _get_logger
    return _get_logger(name)


logger = get_logger(__name__)


class DatadogConfig:
    """Configuration class for Datadog APM and tracing"""

    _initialized: bool = False
    _enabled: bool = False
    _runtime_metrics: Optional = None

    @classmethod
    def initialize(
        cls,
        api_key: Optional[str] = None,
        app_key: Optional[str] = None,
        site: Optional[str] = None,
        service_name: Optional[str] = None,
        env: Optional[str] = None,
        version: Optional[str] = None,
        agent_host: Optional[str] = None,
        agent_port: Optional[int] = None,
        trace_sample_rate: Optional[float] = None,
        log_injection: Optional[bool] = None,
        profiling_enabled: Optional[bool] = None,
        analytics_enabled: Optional[bool] = None,
        runtime_metrics_enabled: Optional[bool] = None,
        enabled: Optional[bool] = None
    ) -> None:
        if cls._initialized:
            logger.info("Datadog already initialized")
            return

        enabled = enabled if enabled is not None else get_config_value('datadog', 'enabled', default=False)

        if not enabled:
            logger.info("Datadog tracing is disabled")
            cls._enabled = False
            cls._initialized = True
            return
        # Load configuration values
        api_key = api_key or get_config_value('datadog', 'api_key', default='')
        app_key = app_key or get_config_value('datadog', 'app_key', default='')
        site = site or get_config_value('datadog', 'site', default='datadoghq.com')
        service_name = service_name or get_config_value('datadog', 'service_name', default='travel-buddy-app')
        env = env or get_config_value('datadog', 'env', default='production')
        version = version or get_config_value('datadog', 'version', default='1.0.0')
        agent_host = agent_host or get_config_value('datadog', 'agent_host', default='127.0.0.1')
        agent_port = agent_port or get_config_value('datadog', 'agent_port', default=8126)
        trace_sample_rate = trace_sample_rate if trace_sample_rate is not None else get_config_value('datadog', 'trace_sample_rate', default=1.0)
        log_injection = log_injection if log_injection is not None else get_config_value('datadog', 'log_injection', default=True)
        profiling_enabled = profiling_enabled if profiling_enabled is not None else get_config_value('datadog', 'profiling_enabled', default=False)
        analytics_enabled = analytics_enabled if analytics_enabled is not None else get_config_value('datadog', 'analytics_enabled', default=True)
        runtime_metrics_enabled = runtime_metrics_enabled if runtime_metrics_enabled is not None else get_config_value('datadog', 'runtime_metrics_enabled', default=True)

        if api_key and 'DD_API_KEY' not in os.environ:
            os.environ['DD_API_KEY'] = api_key
            logger.info("Datadog API key configured")
        elif not api_key and 'DD_API_KEY' not in os.environ:
            logger.warning("No Datadog API key provided. Traces will be sent to agent but may not reach Datadog backend.")

        if app_key and 'DD_APP_KEY' not in os.environ:
            os.environ['DD_APP_KEY'] = app_key
            logger.info("Datadog Application key configured")

        if 'DD_SITE' not in os.environ:
            os.environ['DD_SITE'] = site
            logger.info(f"Datadog site configured: {site}")

        if 'DD_AGENT_HOST' not in os.environ:
            os.environ['DD_AGENT_HOST'] = agent_host
        if 'DD_TRACE_AGENT_PORT' not in os.environ:
            os.environ['DD_TRACE_AGENT_PORT'] = str(agent_port)
        if 'DD_SERVICE' not in os.environ:
            os.environ['DD_SERVICE'] = service_name
        if 'DD_ENV' not in os.environ:
            os.environ['DD_ENV'] = env
        if 'DD_VERSION' not in os.environ:
            os.environ['DD_VERSION'] = version

        # Configure sampling rate via environment variable
        if 'DD_TRACE_SAMPLE_RATE' not in os.environ:
            if 0.0 <= trace_sample_rate <= 1.0:
                os.environ['DD_TRACE_SAMPLE_RATE'] = str(trace_sample_rate)
            else:
                logger.warning(f"Invalid trace_sample_rate: {trace_sample_rate}. Using default 1.0")

        try:
            # Import ddtrace AFTER environment variables are set
            from ddtrace import patch, tracer
            from ddtrace.runtime import RuntimeMetrics

            # Set service tags
            tracer.set_tags({
                'service': service_name,
                'env': env,
                'version': version
            })

            # Patch libraries for automatic instrumentation
            patch(
                fastapi=True,
                httpx=True,
                requests=True,
                logging=log_injection,
                asyncio=True
            )


            if runtime_metrics_enabled:
                try:
                    cls._runtime_metrics = RuntimeMetrics.enable()
                    logger.info("Datadog runtime metrics enabled")
                except Exception as e:
                    logger.warning(f"Failed to enable runtime metrics: {e}")


            if profiling_enabled:
                try:
                    import ddtrace.profiling.auto
                    logger.info("Datadog profiling enabled")
                except Exception as e:
                    logger.warning(f"Failed to enable profiling: {e}")


            if analytics_enabled:
                from ddtrace import config
                config.analytics_enabled = True
                logger.info("Datadog analytics enabled")

            cls._enabled = True
            cls._initialized = True

            logger.info(
                f"Datadog initialized successfully. "
                f"Service: {service_name}, Env: {env}, Version: {version}, "
                f"Agent: {agent_host}:{agent_port}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Datadog: {e}")
            cls._enabled = False
            cls._initialized = True

    @classmethod
    def is_enabled(cls) -> bool:
        """Check if Datadog tracing is enabled"""
        return cls._enabled

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if Datadog has been initialized"""
        return cls._initialized

    @classmethod
    def get_tracer(cls):
        """Get the Datadog tracer instance"""
        if not cls._enabled:
            logger.warning("Datadog is not enabled")
            return None
        try:
            from ddtrace import tracer
            return tracer
        except ImportError:
            logger.error("ddtrace not installed")
            return None

    @classmethod
    def shutdown(cls) -> None:
        """Shutdown Datadog tracing and flush remaining traces"""
        if cls._enabled:
            try:
                from ddtrace import tracer
                tracer.shutdown()
                logger.info("Datadog tracer shutdown successfully")
            except Exception as e:
                logger.error(f"Failed to shutdown Datadog tracer: {e}")


def init_datadog() -> None:
    """
    Initialize Datadog with configuration from config.json.
    This should be called at application startup.
    """
    enabled = get_config_value('datadog', 'enabled', default=False)
    DatadogConfig.initialize(enabled=enabled)


def get_datadog_tracer():
    """
    Get the Datadog tracer instance.

    Returns:
        Datadog tracer or None if not enabled
    """
    if not DatadogConfig.is_initialized():
        init_datadog()
    return DatadogConfig.get_tracer()

