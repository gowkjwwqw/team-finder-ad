from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

AVATAR_FONT_PATH = BASE_DIR / "assets" / "fonts" / "DejaVuSans-Bold.ttf"
AVATAR_SIZE = (200, 200)
DEFAULT_AVATAR_LETTER = "U"
AVATAR_FONT_SIZE = 100
AVATAR_TEXT_Y_OFFSET = 10
DEFAULT_AVATAR_FILENAME_TEMPLATE = "default_avatar_{email}.png"
AVATAR_BACKGROUND_COLORS = (
    "#A98C7A",
    "#7B8FA1",
    "#8F7A66",
    "#6A8E7F",
    "#9A7AB0",
)


PAGINATE_BY = 12

OWNERS_OF_FAVORITE_PROJECTS = "owners-of-favorite-projects"
OWNERS_OF_PARTICIPATING_PROJECTS = "owners-of-participating-projects"
INTERESTED_IN_MY_PROJECTS = "interested-in-my-projects"
PARTICIPANTS_OF_MY_PROJECTS = "participants-of-my-projects"

FILTER_CHOICES = (
    (OWNERS_OF_FAVORITE_PROJECTS, "Авторы избранных проектов"),
    (OWNERS_OF_PARTICIPATING_PROJECTS, "Авторы проектов, в которых я участвую"),
    (INTERESTED_IN_MY_PROJECTS, "Пользователи, которым нравятся мои проекты"),
    (PARTICIPANTS_OF_MY_PROJECTS, "Участники моих проектов"),
)

USER_NAME_MAX_LENGTH = 124
USER_PHONE_MAX_LENGTH = 12
USER_ABOUT_MAX_LENGTH = 256

PHONE_REGEX = r"(8\d{10}|\+7\d{10})"
