"""链路追踪工具模块"""

import os
from contextlib import contextmanager
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.resources import Resource

# 配置服务名称
service_name = os.getenv("SERVICE_NAME", "python-admin")

# 创建资源
resource = Resource.create({"service.name": service_name})

# 创建 TracerProvider
provider = TracerProvider(resource=resource)

# 配置 OTLP 导出器
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
)

processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# 获取 tracer
tracer = trace.get_tracer(__name__)

def init_tracing(app, service_name: str):
    """初始化 FastAPI 应用的链路追踪"""
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

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