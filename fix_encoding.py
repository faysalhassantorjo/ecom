import json

with open('db.json', 'r', encoding='utf-8', errors='replace') as infile:
    data = json.load(infile)

with open('db_utf8.json', 'w', encoding='utf-8') as outfile:
    json.dump(data, outfile, ensure_ascii=False, indent=4)
