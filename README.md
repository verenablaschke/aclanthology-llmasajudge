# aclanthology-llmasajudge

Use the `--recursive` flag while cloning to also get the submodule content:

```
git clone git@github.com:verenablaschke/aclanthology-llmasajudge.git --recursive
```

## ACL Anthology Keyword Search

`filter_anthology.py` Python script for keyword-based search over ACL Anthology XML files, targeting *LLM-as-a-judge* work in low-resource or multilingual settings.

**Input:**  
`acl-anthology/data/xml/` (via Git submodule; all files or a specified subset)

**Output:**  
- `keyword_hits.csv` — matched papers (file, title, keywords, abstract)  
- `keyword_match_results.txt` — detailed logs + summary  

Keyword matching is case-insensitive (OR within groups, AND across groups).