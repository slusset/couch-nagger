from dataclasses import dataclass
from typing import Dict, Any, TypeAlias
import numpy as np

Frame: TypeAlias = np.ndarray

@dataclass
class DetectionResult:
    dog_on_couch: bool
    confidence: Dict[str, float]
    boxes: Dict[str, Any]  # Store raw boxes if needed for debugging/visualization
