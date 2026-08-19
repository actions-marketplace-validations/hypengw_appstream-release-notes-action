import unittest

from appstream_release_notes import ReleaseNotesError, extract_release_notes


class ExtractReleaseNotesTests(unittest.TestCase):
    def test_extracts_fragment_and_normalizes_tag_version(self) -> None:
        xml = """
        <release version="2.0.0" date="2026-01-01">
          <description>
            <p>Added:</p>
            <ul>
              <li>First feature.</li>
              <li>Second <code>feature</code>.</li>
            </ul>
            <p>Standalone note.</p>
          </description>
        </release>
        <release version="1.0.0" date="2025-01-01">
          <description><p>Old release.</p></description>
        </release>
        """

        self.assertEqual(
            extract_release_notes("v2.0.0", xml),
            "### Added\n\n- First feature.\n- Second feature.\n\n- Standalone note.",
        )

    def test_reads_complete_appstream_document(self) -> None:
        xml = """
        <component type="desktop-application">
          <releases>
            <release version="3.0.0">
              <description>
                <p>Fixes:</p>
                <ol><li>One.</li><li>Two.</li></ol>
              </description>
            </release>
          </releases>
        </component>
        """

        self.assertEqual(
            extract_release_notes("3.0.0", xml),
            "### Fixes\n\n1. One.\n2. Two.",
        )

    def test_uses_existing_release_fallback_for_empty_description(self) -> None:
        xml = '<releases><release version="1.2.3" /></releases>'
        self.assertEqual(extract_release_notes("1.2.3", xml), "Release 1.2.3.")

    def test_missing_version_is_an_error(self) -> None:
        xml = '<releases><release version="1.2.3" /></releases>'
        with self.assertRaisesRegex(
            ReleaseNotesError, "release 2.0.0 was not found; available versions: 1.2.3"
        ):
            extract_release_notes("2.0.0", xml)

    def test_malformed_xml_is_an_error(self) -> None:
        with self.assertRaisesRegex(ReleaseNotesError, "could not parse AppStream XML"):
            extract_release_notes("1.0.0", "<release>")


if __name__ == "__main__":
    unittest.main()
