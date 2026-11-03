#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from urllib.parse import urlsplit,unquote
import json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
class Inspect(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=[];self.h1=0;self.canonical=[];self.title='';self.desc='';self.in_title=False;self.in_h1=False;self.h1text=''
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='a' and a.get('href'):self.links.append(a['href'])
  if a.get('id'):self.ids.append(a['id'])
  if t=='h1':self.h1+=1;self.in_h1=True
  if t=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
  if t=='title':self.in_title=True
  if t=='meta' and a.get('name')=='description':self.desc=a.get('content','')
 def handle_endtag(self,t):
  if t=='title':self.in_title=False
  if t=='h1':self.in_h1=False
 def handle_data(self,s):
  if self.in_title:self.title+=s
  if self.in_h1:self.h1text+=s+' '
pages=list(ROOT.glob('*.html'))+list(ROOT.glob('*/index.html'));data={};errors=[]
for p in pages:
 parser=Inspect();parser.feed(p.read_text());rel=p.relative_to(ROOT).as_posix();data[rel]=parser
 if p.name!='404.html':
  if parser.h1!=1:errors.append(f'{rel}: expected one H1')
  if len(parser.canonical)!=1:errors.append(f'{rel}: expected one canonical')
 if len(parser.ids)!=len(set(parser.ids)):errors.append(f'{rel}: duplicate element IDs')
 for link in parser.links:
  parts=urlsplit(link)
  if parts.netloc and parts.netloc!='birminghamcommercialepc.co.uk':continue
  path=parts.path
  if not path.startswith('/') or path.startswith('//'):continue
  path=unquote(path.lstrip('/'))
  candidates=[ROOT/(path or 'index.html'),ROOT/(path+'.html'),ROOT/path/'index.html']
  if not any(c.is_file() for c in candidates):errors.append(f'{rel}: missing destination {link}')
for field in ['title','desc','h1text']:
 values=[getattr(p,field).strip().casefold() for rel,p in data.items() if rel!='404.html']
 if len(values)!=len(set(values)):errors.append(f'Duplicate {field} across indexable site')
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'};urls=[n.text for n in ET.parse(ROOT/'sitemap.xml').findall('.//s:loc',ns)]
tm44=json.loads((ROOT/'data/tm44-locations.json').read_text()) if (ROOT/'data/tm44-locations.json').exists() else []
expected=121+len(tm44)+(1 if tm44 else 0)
if len(urls)!=expected or len(set(urls))!=expected:errors.append(f'Expected {expected} distinct sitemap URLs')
if tm44:
 directory_tm44=data['tm44-locations/index.html']
 for row in tm44:
  path='/'+row['slug']+'/'
  if path not in directory_tm44.links:errors.append(f'TM44 directory missing {path}')
  page=data[row['slug']+'/index.html']
  if page.h1text.strip()!=row['h1']:errors.append(f'TM44 H1 mismatch: {path}')
  if page.canonical!=['https://birminghamcommercialepc.co.uk'+path]:errors.append(f'TM44 canonical mismatch: {path}')
  if '/'+row['epcSlug']+'/' not in page.links:errors.append(f'TM44 missing related EPC: {path}')
  if path not in data[row['epcSlug']+'/index.html'].links:errors.append(f'EPC missing related TM44: {path}')
directory=data['locations/index.html'];location_paths={urlsplit(r['url']).path for r in json.loads((ROOT/'data/seo-pages.json').read_text())['pages'][1:]}
if not location_paths.issubset(set(directory.links)):errors.append('Directory does not link to every location')
result={'htmlPages':len(pages),'indexablePages':len(pages)-1,'sitemapUrls':len(urls),'locationDirectoryLinks':len(location_paths),'errors':errors,'status':'PASS' if not errors else 'FAIL'}
(ROOT/'reports/site-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));raise SystemExit(bool(errors))
