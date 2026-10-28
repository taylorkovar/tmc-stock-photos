"""Search Pixabay for each request in queue/ and save the photos in pixabay/<name>/.

A request is queue/px_<name>.json, for example:
  {"query": "gas pump price", "count": 6, "orientation": "vertical"}
The job writes pixabay/px_<name>/1.jpg ... and pixabay/px_<name>/results.json, then deletes the request.
The API key comes from the PIXABAY_API_KEY repository secret and is never written anywhere.
"""
import glob
import json
import os
import pathlib
import urllib.parse
import urllib.request

KEY = os.environ.get("PIXABAY_API_KEY", "")
UA = {"User-Agent": "Mozilla/5.0 (tmc-stock-photos GitHub Action)"}
# Skip anything tagged as AI-made or not a real photo.
BAD_TAGS = ("ai generated", "ai-generated", "generative", "artificial intelligence", "midjourney",
            "stable diffusion", "dall-e", "3d", "render", "illustration", "digital art", "cartoon")


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


for qfile in sorted(glob.glob("queue/px_*.json")):
    name = pathlib.Path(qfile).stem
    out = pathlib.Path("pixabay") / name
    out.mkdir(parents=True, exist_ok=True)
    try:
        req = json.load(open(qfile))
        count = max(1, min(int(req.get("count", 6)), 10))
        orientation = req.get("orientation", "all")
        if orientation not in ("all", "horizontal", "vertical"):
            orientation = "all"
        if not KEY:
            raise RuntimeError("PIXABAY_API_KEY secret is not set")
        params = {"key": KEY, "q": str(req["query"])[:100], "image_type": "photo", "safesearch": "true",
                  "per_page": 50, "orientation": orientation, "order": "popular"}
        data = json.loads(get("https://pixabay.com/api/?" + urllib.parse.urlencode(params)))
        results = []
        for hit in data.get("hits", []):
            tags = hit.get("tags", "").lower()
            if any(b in tags for b in BAD_TAGS):
                continue
            fn = out / f"{len(results) + 1}.jpg"
            fn.write_bytes(get(hit["largeImageURL"]))
            results.append({"file": str(fn), "pixabay_id": hit["id"], "page": hit["pageURL"], "tags": hit["tags"],
                            "width": hit["imageWidth"], "height": hit["imageHeight"], "photographer": hit["user"]})
            if len(results) >= count:
                break
        status = {"ok": True, "query": req["query"], "total_found": data.get("totalHits", 0), "results": results}
    except Exception as e:  # report the problem without ever printing the key
        msg = str(e).replace(KEY, "***") if KEY else str(e)
        status = {"ok": False, "error": msg[:300]}
    (out / "results.json").write_text(json.dumps(status, indent=2))
    os.remove(qfile)
    print(name, "ok" if status.get("ok") else "error", len(status.get("results", [])))
