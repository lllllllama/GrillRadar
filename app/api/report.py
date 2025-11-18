"""
FastAPI路由：报告生成接口

Refactored to use GrillRadarPipeline for cleaner architecture.
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field, ValidationError

from app.models import UserConfig, Report
from app.core.pipeline import GrillRadarPipeline
from app.utils.markdown import report_to_markdown
from app.utils.domain_helper import domain_helper
from app.config.config_manager import config_manager
from app.config.settings import settings
from app.utils.document_parser import parse_resume_bytes, is_supported_format, DocumentParseError
from app.core.logging import get_logger, generate_request_id

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["report"])


class GenerateReportRequest(BaseModel):
    """生成报告请求（Milestone 4 增强）"""
    mode: str = Field(..., pattern="^(job|grad|mixed)$", description="模式：job/grad/mixed")
    target_desc: str = Field(..., min_length=5, description="目标描述")
    domain: Optional[str] = Field(None, description="领域选择（可选）")
    resume_text: str = Field(..., min_length=50, max_length=10000, description="简历内容")

    # Milestone 4: 外部信息源字段
    enable_external_info: bool = Field(default=False, description="是否启用外部信息源（JD、面经）")
    target_company: Optional[str] = Field(None, description="目标公司名称（用于外部信息检索）")


class GenerateReportResponse(BaseModel):
    """生成报告响应"""
    success: bool
    report: Optional[Report] = None
    markdown: Optional[str] = None
    error: Optional[str] = None


@router.post("/generate-report", response_model=GenerateReportResponse)
async def generate_report(request: GenerateReportRequest):
    """
    生成面试准备报告

    Args:
        request: 生成报告请求

    Returns:
        生成的报告（JSON格式 + Markdown格式）
    """
    # Generate request ID for tracing
    request_id = generate_request_id()
    extra = {'request_id': request_id}

    logger.info(f"API request received - mode={request.mode}", extra=extra)

    try:
        # 构建UserConfig with resume_text
        user_config = UserConfig(
            mode=request.mode,
            target_desc=request.target_desc,
            domain=request.domain,
            resume_text=request.resume_text,
            enable_external_info=request.enable_external_info,
            target_company=request.target_company
        )

        # Use GrillRadarPipeline for report generation
        pipeline = GrillRadarPipeline(request_id=request_id)
        report = await pipeline.run_with_text_async(
            resume_text=request.resume_text,
            user_config=user_config
        )

        # 导出Markdown
        markdown_content = report_to_markdown(report)

        logger.info(f"API request completed successfully", extra=extra)

        return GenerateReportResponse(
            success=True,
            report=report,
            markdown=markdown_content
        )

    except ValidationError as e:
        logger.error(f"Validation error: {e}", extra=extra)
        return GenerateReportResponse(
            success=False,
            error=f"数据验证失败: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Report generation failed: {e}", extra=extra, exc_info=True)
        return GenerateReportResponse(
            success=False,
            error=f"报告生成失败: {str(e)}"
        )


@router.post("/generate-report-form")
async def generate_report_form(
    mode: str = Form(...),
    target_desc: str = Form(...),
    domain: Optional[str] = Form(None),
    resume_text: str = Form(...)
):
    """
    生成面试准备报告（表单提交版本）

    支持从HTML表单直接提交数据
    """
    try:
        request = GenerateReportRequest(
            mode=mode,
            target_desc=target_desc,
            domain=domain,
            resume_text=resume_text
        )
        return await generate_report(request)
    except ValidationError as e:
        logger.error(f"Form validation error: {e}")
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": f"表单数据验证失败: {str(e)}"}
        )


@router.post("/generate-report-upload")
async def generate_report_upload(
    mode: str = Form(...),
    target_desc: str = Form(...),
    domain: Optional[str] = Form(None),
    resume_file: UploadFile = File(...),
    enable_external_info: bool = Form(False),
    target_company: Optional[str] = Form(None)
):
    """
    生成面试准备报告（文件上传版本）

    支持上传简历文件（PDF、Word、TXT、Markdown）

    Args:
        mode: 模式（job/grad/mixed）
        target_desc: 目标岗位描述
        domain: 领域（可选）
        resume_file: 简历文件（支持 .pdf, .docx, .txt, .md）
        enable_external_info: 是否启用外部信息源
        target_company: 目标公司名称（可选）

    Returns:
        生成的报告
    """
    try:
        # Validate file format
        if not is_supported_format(resume_file.filename):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"不支持的文件格式。支持的格式: .pdf, .docx, .txt, .md"
                }
            )

        # Read file content
        logger.info(f"Uploading resume file: {resume_file.filename}")
        file_bytes = await resume_file.read()

        # Parse document
        try:
            resume_text = parse_resume_bytes(file_bytes, resume_file.filename)
            logger.info(f"Successfully parsed resume: {len(resume_text)} characters")
        except DocumentParseError as e:
            logger.error(f"Document parsing failed: {e}")
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": f"简历文件解析失败: {str(e)}"}
            )

        # Validate resume length
        if len(resume_text.strip()) < 50:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"简历内容过短（{len(resume_text.strip())} 字符），请确保文件包含有效的简历内容"
                }
            )

        # Create request
        request = GenerateReportRequest(
            mode=mode,
            target_desc=target_desc,
            domain=domain,
            resume_text=resume_text,
            enable_external_info=enable_external_info,
            target_company=target_company
        )

        return await generate_report(request)

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": f"数据验证失败: {str(e)}"}
        )
    except Exception as e:
        logger.error(f"File upload error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"文件处理失败: {str(e)}"}
        )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "GrillRadar"}


@router.get("/domains")
async def get_domains():
    """获取可用的领域列表（Milestone 3 增强）"""
    return domain_helper.get_domains_list()


@router.get("/domains/{domain}")
async def get_domain_detail(domain: str):
    """获取单个领域的详细信息"""
    detail = domain_helper.get_domain_detail(domain)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")
    return detail


@router.get("/domains-stats")
async def get_domains_stats():
    """获取领域统计信息"""
    return domain_helper.get_domain_summary()


# Milestone 4: External Information Endpoints

from app.sources.external_info_service import external_info_service
from app.models.external_info import ExternalInfoSummary


@router.get("/external-info/search", response_model=ExternalInfoSummary)
async def search_external_info(
    company: Optional[str] = None,
    position: Optional[str] = None,
    domain: Optional[str] = None,
    enable_jd: bool = True,
    enable_interview_exp: bool = True
):
    """
    搜索外部信息（JD和面经）

    Args:
        company: 目标公司（可选）
        position: 目标岗位（可选）
        enable_jd: 是否启用JD检索
        enable_interview_exp: 是否启用面经检索

    Returns:
        外部信息摘要
    """
    summary = external_info_service.retrieve_external_info(
        company=company,
        position=position,
        domain=domain,
        enable_jd=enable_jd,
        enable_interview_exp=enable_interview_exp
    )

    if summary is None:
        raise HTTPException(
            status_code=404,
            detail="No external information found for the given criteria"
        )

    return summary


@router.get("/external-info/preview")
async def preview_external_info(
    company: Optional[str] = None,
    position: Optional[str] = None,
    domain: Optional[str] = None,
):
    """
    预览外部信息（返回文本摘要）

    Args:
        company: 目标公司（可选）
        position: 目标岗位（可选）

    Returns:
        格式化的文本摘要
    """
    summary = external_info_service.retrieve_external_info(
        company=company,
        position=position,
        domain=domain,
        enable_jd=True,
        enable_interview_exp=True
    )

    if summary is None:
        return {"summary": "未找到相关外部信息"}

    text_summary = summary.get_summary_text()

    return {
        "summary": text_summary,
        "jd_count": len(summary.job_descriptions),
        "experience_count": len(summary.interview_experiences),
        "keywords": summary.aggregated_keywords[:15],
        "keyword_trends": summary.keyword_trends[:10],
        "topic_trends": summary.topic_trends[:10],
    }


@router.get("/external-info/trends")
async def get_external_info_trends(
    company: Optional[str] = None,
    position: Optional[str] = None,
    domain: Optional[str] = None,
):
    """获取最新的高频技能/主题趋势"""

    if company or position or domain:
        summary = external_info_service.retrieve_external_info(
            company=company,
            position=position,
            domain=domain,
            enable_jd=True,
            enable_interview_exp=True,
        )
        if summary is None:
            raise HTTPException(
                status_code=404,
                detail="No external information found for the given criteria",
            )

    payload = external_info_service.get_latest_trends()
    if not payload["keyword_trends"] and not payload["topic_trends"]:
        raise HTTPException(status_code=404, detail="Trend data is not available yet")

    return payload


# Configuration Management Endpoints

@router.post("/config/reload")
async def reload_configuration():
    """
    Reload configuration files (development/debugging)

    Force reload domains.yaml and modes.yaml from disk.
    Useful for development when configs change.

    Returns:
        Status message with reload timestamp
    """
    try:
        config_manager.reload()

        return {
            "status": "success",
            "message": "Configuration reloaded successfully",
            "last_reload": config_manager.last_reload.isoformat() if config_manager.last_reload else None,
            "domains_count": len(config_manager.domains.get('engineering', {})) + len(config_manager.domains.get('research', {})),
            "modes_count": len(config_manager.modes)
        }

    except Exception as e:
        logger.error(f"Failed to reload configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Configuration reload failed: {str(e)}"
        )


@router.get("/config/status")
async def get_configuration_status():
    """
    Get current configuration status

    Returns information about loaded configurations without reloading.

    Returns:
        Configuration status and statistics
    """
    return {
        "status": "ok",
        "last_reload": config_manager.last_reload.isoformat() if config_manager.last_reload else "Not loaded yet",
        "domains": {
            "engineering_count": len(config_manager.domains.get('engineering', {})),
            "research_count": len(config_manager.domains.get('research', {})),
            "total": len(config_manager.domains.get('engineering', {})) + len(config_manager.domains.get('research', {}))
        },
        "modes": {
            "available": list(config_manager.modes.keys()),
            "count": len(config_manager.modes)
        }
    }


# API Compatibility and Health Check Endpoints

from app.utils.api_compatibility import api_compatibility


@router.get("/api-health")
async def check_api_health():
    """
    Check API provider health status

    Returns:
        API health status including provider info and configuration
    """
    health_status = await api_compatibility.check_api_health()
    return health_status


@router.get("/api-info")
async def get_api_provider_info():
    """
    Get detailed information about current API provider

    Returns:
        Provider information including capabilities and models
    """
    provider_info = api_compatibility.get_provider_info()
    return provider_info


@router.get("/api-compare")
async def compare_api_providers():
    """
    Compare different API providers

    Returns:
        Comparison of available providers with strengths and use cases
    """
    comparison = api_compatibility.compare_providers()
    return comparison


@router.get("/api-validate")
async def validate_api_configuration():
    """
    Validate current API configuration

    Returns:
        Validation result with detailed error messages if invalid
    """
    is_valid, message = api_compatibility.validate_api_configuration()

    return {
        "valid": is_valid,
        "message": message,
        "provider": settings.DEFAULT_LLM_PROVIDER,
        "model": settings.DEFAULT_MODEL
    }
