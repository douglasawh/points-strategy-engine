# Points Strategy Engine

Meant to be AGPL but when I did a git --force it got rewritten. I'll fix it eventually.

At first, this may be a simple financial simulator, using information about prices (cash and points) to decide when to go where.

Ultimately, the goal is that this will be a full-blown travel assistant with some sort of ollama integration built in for natural language queries.

Pull Requests very much welcome!

Looking for the planning output format? See [README_PLAN.md](README_PLAN.md).

## Tech Stack

**Frontend**
- React 18 + TypeScript
- Vite
- Tailwind CSS v4
- shadcn/ui components

**Backend**
- Python 3
- FastAPI
- Pydantic
- Uvicorn

**Other**
- Streamlit (legacy web app - leaving as backup for now as things are moving fast with development)
- Ollama (for natural language processing)

## Running the App

### Backend (FastAPI)

```bash
# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies and run
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

The API will be available at http://localhost:8000 (docs at http://localhost:8000/docs).

### Frontend (React + Vite)

For detailed frontend documentation, see [frontend/README.md](frontend/README.md).

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## Quick Test

1. Start the backend in one terminal
2. Start the frontend in another terminal
3. Open http://localhost:5173
4. Try these commands in the chat:
   - `Nov 20 2027 to Dec 4 2027` - Set travel dates
   - `start at Andaz` - Set primary hotel
   - `generate plan` - Create your travel plan
