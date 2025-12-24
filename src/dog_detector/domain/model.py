from dataclasses import dataclass
from typing import Dict, Any, TypeAlias, Optional
import numpy as np

Frame: TypeAlias = np.ndarray


@dataclass
class DetectionResult:
    dog_on_couch: bool
    confidence: Dict[str, float]
    boxes: Dict[str, Any]
    image_filename: Optional[str] = None
    overlap_ratio: float = 0.0
