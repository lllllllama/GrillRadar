"""GrillRadar FastAPI主应用"""
import logging
from pathlib import Path

# 重要：在导入任何模块之前先加载环境变量
from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.api.report import router as report_router
from app.config.settings import settings
from app.config.validator import ConfigValidator
from app.exceptions import ConfigurationError
from app.middleware.rate_limiter import RateLimiterMiddleware

# 配置日志
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="GrillRadar: AI驱动的面试准备「拷问+陪练」报告生成系统"
)

app.add_middleware(
    RateLimiterMiddleware,
    max_requests=settings.API_RATE_LIMIT_REQUESTS,
    window_seconds=settings.API_RATE_LIMIT_WINDOW,
    exempt_paths=["/health", "/api/health", "/api/domains"],
)

# 挂载静态文件
static_path = Path(__file__).parent.parent / "frontend" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
else:
    logger.warning(f"Static directory not found: {static_path}")

# 配置模板
templates_path = Path(__file__).parent.parent / "frontend" / "templates"
if templates_path.exists():
    templates = Jinja2Templates(directory=str(templates_path))
else:
    logger.warning(f"Templates directory not found: {templates_path}")
    templates = None

# 注册路由
app.include_router(report_router)


@app.on_event("startup")
async def validate_configuration():
    """Validate all configuration files at startup"""
    try:
        ConfigValidator.validate_all()
        logger.info("✅ Application configuration validated successfully")
    except ConfigurationError as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        raise  # Stop application startup


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页：报告生成表单"""
    if templates is None:
        return HTMLResponse(content="<h1>Templates not found</h1>", status_code=500)
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def root_health():
    """根路径健康检查"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
