from typing import List, Optional, Any
from pydantic import BaseModel, Field

# ----------------------------------------------------------------------
# Nested models for the rubric tags
# ----------------------------------------------------------------------
class RubricParameters(BaseModel):
    """Parameters used by the rubric verifier."""
    N: Optional[int] = None  # the original JSON had `null` for N
    capital_frequency: Optional[Any] = None
    capital_relation: Optional[Any] = None
    end_phrase: Optional[Any] = None
    first_word: Optional[Any] = None
    forbidden_words: Optional[Any] = None
    frequency: Optional[Any] = None
    keyword: Optional[Any] = None
    keyword1: Optional[Any] = None
    keyword2: Optional[Any] = None
    keywords: Optional[Any] = None
    language: Optional[Any] = None
    last_word: Optional[Any] = None
    let_frequency: Optional[Any] = None
    let_relation: Optional[Any] = None
    letter: Optional[Any] = None
    m: Optional[Any] = None
    n: Optional[Any] = None
    n_end: Optional[Any] = None
    n_sent: Optional[Any] = None
    n_start: Optional[Any] = None
    n_words: Optional[Any] = None
    nth_paragraph: Optional[Any] = None
    num_bullets: Optional[Any] = None
    num_highlights: Optional[Any] = None
    num_paragraphs: Optional[Any] = None
    num_placeholders: Optional[Any] = None
    num_sections: Optional[Any] = None
    num_sentences: Optional[Any] = None
    num_words: Optional[Any] = None
    phrase: Optional[Any] = None
    postscript_marker: Optional[Any] = None
    prompt_to_repeat: Optional[Any] = None
    relation: Optional[Any] = None
    section_spliter: Optional[Any] = None
    small_n: Optional[Any] = None

class RubricTags(BaseModel):
    """Tags associated with a rubric criterion."""
    function: str = ""                     # ``function`` field name is highlighted with backticks
    parameters: Optional[RubricParameters]
    verifier: str = "llm"

# ----------------------------------------------------------------------
# Individual rubric criterion (each entry in `rubrics` array)
# ----------------------------------------------------------------------
class RubricCriterion(BaseModel):
    """A single rubric criterion with its scoring details."""
    criterion: str
    points: int
    tags: RubricTags

# ----------------------------------------------------------------------
# The rubric container itself
# ----------------------------------------------------------------------
class Rubric(BaseModel):
    """Container for a rubric criterion (mirrors the JSON object)."""
    criterion: str
    points: int
    tags: RubricTags

# ----------------------------------------------------------------------
# Reward model definition
# ----------------------------------------------------------------------
class RewardModel(BaseModel):
    """Top-level reward model matching the JSON root `reward_model`."""
    ground_truth: str = Field(default="", description="Empty string in the source JSON")
    rubrics: List[RubricCriterion] = Field(..., description="List of rubric criteria")
    style: str = "rubric"  # kept as‑is from the JSON

# ----------------------------------------------------------------------
# Prompt related models
# ----------------------------------------------------------------------
class PromptItem(BaseModel):
    """An entry inside the `prompt` array."""
    content: str  # example: contains inline math like $2(-6)$
    role: str

class Prompt(BaseModel):
    """Top-level prompt container matching the JSON root `prompt`."""
    prompt: List[PromptItem]

# ----------------------------------------------------------------------
# Root model – combines everything
# ----------------------------------------------------------------------
class RootModel(BaseModel):
    """Overall structure that wraps both `prompt` and `reward_model`."""
    prompt: List[PromptItem]
    reward_model: RewardModel