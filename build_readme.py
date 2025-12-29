import feedparser
import pathlib
import re
import ssl
import urllib.request
from datetime import datetime

# Handle SSL certificate issues
ssl._create_default_https_context = ssl._create_unverified_context

root = pathlib.Path(__file__).parent.resolve()


def replace_chunk(content, marker, chunk, inline=False):
    """Replace content between marker comments."""
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


def fetch_blog_entries():
    """Fetch blog entries from RSS feed."""
    feed = feedparser.parse("https://vinitkumar.me/rss.xml")
    entries = []
    
    for entry in feed.entries:
        # Parse the publication date
        published = entry.get("published", "")
        if published:
            try:
                # Parse RSS date format
                dt = datetime(*entry.published_parsed[:6])
                published_str = dt.strftime("%Y-%m-%d")
            except (AttributeError, TypeError):
                published_str = published.split("T")[0] if "T" in published else published
        else:
            published_str = ""
        
        entries.append({
            "title": entry.get("title", "Untitled"),
            "url": entry.get("link", "").split("#")[0],
            "published": published_str,
        })
    
    return entries


def fetch_til_entries():
    """Fetch TIL entries from RSS feed (filtering by /til/ in URL)."""
    feed = feedparser.parse("https://vinitkumar.me/rss.xml")
    entries = []
    
    for entry in feed.entries:
        url = entry.get("link", "")
        # Filter for TIL posts (URLs containing /til/)
        if "/til/" not in url.lower():
            continue
            
        published = entry.get("published", "")
        if published:
            try:
                dt = datetime(*entry.published_parsed[:6])
                published_str = dt.strftime("%Y-%m-%d")
            except (AttributeError, TypeError):
                published_str = published.split("T")[0] if "T" in published else published
        else:
            published_str = ""
        
        entries.append({
            "title": entry.get("title", "Untitled"),
            "url": url.split("#")[0],
            "published": published_str,
        })
    
    return entries


def fetch_regular_blog_entries():
    """Fetch regular blog entries (excluding TIL posts)."""
    feed = feedparser.parse("https://vinitkumar.me/rss.xml")
    entries = []
    
    for entry in feed.entries:
        url = entry.get("link", "")
        # Skip TIL posts
        if "/til/" in url.lower():
            continue
            
        published = entry.get("published", "")
        if published:
            try:
                dt = datetime(*entry.published_parsed[:6])
                published_str = dt.strftime("%Y-%m-%d")
            except (AttributeError, TypeError):
                published_str = published.split("T")[0] if "T" in published else published
        else:
            published_str = ""
        
        entries.append({
            "title": entry.get("title", "Untitled"),
            "url": url.split("#")[0],
            "published": published_str,
        })
    
    return entries


if __name__ == "__main__":
    readme = root / "README.md"
    readme_contents = readme.open().read()
    
    # Fetch and update blog entries (excluding TIL)
    blog_entries = fetch_regular_blog_entries()[:5]
    if blog_entries:
        blog_md = "\n".join(
            ["- [{title}]({url}) - {published}".format(**entry) for entry in blog_entries]
        )
        readme_contents = replace_chunk(readme_contents, "blog", blog_md)
        print(f"Updated {len(blog_entries)} blog entries")
    
    # Fetch and update TIL entries
    til_entries = fetch_til_entries()[:5]
    if til_entries:
        til_md = "\n".join(
            ["- [{title}]({url}) - {published}".format(**entry) for entry in til_entries]
        )
        readme_contents = replace_chunk(readme_contents, "til", til_md)
        print(f"Updated {len(til_entries)} TIL entries")
    
    readme.open("w").write(readme_contents)
    print("README.md updated successfully!")
