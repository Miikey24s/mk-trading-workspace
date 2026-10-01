import hashlib, json
from pathlib import Path
root=Path(__file__).resolve().parent
names=[]
for p in sorted(root.glob('*.png')):
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 names.append({'file':p.name,'sha256':h,'bytes':p.stat().st_size})
(root/'hashes.json').write_text(json.dumps(names,indent=2),encoding='utf-8')
print(json.dumps(names,indent=2))
