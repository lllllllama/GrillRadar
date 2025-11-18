# 陈雨欣 | 计算机视觉 - 图像分割方向

**联系方式**: chenyuxin@email.edu.cn | **GitHub**: github.com/chenyuxin-cv | **Google Scholar**: scholar.google.com/chenyuxin

---

## 教育背景

**上海交通大学** | 计算机科学与技术 | 本科 | 2020.09 - 2024.06
- **GPA**: 3.85/4.0 (专业排名: 5/135)
- **核心课程**:
  - 计算机视觉 (96)
  - 深度学习 (98)
  - 模式识别 (94)
  - 数字图像处理 (97)
  - 机器学习 (95)
  - 凸优化 (92)
- **荣誉**: 国家奖学金 (2022), 校三好学生 (2021, 2022, 2023), 优秀毕业生
- **毕业设计**: Transformer-based Multi-Scale Medical Image Segmentation (优秀毕业设计,评分: 98/100)

---

## 研究经历

### 上海交通大学 视觉与学习实验室 | 本科科研 | 2022.03 - 2024.06

**导师**: 李教授 (CCF A类期刊论文20+篇, Google Scholar引用8000+)

#### 研究项目1: 多尺度医疗影像分割 (2023.06 - 2024.06) ⭐
**研究背景**: 医疗影像分割面临器官尺度差异大(如肝脏vs血管)的挑战,传统CNN难以同时捕获全局结构和细粒度细节。

**我的贡献**:
- **提出新方法**: 设计了一种Hierarchical Multi-Scale Transformer架构(HMS-Former),融合多尺度特征表示
  - 创新点1: 提出Adaptive Scale Fusion模块,动态融合不同分辨率的特征
  - 创新点2: 设计Cross-Scale Attention机制,增强跨尺度信息交互
  - 创新点3: 引入Scale-Aware Loss,指导网络关注不同尺度的目标
- **实验验证**:
  - 在MICCAI 2023 FLARE多器官分割数据集上,相比nnU-Net (baseline)提升**3.8% Dice**, **4.2% HD95**
  - 在Synapse多器官分割数据集上达到**SOTA**: 平均Dice 82.7% (超越之前最好方法1.5%)
  - 消融实验验证每个模块的有效性
- **工程实现**:
  - PyTorch实现,代码规范,完整的训练/测试脚本
  - 使用Mixed Precision Training加速训练,显存占用减少40%
  - 实现多GPU训练 (DDP),支持大batch size
- **论文状态**:
  - **已投稿MICCAI 2024** (under review, 预期结果: 6月公布)
  - 导师评价: "创新性强,实验充分,有望被接收"

#### 研究项目2: 少样本医疗影像分割 (2023.01 - 2023.05)
**研究背景**: 医疗影像标注成本高,少样本学习(Few-Shot Learning)是实际应用的关键。

**我的工作**:
- 复现并改进经典方法(PANet, HSNet, PFENet)
- 提出基于Prototypical Learning的改进方法,引入Uncertainty-Guided Attention
- 在腹部器官分割任务上,1-shot设置下Dice提升2.3%
- 产出课程报告(15页),被评为优秀

#### 研究项目3: 基于SAM的交互式标注工具 (2022.09 - 2022.12)
**研究背景**: Segment Anything Model (SAM)展示了强大的zero-shot分割能力,但缺少医疗场景的适配。

**我的工作**:
- 基于SAM开发医疗影像交互式标注工具
- 实现Point/Box/Scribble多种标注模式
- 在实验室内部使用,标注效率提升**5倍**(从30分钟/张降至6分钟/张)
- 技术栈: Python, PyQt5, SAM, OpenCV
- **代码开源**: github.com/chenyuxin-cv/MedSAM-Annotator (120 stars)

#### 研究项目4: 自监督学习预训练 (2022.06 - 2022.08)
- 探索自监督学习(Self-Supervised Learning)在医疗影像上的应用
- 复现MAE (Masked Autoencoder), SimCLR, MoCo v3
- 在小数据集上,使用自监督预训练模型相比ImageNet预训练,Dice提升1.8%
- 产出实验报告,深入理解对比学习和掩码重建范式

---

## 科研成果

### 论文发表

1. **[Under Review]** **Y. Chen**, X. Li, et al. "HMS-Former: Hierarchical Multi-Scale Transformer for Multi-Organ Segmentation", *MICCAI 2024* (Under Review)
   - 第一作者
   - 提出新颖的多尺度Transformer架构
   - 在两个公开数据集上达到SOTA

2. **[已发表]** Y. Chen, X. Li. "基于元学习的少样本医疗影像分割研究", *中国图象图形学学术会议 (CSIG)*, 2023
   - 第一作者
   - 口头报告(Oral)

### 竞赛获奖

1. **MICCAI 2023 FLARE Challenge** - **第5名/156支队伍** (2023.10)
   - 多器官分割竞赛,13个器官类别
   - 方法: 改进的nnU-Net + 多模型ensemble + 后处理优化
   - 获得Certificate of Achievement

2. **阿里巴巴天池 医疗AI挑战赛** - **第8名** (2023.07)
   - 肺结节检测任务
   - 学习了3D检测算法(如3D U-Net, V-Net)

3. **上海交通大学"挑战杯"** - **一等奖** (2023.05)
   - 基于深度学习的肿瘤分割系统
   - 团队项目,担任技术负责人

### 开源项目

1. **MedSegToolkit** (github.com/chenyuxin-cv/MedSegToolkit)
   - **350+ stars**, 45+ forks
   - 医疗影像分割工具箱,集成20+ SOTA模型
   - 提供预训练模型、训练脚本、评估工具
   - 文档完善,被3篇论文引用

2. **MedSAM-Annotator** (github.com/chenyuxin-cv/MedSAM-Annotator)
   - **120+ stars**
   - 基于SAM的医疗影像标注工具
   - 支持Point/Box/Scribble标注模式

---

## 技术能力

### 编程语言
- **Python**: 精通 (4年经验,主力语言)
- **C++**: 熟练 (课程项目,算法竞赛)
- **MATLAB**: 了解 (图像处理课程)

### 深度学习框架
- **PyTorch**: 精通 (主力框架,2年经验)
  - 熟悉模型定义、训练、调试、部署全流程
  - 理解autograd机制、自定义算子、混合精度训练
  - 多GPU训练(DDP, DataParallel)
- **TensorFlow**: 熟练 (课程项目)
- **JAX**: 了解 (自学中)

### 计算机视觉
- **图像分割**: 精通
  - 经典架构: FCN, U-Net, DeepLab系列, PSPNet
  - Transformer-based: SegFormer, Swin-Unet, Mask2Former, SegNeXt
  - 医疗专用: nnU-Net, TransUNet, MedSAM, UNETR
- **目标检测**: 熟练 (YOLO, Faster R-CNN, RetinaNet)
- **图像分类**: 熟练 (ResNet, ViT, Swin Transformer)
- **生成模型**: 了解 (GAN, Diffusion Models,自学中)

### 专业技术
- **损失函数**: Dice Loss, Focal Loss, Boundary Loss, Hausdorff Distance
- **数据增强**: Spatial (Flip, Rotate, Crop), Intensity (Normalize, Clip), MixUp, CutMix
- **评估指标**: Dice, IoU, Precision, Recall, HD95, ASD
- **模型优化**:
  - 混合精度训练(AMP)
  - 梯度累积
  - 学习率调度(Cosine Annealing, Warm-up)
  - 正则化(Dropout, Weight Decay)
- **后处理**: CRF, Morphological Operations, Connected Components

### 工具与平台
- **开发工具**: Git, Linux, Vim, VS Code, Jupyter
- **实验管理**: Weights & Biases, TensorBoard, MLflow
- **数据处理**: NumPy, Pandas, OpenCV, SimpleITK, MONAI
- **可视化**: Matplotlib, Seaborn, 3D Slicer
- **计算平台**: Slurm集群, Google Colab, Kaggle

---

## 论文阅读

### 精读论文 (50+篇)

**图像分割经典**:
- FCN, U-Net, U-Net++, DeepLab v1-v3+, PSPNet, Mask R-CNN

**Transformer-based分割**:
- ViT, Swin Transformer, SegFormer, Mask2Former, SegNeXt, OneFormer

**医疗影像分割**:
- nnU-Net (重点研读,复现), TransUNet, Swin-Unet, UNETR, MedSAM, SAM

**少样本学习**:
- Prototypical Networks, MAML, Matching Networks, PANet, HSNet, PFENet

**自监督学习**:
- SimCLR, MoCo系列, BYOL, MAE, SimMIM

**多尺度与注意力**:
- FPN, PANet, BiFPN, CBAM, Squeeze-and-Excitation, Non-Local Networks

### 跟进顶会
- **CVPR, ICCV, ECCV** (计算机视觉三大顶会,每届精读15-20篇)
- **MICCAI** (医疗影像顶会,重点关注分割track)
- **NeurIPS, ICLR, ICML** (机器学习,关注Foundation Models, SSL)

### 技术博客
- **知乎专栏**: 《医疗影像分割论文笔记》, 25篇文章, 3万+阅读
- **CSDN博客**: PyTorch代码教程, 10篇文章, 1.5万+阅读

---

## 实习经历

### 商汤科技 | 医疗AI研究实习生 | 2023.07 - 2023.10 (3个月)

**部门**: 医疗影像团队
**导师**: 王博士 (MICCAI领域知名学者)

**工作内容**:
1. **肺结节检测算法优化**:
   - 改进3D U-Net检测算法,召回率提升3.2%
   - 学习了假阳性抑制、多尺度检测等工业界技巧
2. **模型部署**:
   - 学习TensorRT优化,推理速度提升4倍
   - 了解医疗AI产品从研发到临床应用的完整流程
3. **论文阅读与复现**:
   - 复现MICCAI 2023最新方法,撰写技术报告

**收获**:
- 了解工业界医疗AI的技术栈和工程实践
- 学习了模型压缩、量化、部署等知识
- 与资深研究员交流,拓展视野

---

## 课程项目

### 1. 实时语义分割系统 (计算机视觉课程)
- 实现轻量级分割网络(BiSeNet, DDRNet)
- 在Cityscapes数据集上达到75% mIoU, 30 FPS (GTX 1080Ti)
- 应用场景: 自动驾驶
- **成绩**: 课程最高分 (98/100)

### 2. 3D点云分割 (深度学习课程)
- 复现PointNet, PointNet++, PointTransformer
- 在ScanNet数据集上训练室内场景分割模型
- 产出详细实验报告和代码

### 3. 图像生成与编辑 (机器学习课程)
- 实现DCGAN, StyleGAN2生成人脸图像
- 探索潜在空间编辑和属性控制
- 学习了GAN的训练技巧和稳定性优化

---

## 英语能力

- **TOEFL**: 108 (Reading: 30, Listening: 28, Speaking: 24, Writing: 26)
- **GRE**: 330 (Verbal: 160, Quantitative: 170, AW: 4.5)
- 能够流利阅读英文论文、撰写学术论文、进行学术presentation
- 参加国际会议经验 (MICCAI 2023, Poster presentation)

---

## 研究兴趣

### 核心兴趣
1. **医疗影像分割**: CT/MRI多器官分割、病灶检测、3D分割
2. **高效视觉模型**: Lightweight Transformer、模型压缩、边缘设备部署
3. **少样本与域适应**: Few-Shot Learning、Domain Adaptation、Transfer Learning
4. **Foundation Models**: SAM-like模型在医疗领域的应用与改进

### 未来方向
- 探索多模态学习(影像+文本报告)
- 研究可解释性与可信AI
- 关注Diffusion Models在医疗影像生成与分割中的应用

---

## 申请目标

### PhD项目申请
**目标国家/地区**: 美国、英国、香港、新加坡
**研究方向**: Medical Image Analysis, Computer Vision, Deep Learning
**目标学校**:
- **美国**: Stanford (Curtis Langlotz), MIT (Polina Golland), CMU (James Hays), UCSD (Pengtao Xie), JHU (Alan Yuille), UNC (Marc Niethammer)
- **英国**: Oxford (Alison Noble), Imperial College London, UCL
- **香港**: HKU (Qi Dou), CUHK (Pheng-Ann Heng), HKUST
- **新加坡**: NUS, NTU

**期望导师特质**:
- 在医疗影像、计算机视觉领域有深厚积累
- 发表高质量论文(CVPR/ICCV/MICCAI)
- 支持学生探索前沿方向
- 有良好的实验室文化和导师-学生关系

---

## 个人陈述

我对计算机视觉尤其是医疗影像分析充满热情。本科期间,我在李教授实验室进行了2年多的科研训练,从复现论文到提出新方法,从参加竞赛到撰写论文,逐步建立了完整的科研能力。

我提出的HMS-Former方法在多器官分割任务上达到了SOTA,并投稿MICCAI 2024。在MICCAI 2023 FLARE竞赛中获得第5名,验证了我的工程实现能力。我开发的MedSegToolkit开源项目获得350+ stars,展示了代码规范和社区贡献能力。

我有较强的编程能力(PyTorch精通)和数学基础(凸优化、概率论),能够独立完成从idea到实验再到论文撰写的完整科研流程。我阅读了50+篇领域论文,跟进顶会最新进展,保持对前沿技术的敏感度。

我期望在PhD阶段继续深耕医疗影像分析,探索更高效、更鲁棒、更可解释的深度学习方法,推动AI技术在临床中的应用。我希望加入一个重视创新、鼓励探索的实验室,在导师的指导下成长为独立研究者,为学术界和工业界做出贡献。

---

## 推荐信

1. **李教授** (上海交通大学,博士生导师)
   - 本科科研导师,合作2年
   - 了解我的科研能力、创新潜力、学术态度

2. **王博士** (商汤科技,资深研究员)
   - 实习导师
   - 了解我的工程能力、快速学习能力、团队协作

3. **张教授** (上海交通大学,计算机视觉课程教师)
   - 课程成绩优异(98分)
   - 了解我的理论基础和学习能力

---

## 联系方式

- **Email**: chenyuxin@email.edu.cn
- **GitHub**: github.com/chenyuxin-cv
- **Google Scholar**: scholar.google.com/chenyuxin
- **个人主页**: chenyuxin-cv.github.io
- **知乎**: zhihu.com/people/chenyuxin-cv

---

*最后更新: 2024年11月*
