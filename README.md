# Daily Stack

Personal daily ritual app — Stoic reflections, habit tracking, streaks.

## What it does

- **Morning:** Stoic reflection of the day + set your daily focus
- **Evening:** Check off 8 daily habits + write what went well
- **Dashboard:** Streak tracking + 4-week heatmap

## Tech

Single HTML file. No framework, no backend. `localStorage` for persistence.

## Install

```bash
git clone git@github.com:EduardPetraeus/daily-stack.git
cd daily-stack
chmod +x scripts/serve.sh
./scripts/serve.sh
```

Open `http://localhost:8080` in your browser.

## Access from iPhone

1. Run `serve.sh` on your Mac Mini
2. Find your Mac's local IP: `ifconfig en0 | grep inet`
3. On iPhone Safari: `http://<mac-mini-ip>:8080`
4. Add to Home Screen for app-like experience

## License

Private — personal use only.
