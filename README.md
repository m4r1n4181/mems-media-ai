# MEMS — marketing campaigns with AI influencer matching

MEMS is a web app for a marketing agency. A marketing manager creates a **campaign** for a client **brand**,
with a budget and a brief. Inside the campaign the team plans **ads** on different platforms and works through
**tasks** and approvals.

On top of that the app adds **influencer marketing**:

1. **Find creators.** A recommendation model ranks Instagram creators for the campaign's brand. The manager can
   filter the list by audience size and niche. Each suggestion says *why* it was picked (for example "mentioned the
   brand 7 times without being paid" or "brands similar to this one have worked with this creator").
2. **Pick.** The manager selects the creators worth contacting and dismisses the rest. Dismissed and contacted
   creators are not suggested again.
3. **Write the e-mail with AI.** An LLM drafts a collaboration offer from facts the app holds: brand, campaign,
   brief, the creator's niche and the reasons above. The draft is checked automatically (no invented numbers,
   prices or @handles; it must name the brand and the campaign) and falls back to a template when the model is
   unavailable. The manager edits the draft and sends it.
4. **Track replies.** Each creator moves through *Suggested → Selected → Contacted → Accepted / Declined*, and
   every sent e-mail is stored with the campaign.

Influencers are not users of the app; they are contacted by e-mail.

## Repository

| folder | what it is |
|---|---|
| `MusicEventManagementSystem/MusicEventManagementSystem.API` | ASP.NET Core 8 Web API, EF Core + PostgreSQL |
| `MusicEventManagementSystem/MusicEventManagementSystem.Client` | React 19 + Vite + Tailwind front end |
| `ml/` | research: data preparation, baselines, two-stage recommender, experiments ([ml/README.md](ml/README.md)) |
| `ml-service/` | FastAPI service: serves the recommendations, drafts the e-mails ([ml-service/README.md](ml-service/README.md)) |

```
React client ──► .NET API ──► PostgreSQL
                    │
                    └──► ml-service (FastAPI) ──► precomputed rankings (parquet)
                                     └──────────► LLM (Ollama / OpenAI-compatible / Claude)
```

## The recommender in one paragraph

Two stages, trained on a public research dataset of Instagram sponsored posts (2017–2019; creators are
pseudonymized and no personal data is stored in this repository). **Candidate generation** collects about
1,500 creators per brand from organic brand mentions, brand-to-brand similarity (item-kNN), the brand's niche,
SVD embeddings and a LightGCN graph model. A **LightGBM LambdaRank** model then orders them using about 40
features. On a held-out future period the model finds **27.6% of the brand's real new partners in its top 50**
(Recall@50), against 21.4% for the best simple heuristic (+29%). The experiment log is in
[ml/EXPERIMENTS.md](ml/EXPERIMENTS.md). Rankings are computed offline, so the app never waits for the model.

## Running locally

Prerequisites: .NET 8 SDK, Node 20+, PostgreSQL, Python 3.11+, and optionally [Ollama](https://ollama.com)
for AI-written e-mails.

1. **Model data.** `ml-service/data/` (four files) is not in git. Generate it with
   `python ml/scripts/export_service.py`, or copy it from someone who has it.
2. **ML service.**
   ```bash
   cd ml-service
   python -m venv .venv
   .venv/Scripts/python -m pip install -r requirements.txt     # Linux/macOS: .venv/bin/python
   ```
3. **LLM (optional).** Install Ollama, then `ollama pull qwen2.5:7b`. Without it, e-mails use the template.
4. **Database.** Set the connection string in `appsettings.Development.json` (or user secrets). On start the API
   applies migrations and seeds the client brands.
5. **Run everything.** In VS Code, *Run and Debug* → **MEMS: API + Client + ML service**.
   Or start the three parts by hand: `dotnet run` in the API folder, `npm run dev` in the client folder, and
   `.venv/Scripts/python -m uvicorn app.main:app --port 8000` in `ml-service`.

### Where do the e-mails go?

By default nothing leaves your machine: each sent e-mail is written as an `.eml` file to `sent-emails/` in the API
folder (open it with any mail client). To see them in a web inbox, run
[Mailpit](https://mailpit.axllent.org) and set `Email:Mode` to `smtp` (default SMTP: `localhost:1025`).
Demo creator addresses use the reserved domain `creators.example.com`, so they can never reach a real person.

## Data and privacy

The creator dataset is licensed for research only and is **not** included. Creators are identified by a salted
hash (`c_…`), and names, captions and other personal fields are removed before anything reaches the app.

## Origin

MEMS began as a team project (Music Event Management System) with ticket sales, event organization, artist
communication and media campaign modules. This fork keeps the media campaign module and turns it into a
marketing agency tool with ML and LLM features; the other modules are still in the code base but no longer
routed in the UI.
