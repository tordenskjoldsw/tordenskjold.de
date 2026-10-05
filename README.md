# tordenskjold.de

My personal website: the open-source software I build for the devices I
use every day, and a devlog about it.

Server-rendered with FastAPI and Jinja2. No client-side JavaScript, no
cookies, no tracking, no third-party requests.

## Development

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv sync          # install dependencies
make dev         # local server on http://localhost:8000
make verify      # format check, lint, type check and tests
```

Settings come from environment variables or a local `.env` file; see
`.env.example`.

## Content

Projects live in `content/projects/`, devlog entries in `content/devlog/`,
one Markdown file with YAML front matter each. Content is validated at
startup, so a broken file stops the server with a clear error instead of
breaking a page.

## License

The code is licensed under the [MIT License](LICENSE). Words and images
(everything in `content/` and `src/portfolio/static/img/`) are licensed
under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

The fonts [Inter](https://github.com/rsms/inter) and
[JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) are licensed
under the SIL Open Font License 1.1; the license texts ship next to the
font files. The GitHub icon is from
[Primer Octicons](https://github.com/primer/octicons) (MIT).
