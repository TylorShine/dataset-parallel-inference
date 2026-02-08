from typing import List, Optional
from pydantic import BaseModel, Field

# ----------------------------------------------------------------------
# Nested models for the rubric tags
# ----------------------------------------------------------------------
class RubricParameters(BaseModel):
    """Parameters used by the rubric verifier."""
    N: Optional[int] = None  # the original JSON had `null` for N

class RubricTags(BaseModel):
    """Tags associated with a rubric criterion."""
    function: str = ""                     # ``function`` field name is highlighted with backticks
    parameters: RubricParameters
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