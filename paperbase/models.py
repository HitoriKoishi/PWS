from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any


@dataclass
class Paper:
    id: int
    title: str
    venue: str
    year: int
    status: str = "reading"
    tags: list[str] = field(default_factory=list)
    summary: str = ""
    innovations: list[str] = field(default_factory=list)
    notes: str = ""
    updated: str = "刚刚更新"
    date: str = field(default_factory=lambda: date.today().isoformat())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Paper":
        return cls(
            id=int(data.get("id", 0)),
            title=str(data.get("title", "未命名论文")),
            venue=str(data.get("venue", "未标注会议")),
            year=int(data.get("year", date.today().year)),
            status=str(data.get("status", "reading")),
            tags=[str(item).strip() for item in data.get("tags", []) if str(item).strip()],
            summary=str(data.get("summary", "")),
            innovations=[str(item).strip() for item in data.get("innovations", []) if str(item).strip()],
            notes=str(data.get("notes", "")),
            updated=str(data.get("updated", "刚刚更新")),
            date=str(data.get("date", date.today().isoformat())),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def search_text(self) -> str:
        return " ".join([self.title, self.venue, self.summary, self.notes, *self.tags]).lower()


def sample_papers() -> list[Paper]:
    return [
        Paper(
            1,
            "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning",
            "arXiv",
            2025,
            "reading",
            ["LLM", "Reasoning"],
            "通过纯强化学习激励大语言模型的推理能力，展示了无需人工标注推理轨迹也可以涌现出强大的长链思考能力。",
            ["提出 GRPO 算法，在不依赖 critic model 的情况下优化策略。", "观察并分析了模型自发涌现的自我验证与反思行为。", "通过多阶段训练，将推理能力有效迁移到通用任务。"],
            "推理时的 token budget 和训练时的奖励设计值得深入对比。可以关注它与 process reward model 的结合方式。",
            "今天 10:24",
            "2026-08-04",
        ),
        Paper(
            2,
            "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection",
            "ICLR",
            2024,
            "read",
            ["RAG", "Evaluation"],
            "Self-RAG 让语言模型学习何时检索、检索什么以及如何评价自己的生成结果，在准确性和事实性之间取得更好的平衡。",
            ["引入 reflection tokens 统一控制检索与自我批评。", "训练模型根据检索结果对生成内容进行自我评价。"],
            "Reflection token 是很有价值的接口设计。后续可以迁移到多轮 Agent 的工具调用决策。",
            "昨天 16:40",
            "2026-08-03",
        ),
        Paper(
            3,
            "The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits",
            "arXiv",
            2024,
            "later",
            ["LLM", "Efficiency"],
            "探索将大语言模型权重压缩到三值 {-1, 0, +1}，在显著降低内存与计算成本的同时保持模型能力。",
            ["提出 1.58-bit 权重表示，让矩阵乘法可以用加法替代。", "讨论了从预训练阶段开始使用三值权重的可行性。"],
            "需要结合实际硬件 benchmark 判断收益。",
            "3 天前",
            "2026-08-01",
        ),
        Paper(
            4,
            "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?",
            "ICLR",
            2024,
            "reading",
            ["Agent", "Evaluation"],
            "一个评估语言模型解决真实 GitHub issue 能力的基准测试，任务包含理解代码库、定位问题与生成可合并的补丁。",
            ["使用真实开源项目 issue，避免了合成任务的评估偏差。", "建立可执行测试驱动的端到端评估流程。"],
            "评测结果高度依赖上下文构造方式，适合作为 Agent 系统的回归测试集。",
            "上周五",
            "2026-07-31",
        ),
    ]
