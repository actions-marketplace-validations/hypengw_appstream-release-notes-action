# AppStream Release Notes

Convert an AppStream release description to Markdown for a GitHub release.

## Usage

```yaml
permissions:
  contents: write

steps:
  - uses: actions/checkout@v4

  - id: release-notes
    uses: waywallen/appstream-release-notes-action@v1
    with:
      file: release.xml
      version: ${{ github.ref_name }}

  - uses: softprops/action-gh-release@v2
    with:
      body_path: ${{ steps.release-notes.outputs.path }}
```

The `version` input accepts versions with or without a leading `v`. For
example, `v1.2.0` matches `<release version="1.2.0">`.

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `file` | Yes | | AppStream XML file or release fragment. |
| `version` | Yes | | Release version to select. |
| `output-file` | No | Temporary file | Markdown output path. Relative paths are resolved from the workspace. |

## Outputs

| Output | Description |
| --- | --- |
| `path` | Absolute path to the generated Markdown file. |

## Supported XML

The input may be a complete AppStream component, a `<releases>` document, a
single `<release>`, or multiple sibling `<release>` fragments. Paragraphs and
ordered or unordered lists inside the selected release description are
converted to Markdown.

If the requested version is missing, the action fails and reports the versions
available in the input file.

## Development

Run the unit tests with:

```sh
python3 -m unittest discover -s tests -v
```

## License

[MIT](LICENSE)
