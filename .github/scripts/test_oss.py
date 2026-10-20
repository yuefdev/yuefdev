import unittest
from unittest.mock import patch
from xml.etree import ElementTree

from update_oss import collect, readme_block, replace_block, summarise, chart


def pr(repository, number=1, stars=10, private=False, merged="2026-10-19T12:00:00Z", title="Fix a regression"):
    return {
        "number": number, "title": title, "url": f"https://github.com/{repository}/pull/{number}",
        "mergedAt": merged,
        "repository": {
            "nameWithOwner": repository, "url": f"https://github.com/{repository}",
            "isPrivate": private, "stargazerCount": stars,
            "owner": {"login": repository.split("/")[0]}, "primaryLanguage": {"name": "Rust"},
        },
    }


class OSSTests(unittest.TestCase):
    def setUp(self):
        self.nodes = [
            pr("upstream/small", stars=100),
            pr("upstream/large", stars=100_000),
            pr("upstream/large", number=2, stars=100_000, merged="2026-10-20T12:00:00Z"),
            pr("YuefDev/own"),
            pr("private/secret", private=True),
        ]
        self.data = summarise(self.nodes, "2026-10-20")

    def test_only_public_prs_count_and_major_projects_come_first(self):
        self.assertEqual(self.data["total_merged"], 4)
        self.assertEqual(self.data["upstream_merged"], 3)
        self.assertEqual(self.data["upstream_repositories"], 2)
        self.assertEqual(self.data["repositories"][0]["name"], "upstream/large")
        self.assertEqual(self.data["repositories"][0]["merged"], 2)
        self.assertEqual(self.data["repositories"][0]["latest"]["number"], 2)
        self.assertNotIn("private/secret", str(self.data))

    def test_all_pages_are_collected(self):
        pages = [
            {"totalCount": 2, "nodes": [self.nodes[0]], "pageInfo": {"hasNextPage": True, "endCursor": "next"}},
            {"totalCount": 2, "nodes": [self.nodes[1]], "pageInfo": {"hasNextPage": False, "endCursor": "last"}},
        ]
        with patch("update_oss.fetch_page", side_effect=pages):
            self.assertEqual(collect()["upstream_merged"], 2)

    def test_incomplete_api_data_is_rejected(self):
        page = {"totalCount": 2, "nodes": [self.nodes[0]], "pageInfo": {"hasNextPage": False, "endCursor": "last"}}
        with patch("update_oss.fetch_page", return_value=page):
            with self.assertRaisesRegex(ValueError, "incomplete"):
                collect()

    def test_svg_is_valid_and_escapes_untrusted_titles_in_every_variant(self):
        self.data["repositories"][0]["latest"]["title"] = '<script>alert("x")</script> & fix'
        for theme in ("dark", "light"):
            for mobile in (False, True):
                with self.subTest(theme=theme, mobile=mobile):
                    root = ElementTree.fromstring(chart(self.data, theme, mobile))
                    self.assertEqual(root.get("width"), "640" if mobile else "1200")
                    self.assertFalse(root.findall(".//{http://www.w3.org/2000/svg}script"))
                    self.assertIn("&lt;script&gt;", chart(self.data, theme, mobile))

    def test_readmes_link_to_accepted_external_changes(self):
        for language in ("en", "tr"):
            block = readme_block(self.data, "revision", language)
            self.assertIn("https://github.com/upstream/large/pull/2", block)
            self.assertNotIn("YuefDev/own/pull", block)
            self.assertNotIn("private/secret", block)
            self.assertIn("oss-dark-mobile.svg?v=revision", block)

    def test_only_marked_readme_content_is_replaced(self):
        original = "Keep my intro\n<!-- OSS:START -->\nold\n<!-- OSS:END -->\nKeep my projects\n"
        self.assertEqual(replace_block(original, "new"), original.replace("\nold\n", "\nnew\n"))
        with self.assertRaises(ValueError):
            replace_block("No markers", "new")

    def test_no_contributions_does_not_invent_projects(self):
        data = summarise([], "2026-10-20")
        self.assertEqual(data["upstream_merged"], 0)
        self.assertEqual(data["repositories"], [])
        ElementTree.fromstring(chart(data, "dark"))


if __name__ == "__main__":
    unittest.main()
