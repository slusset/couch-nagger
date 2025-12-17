# Gemini CLI Context for `couch-nagger`

This file (`GEMINI.md`) provides context and instructions for the Gemini CLI agent working on this repository.

## Project Overview
**Name:** Couch Nagger
**Goal:** Automated system to detect if a specific dog (Fonzy) is on the couch using computer vision (YOLOv8).
**Core Logic:** Detects "dog" and "couch" objects in an image and calculates geometric overlap to determine if the dog is *on* the couch.

## Tech Stack
- **Language:** Python 3.8+
- **Computer Vision:** YOLOv8 (via `ultralytics` package)
- **Testing:** `pytest`
- **Package Management:** `pip`, `setuptools`

## Key Files & Directories
- `src/dog_detector/dog_detector.py`: Main logic class `DogDetector`. Handles model loading and inference.
- `tests/`: Contains unit and integration tests.
    - `tests/test_dog_detector.py`: Main test suite.
    - `tests/debug_detection.py`: Utility for debugging detections visually.
- `images/`: Test images (dog on couch, dog on floor, empty couch, etc.).
- `requirements.txt`: Project dependencies.

## Development Workflow

### Installation
```bash
pip install -r requirements.txt
pip install -e .
```

### Running Tests
Always run tests after making changes to logic.
```bash
pytest tests/
```

### Basic Usage Example
```python
from dog_detector import DogDetector
detector = DogDetector()
result = detector.check_image('path/to/image.jpg')
print(result['dog_on_couch'])
```

## Coding Conventions
- Follow **PEP 8** style guidelines for Python code.
- Ensure all new logic includes unit tests.
- When modifying `DogDetector`, ensure the `check_image` method signature remains compatible or update all call sites.
- **Docstrings:** Use Google-style or NumPy-style docstrings for complex functions.

---

## References for Customizing Gemini CLI (`GEMINI.md`)

The `GEMINI.md` file is a special context file that the Gemini CLI agent looks for in the root of a project. It serves as a "system prompt extension" specific to the repository.

### What to put in `GEMINI.md`?
1.  **Project Identity:** What is this repo? What is its unique purpose?
2.  **Architectural Decisions:** Why were certain frameworks chosen? Are there specific patterns (e.g., "Always use Repository pattern for DB access") that the agent must follow?
3.  **Critical Workflows:** How strictly must tests pass? Are there manual steps usually required?
4.  **Gotchas:** "Don't touch the legacy parser in `lib/old_parser.py`." or "Always run `make clean` before `make build`."
5.  **Style & Tone:** "Prefer concise code over verbose comments" or "Write comments for every function."

### How Gemini uses this file
- **Context Injection:** The contents of this file are often read by the agent at the start of a session or when exploring the codebase.
- **Rule Enforcement:** If you state "Never use library X" here, the agent will attempt to respect that constraint during code generation.
- **Onboarding:** It acts as an automated onboarding document for the AI developer, similar to how `CONTRIBUTING.md` helps human developers.

### Best Practices
- Keep it up-to-date with major architectural changes.
- Be specific. Instead of "Write good code", say "Use type hints for all function arguments."
- Include command aliases or scripts that are specific to your local environment if they differ from standard usage.
