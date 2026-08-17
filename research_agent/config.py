"""全局配置：路径、环境变量、默认参数。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录 = 本文件向上两级（research_agent/config.py → research_agent/ → 项目根）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = Path(__file__).resolve().parent

# 优先加载项目根下的 .env；其次用户 home 的 .env
for candidate in (PROJECT_ROOT / ".env", Path.home() / ".research_agent.env"):
    if candidate.is_file():
        load_dotenv(candidate, override=False)
        break


@dataclass(frozen=True)
class ModelConfig:
    """一组 OpenAI 协议兼容的模型配置。"""

    api_key: str
    base_url: str
    model: str

    @property
    def available(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)


@dataclass(frozen=True)
class Settings:
    """框架运行配置。所有路径默认在项目根下。"""

    # ---- 路径 ----
    project_root: Path = PROJECT_ROOT
    data_dir: Path = PROJECT_ROOT / "data"
    sessions_db: Path = PROJECT_ROOT / "data" / "sessions.db"
    checkpoints_db: Path = PROJECT_ROOT / "data" / "checkpoints.db"
    static_dir: Path = PACKAGE_DIR / "static"
    outputs_dir: Path = PROJECT_ROOT / "outputs"
    # 技能目录：项目自带 skills/ + curator 自进化产出 data/skills/ + 可选的用户级 ~/.research_agent/skills
    skills_dirs: tuple[Path, ...] = field(default_factory=tuple)
    memory_file: Path = PROJECT_ROOT / "data" / "memory" / "AGENTS.md"

    # ---- 服务 ----
    host: str = "127.0.0.1"
    port: int = 8321

    # ---- curator ----
    curator_interval: float = 120.0
    curator_max_turns: int = 25

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        for d in self.skills_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
        if not self.memory_file.exists():
            self.memory_file.write_text(
                "# Research Agent 长期记忆\n\n"
                "<!-- 本文件由 curator 自进化进程维护，也可手工编辑。 -->\n",
                encoding="utf-8",
            )


def brain_model() -> ModelConfig:
    """主模型（对话/任务执行）。支持 BRAIN_* 统一变量；兼容 OPENAI_*。"""
    api_key = os.getenv("BRAIN_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("BRAIN_API_URL") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("BRAIN_MODEL_NAME") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ModelConfig(api_key=api_key, base_url=base_url, model=model)


def optimizer_model() -> ModelConfig:
    """curator 自进化用的反思模型，缺省回退到主模型。"""
    cfg = ModelConfig(
        api_key=os.getenv("OPTIMIZER_API_KEY", ""),
        base_url=os.getenv("OPTIMIZER_API_URL", ""),
        model=os.getenv("OPTIMIZER_MODEL_NAME", ""),
    )
    return cfg if cfg.available else brain_model()


def get_settings() -> Settings:
    skills: list[Path] = []
    # 项目自带 skills（用户可编辑扩展）
    builtin = PROJECT_ROOT / "skills"
    if builtin.is_dir():
        skills.append(builtin)
    # curator 自进化产出
    curator_skills = PROJECT_ROOT / "data" / "skills"
    skills.append(curator_skills)
    # 用户级全局 skills（可选）
    user_skills = Path.home() / ".research_agent" / "skills"
    if user_skills.is_dir():
        skills.append(user_skills)
    settings = Settings(skills_dirs=tuple(skills))
    settings.ensure_dirs()
    return settings
