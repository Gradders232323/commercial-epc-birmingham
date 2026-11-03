#!/usr/bin/env python3
"""Audit real HTML against the approved SEO inventory; never infer missing locations."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
from collections import Counter
import csv,json,re,sys
ROOT=Path(__file__).resolve().parent.parent
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.title='';self.description='';self.h1=[];self.opener='';self.body='';self.active=None;self.main=False;self.first_p=False;self.ignored=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ('script','style'):self.ignored+=1
  if tag=='meta' and a.get('name')=='description':self.description=a.get('content','')
  if tag=='main':self.main=True
  if tag=='title':self.active='title'
  if tag=='h1':self.h1.append('');self.active='h1'
  if tag=='p' and self.main and 'lead' in a.get('class','').split() and not self.opener:self.active='opener';self.first_p=True
 def handle_endtag(self,tag):
  if tag in ('script','style'):self.ignored=max(0,self.ignored-1)
  if tag=='main':self.main=False
  if tag in ('title','h1','p') and (tag!='p' or self.first_p):self.active=None;self.first_p=False
 def handle_data(self,data):
  if self.ignored:return
  if self.active=='title':self.title+=data
  elif self.active=='h1':self.h1[-1]+=data+' '
  elif self.active=='opener':self.opener+=data+' '
  if self.main:self.body+=data+' '
def clean(s):return ' '.join(s.split())
manifest=json.loads((ROOT/'data/seo-pages.json').read_text());rows=[]
for spec in manifest['pages']:
 p=Page();p.feed((ROOT/spec['file']).read_text());keyword=spec['primaryKeyword'];h=clean(' '.join(p.h1));t=clean(p.title);d=clean(p.description);errors=[];notes=[]
 for label,value in [('H1',h),('Meta title',t),('Meta description',d),('Opening paragraph',clean(p.opener))]:
  if keyword not in value:errors.append(f'{label}: exact keyword missing')
 if len(p.h1)!=1:errors.append('Must have exactly one H1')
 if h.casefold()==t.casefold():errors.append('H1 and title identical')
 if len({h.casefold(),t.casefold(),d.casefold()})<3:errors.append('SEO elements repeat the same wording')
 if not 50<=len(t)<=60:notes.append('Title outside preferred 50–60 range')
 if not 140<=len(d)<=160:notes.append('Description outside preferred 140–160 range')
 if spec['type']=='property' and 'Commercial EPC Birmingham' not in p.body:errors.append('Supporting Birmingham keyword missing')
 occurrences=p.body.casefold().count(keyword.casefold());words=max(1,len(p.body.split()));density=occurrences*len(keyword.split())/words
 if density>.04 and occurrences>3:errors.append('Review excessive exact-keyword repetition')
 rows.append({'URL':spec['url'],'Primary Keyword':keyword,'H1':h,'Meta Title':t,'Meta Description':d,'Character Counts':f'H1 {len(h)} | Title {len(t)} | Description {len(d)}','Validation Status':'','errors':errors,'notes':notes,'type':spec['type'],'location':spec.get('location',''),'density':round(density,4)})
for field in ['H1','Meta Title','Meta Description']:
 counts=Counter(r[field].casefold() for r in rows)
 for r in rows:
  if counts[r[field].casefold()]>1:r['errors'].append(f'Duplicate {field}')
# Detect description skeletons shared after removing exact location/service keywords.
def skeleton(r):
 text=r['Meta Description'].casefold().replace(r['Primary Keyword'].casefold(),'[keyword]')
 if r['location']:text=text.replace(r['location'].casefold(),'[location]')
 return re.sub(r'\W+',' ',text).strip()
patterns=Counter(skeleton(r) for r in rows)
for r in rows:
 if patterns[skeleton(r)]>1:r['errors'].append('Description is a repeated location-substitution pattern')
 r['Validation Status']='PASS' if not r['errors'] else 'FAIL: '+'; '.join(r['errors'])
fields=['URL','Primary Keyword','H1','Meta Title','Meta Description','Character Counts','Validation Status'];out=ROOT/'reports';out.mkdir(exist_ok=True)
with (out/'seo-audit.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
counts=Counter(r['type'] for r in rows);coverage={'locations':{'actual':counts['location'],'expected':manifest['expectedLocationPages']},'propertyTypes':{'actual':counts['property'],'expected':manifest['expectedPropertyPages']}}
complete=counts['location']==manifest['expectedLocationPages'] and counts['property']==manifest['expectedPropertyPages'];summary={'pagesAudited':len(rows),'passed':sum(not r['errors'] for r in rows),'coverage':coverage,'scopeComplete':complete,'locationScopeComplete':counts['location']==manifest['expectedLocationPages'],'pendingPropertyTypes':manifest['expectedPropertyPages']-counts['property'],'limitations':'Structural checks flag repetition; editorial review is still required to judge natural language. Missing pages are not counted as passing.','rows':rows}
(out/'seo-audit.json').write_text(json.dumps(summary,indent=2)+'\n')
html='<!doctype html><meta charset="utf-8"><title>Birmingham SEO Audit</title><style>body{font:15px/1.5 system-ui;margin:32px;color:#183b33}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd6d0;padding:12px;text-align:left;vertical-align:top}th{background:#edf3ec}td{min-width:130px}h1{font-size:28px}</style><h1>Birmingham SEO audit</h1><p>'+f'{len(rows)} existing page(s) audited. Location coverage: {counts["location"]}/{manifest["expectedLocationPages"]}. Property coverage: {counts["property"]}/{manifest["expectedPropertyPages"]}. All 100 supplied locations plus the Birmingham homepage are included. The 20 property-type pages remain pending their approved list.'+'</p><table><thead><tr>'+''.join('<th>'+escape(x)+'</th>' for x in fields)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(r[x])+'</td>' for x in fields)+'</tr>' for r in rows)+'</tbody></table>'
(out/'seo-audit.html').write_text(html)
print(json.dumps({'pagesAudited':len(rows),'passed':summary['passed'],'coverage':coverage,'scopeComplete':complete}))
if any(r['errors'] for r in rows) or ('--require-complete' in sys.argv and not complete) or ('--require-locations' in sys.argv and counts['location']!=manifest['expectedLocationPages']):sys.exit(1)
