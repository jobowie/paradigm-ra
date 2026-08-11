# Publish Paradigm Ra now

## Local check

```bash
npm install
npm run dev
```

Open http://localhost:3000.

Then:

```bash
npm run build
```

## GitHub

```bash
git init
git add .
git commit -m "Launch Paradigm Ra production site"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

## Netlify

1. In Netlify, add a new project from Git.
2. Choose GitHub and select the Paradigm Ra repository.
3. Netlify should detect Next.js automatically.
4. Build command: `npm run build`.
5. Deploy.
6. Add the custom domain after the deploy is green.

## Important

Confirm `src/content/site.ts` before launch. The starter contact email is `hello@paradigmra.com`.
