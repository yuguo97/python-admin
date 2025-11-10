"""链路追踪工具模块"""

import os
from contextlib import contextmanager
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.resources import Resource
from utils.logger import setup_logger

logger = setup_logger("tracing", "tracing")

# 配置服务名称
service_name = os.getenv("SERVICE_NAME", "python-admin")

# 创建资源
resource = Resource.create({"service.name": service_name})

# 创建 TracerProvider
provider = TracerProvider(resource=resource)

# 配置导出器 - 如果启用追踪则使用OTLP,否则使用Console或不导出
enable_tracing = os.getenv("ENABLE_TRACING", "false").lower() == "true"

if enable_tracing:
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
        )
        processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(processor)
        logger.info("链路追踪已启用,使用OTLP导出器")
    except Exception as e:
        logger.warning(f"OTLP导出器初始化失败,链路追踪将被禁用: {str(e)}")
else:
    logger.info("链路追踪未启用")

trace.set_tracer_provider(provider)

# 获取 tracer
tracer = trace.get_tracer(__name__)

def init_tracing(app, service_name: str):
    """初始化 FastAPI 应用的链路追踪"""
    try:
        if enable_tracing:
            FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
            logger.info(f"FastAPI链路追踪已初始化: {service_name}")
    except Exception as e:
        logger.warning(f"FastAPI链路追踪初始化失败: {str(e)}")

@contextmanager
def create_span(name: str):
    """创建新的 span"""
    with tracer.start_as_current_span(name) as span:
        yield span

def add_span_attribute(span, key: str, value: str):
    """添加 span 属性"""
    span.set_attribute(key, value)

def set_span_status(span, code: StatusCode, message: str = None):
    """设置 span 状态"""
    span.set_status(Status(code, message))

def end_span(span):
    """结束 span"""
    span.end() 