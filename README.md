# aldiruli.com

Personal portfolio website with interactive Iron Man reveal effect.

## Deploy to Vercel

1. Push this repo to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project" → Import your GitHub repo
4. Vercel auto-detects Vite - just click Deploy
5. Add your domain in Project Settings → Domains → Add `aldiruli.com`
6. Update your GoDaddy DNS:
   - Add A record: `@` → `76.76.21.21`
   - Add CNAME: `www` → `cname.vercel-dns.com`

## Local Development

```bash
npm install
npm run dev
```

## Built with
- React 18
- Vite 5
- Custom cursor blob reveal effect
