import io
import random

from PIL import Image, ImageDraw, ImageFont

from .constants import (
    AVATAR_FONT_PATH,
    AVATAR_SIZE,
    AVATAR_BACKGROUND_COLORS,
    DEFAULT_AVATAR_LETTER,
    AVATAR_FONT_SIZE,
    AVATAR_TEXT_Y_OFFSET,
)


def get_avatar_font(size):
    try:
        return ImageFont.truetype(str(AVATAR_FONT_PATH), size)
    except OSError:
        return ImageFont.load_default()


def generate_avatar(name):
    image = Image.new("RGB", AVATAR_SIZE, random.choice(AVATAR_BACKGROUND_COLORS))
    draw = ImageDraw.Draw(image)

    letter = (name[:1] or DEFAULT_AVATAR_LETTER).upper()
    font = get_avatar_font(AVATAR_FONT_SIZE)

    bbox = draw.textbbox((0, 0), letter, font=font)
    t_width = bbox[2] - bbox[0]
    t_height = bbox[3] - bbox[1]

    x = (AVATAR_SIZE[0] - t_width) / 2
    y = (AVATAR_SIZE[1] - t_height) / 2 - AVATAR_TEXT_Y_OFFSET

    draw.text((x, y), letter, fill="white", font=font)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
