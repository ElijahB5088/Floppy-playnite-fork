"""Which tracking actions the detail-page split button offers.

The first action is the main button. A second action becomes a small
icon-only segment and three or more open a menu, so adding an action later
needs no template change.
"""

from django.utils.translation import gettext as _

from app.models import MediaTypes, Status

# Every play is its own entry, so adding one is always the forward action.
ALWAYS_ADD_ENTRY = frozenset({MediaTypes.GAME.value, MediaTypes.BOARDGAME.value})
# Once a finished entry exists, the next thing to do is another one.
ADD_ENTRY_WHEN_COMPLETED = frozenset(
    {
        MediaTypes.MOVIE.value,
        MediaTypes.ANIME.value,
        MediaTypes.BOOK.value,
        MediaTypes.COMIC.value,
        MediaTypes.VIDEO.value,
    },
)


def track_actions(media_type, status):
    """Return the ordered actions for a tracked item of this type and status."""
    edit = {"key": "edit", "label": _("Edit"), "icon": "edit"}
    add_entry = {"key": "create", "label": _("Add new entry"), "icon": "plus"}
    if media_type in ALWAYS_ADD_ENTRY or (
        media_type in ADD_ENTRY_WHEN_COMPLETED and status == Status.COMPLETED.value
    ):
        return [add_entry, edit]
    return [edit]
