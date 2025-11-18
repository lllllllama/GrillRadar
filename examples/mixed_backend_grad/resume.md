# 刘浩然 | 后端开发 & 分布式系统研究

**联系方式**: liuhaoran@email.edu.cn | **GitHub**: github.com/liuhaoran-sys | **Scholar**: scholar.google.com/liuhaoran

---

## 教育背景

**北京大学** | 计算机科学与技术 | 本科 | 2020.09 - 2024.06
- **GPA**: 3.75/4.0 (专业排名: 12/150)
- **核心课程**: 分布式系统(96), 操作系统(95), 计算机网络(94), 数据库系统(93), 算法设计(97)
- **荣誉**: 北京大学三好学生(2022), 优秀学生干部(2023), 优秀毕业生
- **毕业设计**: 基于Raft的分布式键值存储系统 (优秀毕业设计,98分)

---

## 工作经历

### 字节跳动 | 后端开发工程师(校招) | 2024.07 - 至今 (5个月)

**团队**: 抖音推荐后端 - 在线服务(Serving)组

#### 项目1: 推荐系统在线特征服务优化 (2024.09 - 至今)
- **背景**: 推荐系统需要实时获取用户/物品特征,原有服务在高峰期延迟高(p99 150ms),影响用户体验
- **负责工作**:
  * 分析性能瓶颈,发现Redis热key和慢查询问题
  * 设计二级缓存架构(本地缓存+Redis),热key命中率提升至95%
  * 优化数据库查询,引入批量查询和连接池复用
  * 实现优雅降级策略,服务不可用时返回默认特征
- **技术栈**: Go, Redis, MySQL, gRPC, Prometheus
- **成果**: p99延迟降至60ms,QPS提升40%,服务可用性从99.5%提升至99.95%

#### 项目2: 分布式配置中心迁移 (2024.07 - 2024.08)
- **背景**: 团队使用老旧的配置中心,功能不足,稳定性差
- **工作内容**:
  * 调研Nacos、Apollo、Consul等方案,最终选型Apollo
  * 设计平滑迁移方案,避免业务中断
  * 实现配置版本管理和灰度发布
  * 编写迁移文档和最佳实践
- **成果**: 成功迁移20+微服务,配置变更时间从30分钟降至5分钟

---

## 研究经历

### 北京大学 系统与网络实验室 | 本科科研 | 2022.09 - 2024.06

**导师**: 王教授 (CCF杰出会员,SOSP/OSDI论文10+篇)

#### 研究项目1: 分布式事务性能优化 (2023.06 - 2024.06) ⭐
**研究背景**: 分布式事务(如2PC, Percolator)在跨分片场景下延迟高,成为系统瓶颈。

**我的贡献**:
- **提出新方法**: 设计了一种基于依赖图(Dependency Graph)的并发控制协议 **DepCC**
  - 核心思想: 将事务间依赖关系显式建模为DAG,通过拓扑排序确定提交顺序
  - 创新点1: 去中心化设计,无需全局协调者,避免单点瓶颈
  - 创新点2: 乐观并发控制,减少锁等待时间
  - 创新点3: 自适应冲突检测,根据负载动态调整策略
- **实验验证**:
  - 在YCSB基准测试上,相比2PC延迟降低**35%**,吞吐量提升**28%**
  - 在TPC-C基准测试上,高冲突场景下性能提升**40%**
  - 实现原型系统(基于Go + etcd),代码5000+行
- **论文状态**:
  - **已投稿SOSP 2024** (under review, 6月结果)
  - 导师评价: "工作扎实,有创新性,但SOSP竞争激烈,也准备投OSDI 2025作为backup"

#### 研究项目2: Raft协议优化 (2023.01 - 2023.05)
**研究背景**: Raft在地理分布式场景下,跨地域日志复制延迟高。

**我的工作**:
- 复现Raft论文,深入理解Leader选举、日志复制、安全性保证
- 提出基于**Pipeline**的日志复制优化,重叠网络传输和持久化
- 在3个数据中心的部署中,跨地域写入延迟降低**20%**
- 产出课程报告和技术博客,被1000+人阅读

#### 研究项目3: 分布式键值存储系统实现 (2022.09 - 2022.12)
- 基于Raft实现分布式KV存储系统(类似etcd)
- 实现Snapshot、日志压缩、动态成员变更
- 通过MIT 6.824 Lab测试(3000+次测试用例)
- 技术栈: Go, gRPC, BoltDB
- **代码开源**: github.com/liuhaoran-sys/raft-kv (200+ stars)

---

## 科研成果

### 论文

1. **[Under Review]** **H. Liu**, X. Wang, et al. "DepCC: Dependency-Graph Based Concurrency Control for Distributed Transactions", *SOSP 2024* (Under Review)
   - 第一作者
   - 提出新的分布式事务并发控制协议
   - 在多个benchmark上验证性能提升

2. **[技术报告]** H. Liu. "Pipelined Log Replication in Geo-Distributed Raft", *北京大学本科生论坛*, 2023
   - 口头报告

### 竞赛

1. **字节跳动"青训营"后端专场** - **一等奖** (2023.08)
   - 实现高性能RPC框架,支持多种序列化协议和负载均衡
   - 团队项目,担任技术负责人

2. **阿里云"飞天计划"云原生挑战赛** - **优秀奖** (2023.06)
   - Kubernetes应用性能优化

### 开源项目

1. **raft-kv** (github.com/liuhaoran-sys/raft-kv)
   - **200+ stars**, 30+ forks
   - 基于Raft的分布式键值存储系统
   - 通过MIT 6.824测试,代码规范,文档完善

2. **DepCC-Prototype** (github.com/liuhaoran-sys/depcc)
   - **80+ stars**
   - SOSP投稿论文的原型实现
   - Go实现,5000+行代码

---

## 技术能力

### 编程语言
- **Go**: 精通 (2年经验,工作和科研主力语言)
- **C/C++**: 熟练 (系统编程,性能优化)
- **Python**: 熟练 (脚本,数据分析)
- **Java**: 了解 (课程项目)

### 后端开发
- **微服务框架**: Go-Micro, Kitex (字节自研), gRPC
- **Web框架**: Gin, Echo, Fiber
- **数据库**: MySQL (索引优化,事务隔离), PostgreSQL, MongoDB
- **缓存**: Redis (数据结构,持久化,集群), Memcached
- **消息队列**: Kafka, RabbitMQ, Pulsar
- **搜索引擎**: Elasticsearch
- **RPC**: gRPC, Thrift, Protocol Buffers

### 分布式系统
- **一致性协议**: Raft, Paxos, 2PC, 3PC, Percolator
- **分布式事务**: ACID, 最终一致性, Saga模式
- **CAP理论**: 理解trade-off,设计系统
- **分布式存储**: etcd, ZooKeeper, TiKV
- **服务治理**: 服务发现(Consul, Nacos), 负载均衡, 熔断降级

### 云原生
- **容器**: Docker (镜像构建,网络,存储)
- **编排**: Kubernetes (Pod, Service, Deployment, ConfigMap)
- **服务网格**: Istio (了解,学习中)
- **CI/CD**: GitLab CI, Jenkins, ArgoCD

### 工程能力
- **监控**: Prometheus, Grafana, Jaeger (分布式追踪)
- **日志**: ELK Stack, Loki
- **性能分析**: pprof, Flame Graph, perf
- **压测**: wrk, Apache Bench, Locust
- **版本管理**: Git (熟练使用,参与code review)

---

## 论文阅读

### 精读论文 (40+篇)

**分布式系统经典**:
- MapReduce, GFS, Bigtable (Google三驾马车)
- Raft, Paxos, ZAB, Viewstamped Replication
- Spanner, CockroachDB, TiDB

**分布式事务**:
- Percolator, Calvin, TAPIR, Occult, Sundial, 2PL, MVCC

**存储系统**:
- LevelDB, RocksDB, LSM-Tree, B+Tree
- Ceph, HDFS

**一致性与共识**:
- FLP不可能性, CAP定理, Linearizability

### 跟进顶会
- **SOSP, OSDI** (系统顶会,重点关注)
- **NSDI, ATC** (网络和系统)
- **EuroSys, SIGMOD** (欧洲系统,数据库)

### 技术博客
- **知乎专栏**: 《分布式系统笔记》, 20篇文章, 5万+阅读
- **个人博客**: MIT 6.824实验详解, Raft源码分析

---

## 实习经历

### 腾讯 | 后端开发实习生 | 2023.06 - 2023.09 (3个月)

**团队**: 微信后台 - 存储组

**工作内容**:
1. **分布式存储系统监控优化**:
   - 开发Prometheus exporter,导出存储系统指标
   - 设计Grafana Dashboard,可视化集群状态
   - 实现告警规则,及时发现异常
2. **性能测试与调优**:
   - 使用YCSB压测存储系统,发现性能瓶颈
   - 优化RocksDB配置(如Block Cache, Compaction策略)
   - 写入吞吐量提升15%
3. **学习收获**:
   - 了解工业界分布式存储的架构和运维
   - 学习了性能调优、监控、故障处理

---

## 课程项目

### 1. 分布式文件系统 (分布式系统课程)
- 实现类似GFS的分布式文件系统
- 支持大文件存储、副本复制、容错恢复
- **成绩**: 课程最高分 (98/100)

### 2. 高性能Web服务器 (操作系统课程)
- 使用C++实现高并发Web服务器
- 使用epoll实现IO多路复用,线程池处理请求
- 支持HTTP/1.1, Keep-Alive, 静态文件服务
- QPS达到10万+ (单机)

### 3. 数据库管理系统 (数据库课程)
- 实现简化版关系数据库(类似SQLite)
- 支持SQL解析、查询优化、B+树索引、事务(2PL)
- 产出详细设计文档和代码

---

## 英语能力

- **TOEFL**: 102 (Reading: 28, Listening: 27, Speaking: 23, Writing: 24)
- **GRE**: 325 (Verbal: 155, Quantitative: 170, AW: 4.0)
- 能够流利阅读英文论文和技术文档,参与国际会议
- 技术博客中英文均有

---

## 兴趣与规划

### 研究兴趣
- 分布式一致性与共识协议
- 分布式事务处理
- 分布式存储系统
- 云原生与边缘计算

### 职业规划 (两条路径)

**路径A: 工业界深耕** (当前优先)
- 在字节跳动积累2-3年工程经验
- 深入学习推荐系统/基础架构
- 晋升为高级后端工程师/技术专家
- 长期在大厂从事基础架构研发

**路径B: 学术研究** (备选/长期目标)
- 如果SOSP论文被接收,考虑申请PhD
- 目标: 美国/香港/新加坡 系统方向PhD
- 研究方向: 分布式系统、数据库、云计算
- 毕业后可选择学术界或工业界研究岗

**当前策略**: 先在工业界锻炼,积累经验,同时关注学术进展。如果论文发表顺利且对学术仍有热情,未来2-3年内可能申请PhD。

---

## 申请意向

### 工程岗位 (当前主要方向)
**期望岗位**: 后端开发工程师 / 基础架构工程师 / 分布式系统工程师
**期望公司**: 字节跳动(当前), 阿里巴巴, 腾讯, 美团, 百度 (基础架构/存储/中间件团队)
**期望城市**: 北京 / 深圳 / 杭州
**到岗时间**: 已入职字节跳动,当前简历仅用于内部转岗或未来跳槽参考

### PhD申请 (备选方向,视论文发表情况)
**申请时间**: 2025年秋季或2026年秋季 (视SOSP论文结果)
**研究方向**: Distributed Systems, Database Systems, Cloud Computing
**目标学校**:
- **美国**: MIT (PDOS), Stanford (Platform Lab), CMU (PDL), UC Berkeley (RISELab), UCSD, Wisconsin-Madison
- **香港**: HKUST (魏星达), HKU, CUHK
- **新加坡**: NUS, NTU
**期望导师**: 在分布式系统、数据库、云计算领域有深入研究的教授

---

## 个人陈述

我是一名对分布式系统充满热情的工程师和研究者。本科期间,我在北大系统实验室进行了2年科研训练,提出的DepCC分布式事务协议投稿SOSP 2024。同时,我在腾讯和字节跳动实习/工作,积累了工业界系统研发经验。

我既喜欢工程的务实(解决实际业务问题,优化性能),也享受科研的探索(提出新方法,发表论文)。我认为工程和科研是相辅相成的:工程经验帮助我发现real problem,科研训练提升我的系统性思考。

当前,我选择先在工业界深耕,积累大规模系统研发经验。但我对学术仍保持开放态度,如果SOSP论文被接收,我会认真考虑PhD申请,在学术界继续探索分布式系统的前沿问题。

无论选择哪条路径,我的目标都是成为分布式系统领域的专家,为学术界或工业界做出有影响力的贡献。

---

## 联系方式

- **Email**: liuhaoran@email.edu.cn (个人), liuhaoran@bytedance.com (工作)
- **GitHub**: github.com/liuhaoran-sys
- **Google Scholar**: scholar.google.com/liuhaoran
- **知乎**: zhihu.com/people/liuhaoran-sys
- **个人博客**: liuhaoran-sys.github.io

---

*最后更新: 2024年11月*
