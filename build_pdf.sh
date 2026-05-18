#!/usr/bin/env bash
# Build paper.pdf from SURVEY.md.
# Pipeline: preprocess -> pandoc --natbib -> xelatex/bibtex/xelatex x3.
# Three xelatex passes after bibtex are needed for natbib to resolve all
# citations and write back stable label numbers; fewer passes leaves [?]
# placeholders in the rendered PDF.

set -e
cd "$(dirname "$0")"

# 1. Regenerate the build-source markdown (citations + figure swap) from SURVEY.md
python3 - <<'PY'
import re
with open("SURVEY.md") as f:
    text = f.read()

def cite_key(arxid):
    return f"arxiv{arxid.replace('.', '_')}"

# Drop the H1 title (\maketitle handles it) and the existing References appendix
text = re.sub(r"^# A Comprehensive Survey of World Models for Coding\s*\n+", "", text, count=1)
text = re.sub(r"## Appendix A · References.*?(?=## Appendix B)", "", text, flags=re.DOTALL)
text = text.replace("## Appendix B · Glossary", "## Appendix · Glossary")

# Convert inline arxiv IDs into pandoc citation syntax
text = re.sub(r"\((\d{4}\.\d{4,5})\)", lambda m: f"[@{cite_key(m.group(1))}]", text)
text = re.sub(r"ar[Xx]iv:(\d{4}\.\d{4,5})", lambda m: f"[@{cite_key(m.group(1))}]", text)
text = re.sub(r"\barxiv\s+(\d{4}\.\d{4,5})", lambda m: f"[@{cite_key(m.group(1))}]", text)
text = re.sub(r"(?<![@_])\b(\d{4}\.\d{4,5})\b", lambda m: f"[@{cite_key(m.group(1))}]", text)

# Swap the two ASCII fenced diagrams for figure references / hero pointer
ctr = {"n": 0}
def repl(m):
    ctr["n"] += 1
    if ctr["n"] == 1:
        return "(See Figure 1 at the start of the paper for the timeline diagram.)"
    elif ctr["n"] == 2:
        return ("![Taxonomy of world models for coding. Three modeling axes "
                "(code, agents, tasks) bridged by JEPA / Dreamer / latent-action "
                "discussion in §11. Specialized domains and synthesis chapters "
                "sit below.](fig_taxonomy.pdf)")
    return m.group(0)
text = re.sub(r"```\n(.*?)```", repl, text, flags=re.DOTALL)

with open("SURVEY_for_pdf.md", "w") as f:
    f.write(text)
PY

# 2. Markdown -> LaTeX (with \citep / \citet emission via --natbib)
pandoc SURVEY_for_pdf.md \
  -o paper.tex \
  --natbib \
  --template=neurips_template.tex \
  -V title="A Comprehensive Survey of World Models for Coding" \
  -V author="Keon Kim" \
  -V date="May 2026"

# 3. xelatex + bibtex + xelatex x3 (natbib needs the extra passes)
xelatex -interaction=nonstopmode paper.tex > /dev/null
bibtex paper > /dev/null
xelatex -interaction=nonstopmode paper.tex > /dev/null
xelatex -interaction=nonstopmode paper.tex > /dev/null
xelatex -interaction=nonstopmode paper.tex > /dev/null

# 4. Cleanup intermediate artifacts
rm -f paper.aux paper.log paper.bbl paper.blg paper.out paper.tex

echo "built paper.pdf ($(stat -f%z paper.pdf) bytes, $(mdls -name kMDItemNumberOfPages -raw paper.pdf) pages)"
