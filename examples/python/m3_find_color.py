"""Find the first near-#123456 screen pixel through Host accessibility."""

from autojs6 import images, result


target = "#123456"
match = images.find_color(target, threshold=2)

result.set(
    {
        "color": target,
        "match": None if match is None else list(match),
    }
)
