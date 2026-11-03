#!/usr/bin/env python3
"""Render Birmingham-only service pages without modifying EPC page metadata."""
from pathlib import Path
import json,re,html,csv,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
ORIGIN='https://birminghamcommercialepc.co.uk'
rows=json.loads((ROOT/'data/service-pages.json').read_text());catalog=json.loads((ROOT/'data/services.json').read_text());e=html.escape
source=(ROOT/'services/index.html').read_text();basehead=source.split('<head>',1)[1].split('</head>',1)[0];basehead=re.sub(r'<script type="application/ld\+json">.*?</script>','',basehead,flags=re.S)
header=re.search(r'<div class="topline">.*?</header>',source,re.S).group(0);footer=re.search(r'<footer.*?</footer>',source,re.S).group(0)
oldtitle=re.search(r'<title>(.*?)</title>',basehead).group(1);oldDesc=re.search(r'<meta name="description" content="(.*?)">',basehead).group(1)
local={
'Energy Certificates':('Offices, public buildings and mixed occupation','For city-centre offices and separately occupied floors, identify the exact accommodation. Public-building reports need the organisation and operational evidence; a commercial EPC needs the assessment boundary and available building information.','commercial-epc-colmore-business-district','Colmore Business District'),
'Energy Compliance':('Decisions around occupied commercial property','For a letting or improvement review in Birmingham, provide the existing reports, current occupation and the decision you need to make. Distinguish building-specific work from any wider organisational obligations.','commercial-epc-jewellery-quarter','Jewellery Quarter'),
'HVAC Compliance':('Plant, served areas and safe access','For office or industrial accommodation, identify the rooms each system serves and who controls the equipment. Explain shared roofs, external plant areas and any restricted access rather than assuming one site contact can open every area.','commercial-epc-tyseley','Tyseley'),
'Building Safety':('People, occupation and the actual premises','For Birmingham mixed-use buildings and managed workplaces, explain the commercial boundaries, common areas and other occupiers. Earlier reports and management records can help define gaps without assuming the whole building needs the same work.','commercial-epc-digbeth','Digbeth'),
'Electrical & Gas Safety':('Coordinate testing with business operations','For occupied Birmingham premises, identify critical equipment, opening hours and any isolation restrictions. Agree who can authorise access or interruptions and which installation or appliances are included in the inspection.','commercial-epc-aston','Aston'),
}
for s in rows:
 if s['slug']=='fire-risk-assessment-birmingham':s['sections'][2]['text']=s['sections'][2]['text'].replace('The assessment should identify','The written assessment should identify')
 url=f'{ORIGIN}/{s["slug"]}/';head=basehead.replace(oldtitle,e(s['title'])).replace(oldDesc,e(s['description'])).replace(ORIGIN+'/services/',url)
 head=head.replace('/styles.css?v=20261017-photos','/styles.css?v=20261103-services')
 schema={'@context':'https://schema.org','@graph':[{'@type':'Service','name':s['name'],'serviceType':s['name'],'url':url,'description':s['summary'],'areaServed':[{'@type':'City','name':'Birmingham'},{'@type':'Place','name':'West Midlands'}],'provider':{'@type':'Organization','name':'Birmingham Commercial EPC','url':ORIGIN+'/'}},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':ORIGIN+'/'},{'@type':'ListItem','position':2,'name':'Services','item':ORIGIN+'/services/'},{'@type':'ListItem','position':3,'name':s['name'],'item':url}]}]}
 cases='<section class="detail-use-cases"><p class="kicker">Existing commercial premises</p><h2>When this service can help</h2><ul>'+''.join('<li>'+e(c)+'</li>' for c in s['cases'])+'</ul></section>'
 scope='<div class="detail-scope">'+''.join(f'<section><p class="kicker">0{i+1} · Scope and preparation</p><h2>{e(part["title"])}</h2><p>{e(part["text"])}</p></section>' for i,part in enumerate(s['sections']))+'</div>'
 localtitle,localcopy,nearby,nearbyname=local[s['group']]
 related=''
 for slug in s['related']:
  target=next((r for r in rows if r['slug']==slug),None)
  if slug=='commercial-epc-birmingham':related+='<a href="/">Commercial EPC Birmingham →</a>'
  elif target:related+=f'<a href="/{e(slug)}/">{e(target["name"])} →</a>'
 faq=''.join(f'<details><summary>{e(f["question"])}</summary><p>{e(f["answer"])}</p></details>' for f in s['faqs'])
 sources=''.join(f'<li><a href="{e(v["url"])}" target="_blank" rel="noopener noreferrer">{e(v["title"])} ↗</a></li>' for v in s['sources'])
 content=f'''<main class="service-detail service-detail-{s['layout']}"><section class="detail-hero dark"><div><nav class="location-breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/services/">Services</a><span aria-hidden="true">/</span><span aria-current="page">{e(s['name'])}</span></nav><p class="kicker">{e(s['group'])} · Existing buildings</p><h1>{e(s['h1'])}</h1><p class="lead">{e(s['intro'])}</p><div class="actions"><a class="button brass-button" href="/quote">Request a service quote <span aria-hidden="true">→</span></a><a href="#scope">Explore the scope ↓</a></div></div><aside><p class="kicker">Birmingham & the West Midlands</p><h2>{e(s['focus'])}</h2><p>Tell us the property, its current use and the purpose of your enquiry. The appropriate scope, provider and arrangements are confirmed before work is agreed.</p></aside></section><div id="scope" class="detail-content">{scope+cases if s['layout']%2 else cases+scope}</div><section class="detail-local stone"><div><p class="kicker">Birmingham property context</p><h2>{e(localtitle)}</h2><p>{e(localcopy)}</p></div><div><h3>Start with the precise address</h3><p>We welcome enquiries for existing premises in Birmingham and surrounding West Midlands commercial areas. The location alone does not establish an inspection requirement, a completed customer project or a local branch office.</p><a class="text-link" href="/{nearby}/">Commercial EPC {e(nearbyname)} →</a><a class="text-link" href="/locations/">All 100 location guides →</a></div></section><section class="detail-faqs"><p class="kicker">Before you enquire</p><h2>{e(s['name'])}: useful answers</h2>{faq}<aside class="detail-guidance"><h3>Official and technical guidance</h3><ul>{sources}</ul></aside></section><section class="detail-related"><h2>Related services</h2><div>{related}</div><a class="text-link" href="/services/">All Birmingham services →</a></section><section class="detail-quote dark"><div><p class="kicker">Property-specific quotations</p><h2>Discuss your {e(s['name'].lower())} requirement.</h2><p>Use the existing Birmingham quote and booking form. Select the service, provide the full address and describe the information you have. Add earlier reports, system details and access restrictions where relevant.</p><p>Enquiries do not confirm a price, appointment or compliance outcome. The agreed instruction should identify the deliverables and any separate testing, servicing or remedial work.</p></div><a class="button brass-button" href="/quote">Quote & booking <span aria-hidden="true">→</span></a></section></main>'''
 p=ROOT/s['slug']/'index.html';p.parent.mkdir(exist_ok=True);p.write_text('<!doctype html><html lang="en"><head>'+head+'<script type="application/ld+json">'+json.dumps(schema).replace('<','\\u003c')+'</script></head><body>'+header+content+footer+'<script src="/site.js"></script></body></html>')
# Each service card now has its own page; commercial EPC retains the homepage.
p=ROOT/'services/index.html';overview=p.read_text()
for service in catalog:
 pattern=r'(<h3>'+re.escape(e(service['name']))+r'</h3>.*?)(<a href="/quote" class="text-link">Discuss this service <span aria-hidden="true">→</span></a>)'
 overview,count=re.subn(pattern,lambda m:m[1]+'<a href="'+service['href']+'" class="text-link">Explore service <span aria-hidden="true">→</span></a>',overview,flags=re.S)
 if not count:
  # Idempotent reruns already point at the dedicated page.
  assert f'href="{service["href"]}" class="text-link">Explore service' in overview,service['name']
p.write_text(overview)
ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';ET.register_namespace('',ns[1:-1]);tree=ET.parse(ROOT/'sitemap.xml');urls={x.text for x in tree.findall('.//'+ns+'loc')}
for s in rows:
 url=f'{ORIGIN}/{s["slug"]}/'
 if url not in urls:ET.SubElement(ET.SubElement(tree.getroot(),ns+'url'),ns+'loc').text=url
ET.indent(tree);tree.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
with (ROOT/'reports/service-pages-metadata.csv').open('w') as f:
 fields=['name','group','slug','h1','title','description','layout'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:s[k] for k in fields} for s in rows)
print('Rendered 16 dedicated Birmingham service pages; EPC homepage retained; all 17 cards linked.')

# Retain TM44 coverage and cross-links when regenerating shared pages.
if (ROOT / "data/tm44-locations.json").exists():
 import runpy
 runpy.run_path(str(ROOT / "scripts/generate-tm44-locations.py"), run_name="__main__")
