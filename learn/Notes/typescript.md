npx tsc script.ts
npx tsc script.ts --watch

open index.html
python3 -m http.server 8000

npx serve .
Since you have Node.js, you can use:

**Option 1: Node.js static server**
```bash
npx serve .
```
Then open `http://localhost:3000`

**Option 2: Node.js http-server**
```bash
npx http-server .
```
Then open `http://localhost:8080`

**Option 3: Python server (still works)**
```bash
python3 -m http.server 8000
```
