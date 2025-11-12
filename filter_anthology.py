from bs4 import BeautifulSoup

# Only one infile as proof-of-concept for setting up this code snippet
infile = "acl-anthology/data/xml/2025.acl.xml"

soup = BeautifulSoup(open(infile), 'xml')

for paper in soup.find_all("paper"):
    title = paper.title.text
    abstract = paper.abstract.text
    print(title)
    print(abstract)
    print()
    
# filter based on keyword combinations, keep track of results (how many hits, what kinds of content)

