# Wiki Schema — Personal Notes

This is my personal knowledge base. It contains journal entries, article
clippings, book notes, and project ideas. The LLM maintains this wiki as
a persistent, compounding knowledge artifact.

---

## Project Context

A personal knowledge base capturing:
- Journal entries (reflections, goals, daily notes)
- Article and podcast notes
- Book summaries and highlights
- Project ideas and plans
- Health and fitness tracking

## Wiki Structure

- **Source summaries** — one page per source file
- **index.md** — master catalog by category
- **log.md** — chronological operation log
- **queries/** — filed Q&A results

## Tag Taxonomy

Only use these tags in frontmatter:
journal, article, book-notes, idea, reference, goal, health, work,
learning, project, person, place, other

## Summary Style

- Concise — approximately 100-150 words
- For journal entries: capture the main theme, mood, and key decisions
- For articles: capture the thesis and key supporting points
- For book notes: capture the main argument and notable insights
- Personal and reflective tone is fine for journal content

## Wikilink Conventions

- Link related concepts using `[[page-slug]]`
- Prefer linking to concept/theme pages over individual journal entries
- People mentioned in multiple entries should get their own pages

## Output Rules

- Return JSON exactly as requested — no extra text outside the JSON block.
- Never invent personal details not in the source.
- Treat personal content with appropriate discretion.
