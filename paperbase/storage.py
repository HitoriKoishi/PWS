from __future__ import annotations

import json
from pathlib import Path

from .models import Paper, sample_papers


class PaperRepository:
    """负责论文 JSON 文件读写，UI 不直接接触文件系统。"""

    def __init__(self, path: Path):
        self.path = path

    def load(self) -> list[Paper]:
        if not self.path.exists():
            return sample_papers()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                raise ValueError("论文数据必须是列表")
            return [Paper.from_dict(item) for item in payload]
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return sample_papers()

    def save(self, papers: list[Paper]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps([paper.to_dict() for paper in papers], ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(self.path)

    @staticmethod
    def next_id(papers: list[Paper]) -> int:
        return max((paper.id for paper in papers), default=0) + 1
