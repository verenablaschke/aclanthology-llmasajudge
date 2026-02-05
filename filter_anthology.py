from bs4 import BeautifulSoup
import glob
import csv

# ============================================================
# CSV output setup
# ============================================================

csv_path = "keyword_hits.csv"
f_csv = open(csv_path, "w", encoding="utf-8", newline="")
csv_writer = csv.writer(f_csv)

# Write header row
csv_writer.writerow(["FILE", "TITLE", "Matched Keywords", "ABSTRACT"])


#### ============================================================
#### Input XML Files 
#### ============================================================

# Option 1: Loop over *all* XML files in a directory
infiles = glob.glob("acl-anthology/data/xml/*.xml")

# Option 2: Provide an explicit list of XML files

# infiles = [
#     "acl-anthology/data/xml/2025.acl.xml",
#     "acl-anthology/data/xml/2025.emnlp.xml",
#     "acl-anthology/data/xml/2025.coling.xml",
#     "acl-anthology/data/xml/2025.findings.xml",
#     "acl-anthology/data/xml/2024.acl.xml",
#     "acl-anthology/data/xml/2024.emnlp.xml",
#     "acl-anthology/data/xml/2024.coling.xml",
#     "acl-anthology/data/xml/2024.findings.xml"    
# ]

#### ============================================================
#### Keyword Configuration
#### ============================================================
# Keywords are matched in a case-insensitive way.
# Each group is an OR list; across groups the logic is AND:
#   (any LLM keyword) AND (any Judge keyword) AND (any LR keyword)

llm_any = ["LLM", "large language model"]   # OR
judge_any = ["judge", "evaluator", "LLM-based evaluation", 
            "LLM-as-a-judge", "LLM-based assessment", "automatic evaluator"]  # OR
lr_any = ["low-resource", "underresourced", "underresearched", 
          "under-resourced", "under-researched", 
          "low resource", "multilingual"] # OR
# Alternative: disable low-resource filtering
#lr_any = [" "]


#### ============================================================
#### Keyword matching functions
#### ============================================================

def find_matched_keywords(text, keyword_list):
    """Return which keywords are matched (case insensitive)."""
    text_low = text.lower()
    return [kw for kw in keyword_list if kw.lower() in text_low]

def match_keywords_and_return_details(text):
    """
    Check whether text satisfies ALL keyword-group constraints:
        - At least one LLM keyword
        - At least one Judge keyword
        - At least one LR keyword

    Returns:
        (matched: bool, details: dict)
        where details = {
            "LLM": [...matched keywords...],
            "Judge": [...matched keywords...],
            "LR": [...matched keywords...]
        }
    """
    matched = True
    details = {}

    # LLM keywords
    llm_hits = find_matched_keywords(text, llm_any)
    if not llm_hits:
        matched = False
    details["LLM"] = llm_hits

    # Judge keywords
    judge_hits = find_matched_keywords(text, judge_any)
    if not judge_hits:
        matched = False
    details["Judge"] = judge_hits

    # Low-resource keywords
    lr_hits = find_matched_keywords(text, lr_any)
    if not lr_hits:
        matched = False
    details["LR"] = lr_hits

    return matched, details


#### ============================================================
#### Output file setup
#### ============================================================

output_path = "keyword_match_results.txt"
fout = open(output_path, "w", encoding="utf-8")

total_papers = 0   # Total number of papers across all XMLs
global_hits = 0    # Total matched papers across all XMLs

file_hit_stats = {}    # {xml_file: number of hits}
file_total_stats = {}  # {xml_file: total number of papers}


#### ============================================================
#### Main loop: parse each XML and apply keyword matching
#### ============================================================

for infile in infiles:
    print(f"\n=== PROCESSING: {infile} ===")
    fout.write(f"\n=== PROCESSING: {infile} ===\n")

    soup = BeautifulSoup(open(infile), 'xml')

    papers = soup.find_all("paper")
    file_total_stats[infile] = len(papers)
    total_papers += len(papers)
    file_hits = 0

    for paper in papers:
        title = (paper.find("title").text.strip()
                 if paper.find("title") and paper.find("title").text else "")

        abstract = (paper.find("abstract").text.strip()
                    if paper.find("abstract") and paper.find("abstract").text else "")

        combined = f"{title}\n{abstract}"

        matched, match_details = match_keywords_and_return_details(combined)

        if matched:
            global_hits += 1
            file_hits += 1

            # Write to CSV
            csv_writer.writerow([
                infile,
                title,
                "; ".join([f"{group}: {', '.join(kws)}" for group, kws in match_details.items()]),
                abstract
            ])
            ...

            print("\n=== HIT ===")
            print("FILE:", infile)
            print("TITLE:", title)
            print("Matched Keywords:", match_details)
            print()

            fout.write("\n=== HIT ===\n")
            fout.write(f"FILE: {infile}\n")
            fout.write(f"TITLE: {title}\n")
            fout.write("Matched Keywords:\n")
            for group, kws in match_details.items():
                fout.write(f"  - {group}: {', '.join(kws)}\n")
            fout.write(f"ABSTRACT: {abstract}\n\n")

    file_hit_stats[infile] = file_hits

#### ============================================================
#### Final summary (printed + stored)
#### ============================================================

print("\n---- SUMMARY ----")
print("Total papers:", total_papers)
print("Matched papers:", global_hits)
print("Per-file hits:", file_hit_stats)

fout.write("\n---- SUMMARY ----\n")
fout.write(f"Total papers: {total_papers}\n")
fout.write(f"Matched papers: {global_hits}\n")
fout.write("Per-file hits:\n")
for fname in infiles:
    hits_here = file_hit_stats.get(fname, 0)
    total_here = file_total_stats.get(fname, 0)
    print(f"  {fname}: {hits_here}/{total_here}")

fout.write("\n---- SUMMARY ----\n")
fout.write(f"Total papers: {total_papers}\n")
fout.write(f"Matched papers: {global_hits}\n")

fout.write("Per-file hits:\n")
for fname in infiles:
    hits_here = file_hit_stats.get(fname, 0)
    total_here = file_total_stats.get(fname, 0)
    fout.write(f"  {fname}: {hits_here}/{total_here}\n")

fout.close()
f_csv.close()