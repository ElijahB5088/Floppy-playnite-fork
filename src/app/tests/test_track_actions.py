from types import SimpleNamespace
from unittest.mock import patch

from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase

from app.models import MediaTypes, Status
from app.track_actions import track_actions

ADD, EDIT = "create", "edit"


class TrackActionsTests(SimpleTestCase):
    """The main button leads with the forward action where the media type has one."""

    def keys(self, media_type, status):
        return [action["key"] for action in track_actions(media_type, status)]

    def test_games_and_board_games_always_lead_with_add_entry(self):
        for media_type in (MediaTypes.GAME.value, MediaTypes.BOARDGAME.value):
            for status in Status.values:
                with self.subTest(media_type=media_type, status=status):
                    self.assertEqual(self.keys(media_type, status), [ADD, EDIT])

    def test_finished_items_lead_with_add_entry(self):
        for media_type in (
            MediaTypes.MOVIE.value,
            MediaTypes.ANIME.value,
            MediaTypes.BOOK.value,
            MediaTypes.COMIC.value,
            MediaTypes.VIDEO.value,
        ):
            with self.subTest(media_type=media_type):
                self.assertEqual(
                    self.keys(media_type, Status.COMPLETED.value),
                    [ADD, EDIT],
                )

    def test_unfinished_items_only_edit(self):
        for status in (
            Status.IN_PROGRESS.value,
            Status.PLANNING.value,
            Status.PAUSED.value,
            Status.DROPPED.value,
        ):
            with self.subTest(status=status):
                self.assertEqual(self.keys(MediaTypes.MOVIE.value, status), [EDIT])

    def test_manga_only_edits(self):
        for status in Status.values:
            with self.subTest(status=status):
                self.assertEqual(self.keys(MediaTypes.MANGA.value, status), [EDIT])


class TrackSplitTemplateTests(SimpleTestCase):
    """One action is a plain button, two a pencil segment, three or more a menu."""

    def render(self, actions, status=Status.COMPLETED.value):
        request = RequestFactory().get("/details/")
        media = {"source": "tmdb", "media_type": "movie", "media_id": "238"}
        with patch("app.track_actions.track_actions", return_value=actions):
            return render_to_string(
                "app/components/detail_track_split.html",
                {
                    "request": request,
                    "media": media,
                    "media_type": "movie",
                    "current_instance": SimpleNamespace(id=7, status=status),
                },
            )

    @staticmethod
    def action(key):
        return {
            "key": key,
            "label": "Add new entry" if key == "create" else "Edit",
            "icon": "plus" if key == "create" else "edit",
        }

    def test_single_action_is_a_plain_edit_button_with_no_menu(self):
        html = self.render([self.action("edit")])
        self.assertIn("Completed", html)
        self.assertNotIn("More tracking actions", html)
        self.assertNotIn("Edit entry,", html)
        self.assertNotIn('x-show="trackMenuOpen"', html)

    def test_two_actions_add_an_icon_only_edit_segment(self):
        html = self.render([self.action("create"), self.action("edit")])
        self.assertIn("Add new entry", html)
        self.assertEqual(html.count('aria-label="Edit entry, Completed"'), 1)
        self.assertIn('title="Edit entry, Completed"', html)
        self.assertNotIn("More tracking actions", html)
        self.assertNotIn('x-show="trackMenuOpen"', html)

    def test_three_actions_open_a_menu(self):
        extra = {"key": "create", "label": "Another action", "icon": "plus"}
        html = self.render([self.action("create"), self.action("edit"), extra])
        self.assertIn('aria-label="More tracking actions"', html)
        self.assertIn(':aria-expanded="trackMenuOpen"', html)
        self.assertIn('@keydown.escape.window="trackMenuOpen = false"', html)
        self.assertIn("Another action", html)
        self.assertNotIn("Edit entry,", html)
