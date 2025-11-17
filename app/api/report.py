"""FastAPI路由：报告生成接口"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field, ValidationError

from app.models.user_config import UserConfig
from app.models.report import Report
from app.core.report_generator import ReportGenerator
from app.utils.markdown import report_to_markdown
from app.utils.domain_helper import domain_helper

logger = logging.getLogger(__name__)

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
    try:
        # 构建UserConfig
        user_config = UserConfig(
            mode=request.mode,
            target_desc=request.target_desc,
            domain=request.domain,
            resume_text=request.resume_text,
            enable_external_info=request.enable_external_info,
            target_company=request.target_company
        )

        # 生成报告
        generator = ReportGenerator()
        report = generator.generate_report(user_config)

        # 导出Markdown
        markdown_content = report_to_markdown(report)

        return GenerateReportResponse(
            success=True,
            report=report,
            markdown=markdown_content
        )

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return GenerateReportResponse(
            success=False,
            error=f"数据验证失败: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
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
    position: Optional[str] = None
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
        "keywords": summary.aggregated_keywords[:15]
    }
