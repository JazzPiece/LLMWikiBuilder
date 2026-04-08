# Wiki Schema — Research Papers

An academic research knowledge base. The LLM reads papers, extracts key
contributions, and maintains cross-references between related work.

---

## Project Context

A deep-dive research wiki. Sources are academic papers (PDF, Word, Markdown).
The goal is to build a structured understanding of a research area over time,
tracking: methods, results, authors, datasets, and the evolution of ideas.

## Wiki Structure

- **Paper summaries** — one page per paper with structured metadata
- **Concept pages** — synthesized pages for key methods and theories
- **Author pages** — pages for frequently cited researchers
- **index.md** — master catalog
- **log.md** — chronological ingest log

## Tag Taxonomy

Only use these tags:
paper, survey, dataset, method, result, theory, concept, author, venue,
replication, critique, foundational, recent

## Summary Style

For each paper summary, include:
1. **Problem**: What problem does this paper address?
2. **Method**: What approach/technique is proposed?
3. **Results**: Key quantitative or qualitative results
4. **Significance**: Why does this paper matter? What does it change?
5. **Limitations**: Known limitations or open questions

Summaries should be ~200 words.

## Wikilink Conventions

- Link to related papers, methods, datasets, and authors
- Use `[[method-name]]` for established techniques
- Use `[[author-lastname-year]]` style for paper references
- Always add a "Related Work" section

## Output Rules

- Return JSON exactly as requested — no extra text outside the JSON block.
- Be precise about claims — only state what the paper explicitly claims.
- Flag contradictions with other papers in the related_topics field.
