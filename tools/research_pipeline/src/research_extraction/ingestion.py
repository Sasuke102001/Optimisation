from __future__ import annotations

from pathlib import Path

from markdown_it import MarkdownIt

from research_extraction.config import PipelineConfig
from research_extraction.ids import build_canonical_id
from research_extraction.research_profiles import get_research_source_profile
from research_extraction.schemas import FileMetadata, SemanticSection
from research_extraction.utils import normalize_mojibake, normalize_whitespace


def _build_file_metadata(file_path: Path, research_dir: Path) -> FileMetadata:
    stat = file_path.stat()
    return FileMetadata(
        file=str(file_path),
        relative_file=str(file_path.relative_to(research_dir)),
        filename=file_path.name,
        bytes_size=stat.st_size,
        modified_at=file_path.stat().st_mtime_ns.__str__(),
    )


def iter_markdown_files(research_dir: Path) -> list[Path]:
    return sorted(path for path in research_dir.rglob("*.md") if path.is_file())


def parse_markdown_sections(file_path: Path, research_dir: Path, config: PipelineConfig) -> list[SemanticSection]:
    md = MarkdownIt()
    raw = file_path.read_text(encoding="utf-8", errors="ignore")
    tokens = md.parse(raw)
    file_metadata = _build_file_metadata(file_path, research_dir)
    source_profile = get_research_source_profile(file_metadata.relative_file)

    sections: list[SemanticSection] = []
    heading_path: list[str] = []
    current_title = "Document Root"
    current_level = 0
    buffer: list[str] = []
    order_index = 0

    def flush_section() -> None:
        nonlocal buffer, order_index, current_title, current_level
        text = "\n".join(buffer).strip()
        normalized_text = normalize_mojibake(text)
        if normalize_whitespace(normalized_text) and len(normalize_whitespace(normalized_text)) >= config.section_min_text_length:
            label = f"{file_metadata.relative_file}:{' > '.join(heading_path or [current_title])}:{order_index}"
            sections.append(
                SemanticSection(
                    file=file_metadata.file,
                    relative_file=file_metadata.relative_file,
                    filename=file_metadata.filename,
                    heading_path=list(heading_path),
                    section_title=current_title,
                    raw_text=text,
                    normalized_text=normalized_text,
                    section_id=build_canonical_id("section", label),
                    level=current_level,
                    order_index=order_index,
                    metadata={**file_metadata.model_dump(), "source_profile": source_profile},
                    source_role=str(source_profile["source_role"]),
                    domain_tags=list(source_profile["domain_tags"]),
                    expected_coverage_tags=list(source_profile["expected_coverage_tags"]),
                )
            )
            order_index += 1
        buffer = []

    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.type == "heading_open":
            flush_section()
            level = int(token.tag[1])
            inline_token = tokens[index + 1] if index + 1 < len(tokens) else None
            title = inline_token.content.strip() if inline_token else "Untitled"
            heading_path = heading_path[: level - 1]
            heading_path.append(title)
            current_title = title
            current_level = level
            index += 1
        elif token.type == "inline" and token.content.strip():
            buffer.append(token.content)
        elif token.type in {"fence", "code_block"} and token.content.strip():
            buffer.append(token.content)
        elif token.type == "paragraph_open":
            pass
        elif token.type == "bullet_list_open" or token.type == "ordered_list_open":
            pass
        elif token.type == "list_item_open":
            pass
        elif token.type == "softbreak":
            buffer.append("")
        index += 1

    flush_section()
    return sections


def ingest_research_directory(config: PipelineConfig) -> list[SemanticSection]:
    sections: list[SemanticSection] = []
    for file_path in iter_markdown_files(config.research_dir):
        sections.extend(parse_markdown_sections(file_path, config.research_dir, config))
    return sections
