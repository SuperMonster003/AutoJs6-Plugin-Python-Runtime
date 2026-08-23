"""Find a project-local PNG template in a bounded fresh Host screenshot."""

from pathlib import Path

from autojs6 import images, result


template = Path("fixtures/target.png").read_bytes()
match = images.find_image(
    template,
    region=(0, 200, 1080, 1200),
    threshold=2,
)

result.set(
    {
        "template": "fixtures/target.png",
        "match": None if match is None else list(match),
    }
)
