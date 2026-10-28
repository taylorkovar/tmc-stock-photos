# TMC Stock Photos

Real stock photos from Pixabay for Content Mill graphics (The Money Couple). The Build Graphics robot asks for photos here, picks one, and imports it into Canva. No AI images.

## How it works
1. The robot adds a request file `queue/px_<name>.json`, for example `{"query": "gas pump price", "count": 6, "orientation": "vertical"}`.
2. That starts the **Fetch Pixabay photos** job. It searches Pixabay with the key stored as a secret, skips anything tagged as AI-made or not a real photo, saves the top results as `pixabay/px_<name>/1.jpg, 2.jpg ...` with `results.json`, and deletes the request.
3. The robot looks at the photos, picks one, and imports it into Canva from its raw.githubusercontent.com link.

Pixabay photos are free to use commercially without credit. The API key is never written in this repo.

## One-time setup (a person has to do these two steps)
1. **Add the key:** Settings > Secrets and variables > Actions > New repository secret. Name: `PIXABAY_API_KEY`. Value: the Pixabay API key. Save.
2. **Turn the job on:** open `setup/pixabay.yml`, copy all of it, then Add file > Create new file, name it `.github/workflows/pixabay.yml`, paste, and commit to `main`.

## Test it
Actions > Fetch Pixabay photos > Run workflow (with a request in `queue/`), then check `pixabay/`.
