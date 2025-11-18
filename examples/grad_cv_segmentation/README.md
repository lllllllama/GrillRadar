# 示例2: 计算机视觉PhD申请场景

## 场景描述

**候选人背景**: 陈雨欣,上海交通大学计算机科学本科毕业(GPA 3.85),有2年+本科科研经历,提出HMS-Former方法并投稿MICCAI 2024

**目标**: 美国/香港 计算机视觉方向PhD申请,研究方向为医疗影像分割

**学术特点**:
- 论文投稿: MICCAI 2024 (under review)
- 竞赛成绩: MICCAI FLARE Challenge第5名/156队
- 开源项目: MedSegToolkit (350+ stars)
- 英语能力: TOEFL 108, GRE 330

---

## 如何运行

### 方式1: 使用命令行

```bash
# 从项目根目录运行
python cli.py \
  --config examples/grad_cv_segmentation/config.json \
  --resume examples/grad_cv_segmentation/resume.md \
  --output my_grad_report.md
```

### 方式2: 查看示例报告

直接查看 `sample_report.md` 了解报告输出格式和问题类型。

---

## 文件说明

- `resume.md` - 候选人简历(中文,Markdown格式)
- `config.json` - GrillRadar配置文件
- `sample_report.md` - 生成的示例报告
- `README.md` - 本说明文档

---

## 报告亮点

本报告包含**12个核心拷问问题**,覆盖PhD申请的关键维度:

1. **研究深度** (创新性、实验严谨性、失败经历)
2. **理论基础** (数学推导、Transformer原理、损失函数)
3. **领域认知** (文献综述、研究热点、未来方向)
4. **PhD规划** (Research Proposal、研究独立性)
5. **工程能力** (代码质量、开源项目管理)
6. **学术素养** (英语能力、学术诚信、时间管理)

每个问题都包含:
- 提问理由(为什么导师问这个问题)
- 基准答案框架
- 支撑材料和学习资源
- **可复用的练习提示词**(复制后喂给ChatGPT/Claude进行深度练习)

---

## PhD面试特点

与工程求职面试不同,PhD面试更关注:

- ✅ **研究深度** > 项目数量
- ✅ **创新能力** > 调包能力
- ✅ **理论基础** > 工程技巧
- ✅ **失败经历** > 只报喜
- ✅ **Research Proposal** > 泛泛而谈
- ✅ **学术诚信** > 简历包装

---

## 适用人群

- 计算机视觉PhD申请者
- 医疗影像分析方向研究生
- 有科研经历的本科生
- 准备套磁和面试的申请人

---

[返回examples目录](../)
