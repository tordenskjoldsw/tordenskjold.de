from portfolio.models import SiteContent, SitemapEntry


def sitemap_entries(content: SiteContent) -> tuple[SitemapEntry, ...]:
    entries = [SitemapEntry(path="/")]
    entries += [SitemapEntry(path=f"/projects/{p.slug}") for p in content.projects]
    if content.devlog:
        entries.append(SitemapEntry(path="/devlog", lastmod=content.devlog[0].date))
        entries += [
            SitemapEntry(path=f"/devlog/{entry.slug}", lastmod=entry.date)
            for entry in content.devlog
        ]
    return tuple(entries)
