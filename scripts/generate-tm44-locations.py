#!/usr/bin/env python3
"""Generate TM44 coverage in the Birmingham repository; retain EPC metadata."""
from pathlib import Path
import json,re,html,csv,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
ORIGIN='https://birminghamcommercialepc.co.uk'
GUIDANCE='https://www.gov.uk/government/publications/air-conditioning-inspections-for-buildings/a-guide-to-air-conditioning-inspections'
rows=json.loads((ROOT/'data/tm44-locations.json').read_text());e=html.escape
# Remove only this generator's withdrawn, Git-tracked coverage pages.
allowed={r['slug'] for r in rows}
for page in ROOT.glob('tm44-inspections-*/index.html'):
 if page.parent.name not in allowed and '<main class="tm44-location ' in page.read_text():
  page.unlink()
  if not any(page.parent.iterdir()):page.parent.rmdir()
# Rebuild reciprocal blocks so withdrawn areas leave no stale EPC links.
for page in ROOT.glob('commercial-epc-*/index.html'):
 page.write_text(re.sub(r'<!-- tm44-related:start -->.*?<!-- tm44-related:end -->','',page.read_text(),flags=re.S))
source=(ROOT/'services/index.html').read_text()
head=re.search(r'<head>(.*?)</head>',source,re.S)[1]
head=re.sub(r'<script type="application/ld\+json">.*?</script>','',head,flags=re.S)
header=re.search(r'<div class="topline">.*?</header>',source,re.S)[0]
footer=re.search(r'<footer.*?</footer>',source,re.S)[0]
def pagehead(title,description,url):
 h=re.sub(r'<title>.*?</title>',lambda _: '<title>'+e(title)+'</title>',head,flags=re.S)
 for pattern,value in [(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*(">)',description),(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*(">)',title),(r'(<meta property="og:url" content=")[^"]*(">)',url),(r'(<link rel="canonical" href=")[^"]*(">)',url)]:
  h=re.sub(pattern,lambda m:m[1]+e(value,quote=True)+m[2],h)
 return re.sub(r'(/styles.css)(?:\?[^"\s]*)?',r'\1?v=20261103-tm44',h)
def write_page(slug,title,description,body,schema):
 p=ROOT/slug/'index.html';p.parent.mkdir(exist_ok=True)
 p.write_text('<!doctype html><html lang="en"><head>'+pagehead(title,description,f'{ORIGIN}/{slug}/')+'<script type="application/ld+json">'+json.dumps(schema).replace('<','\\u003c')+'</script></head><body>'+header+body+footer+'<script src="/site.js"></script></body></html>')
def breadcrumbs(name,url):
 return {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':ORIGIN+'/'},{'@type':'ListItem','position':2,'name':'TM44 locations','item':ORIGIN+'/tm44-locations/'},{'@type':'ListItem','position':3,'name':name,'item':url}]}
for i,r in enumerate(rows):
 name=r['location'];url=f'{ORIGIN}/{r["slug"]}/'
 epc_href='/'+r['epcSlug']+'/' if r['epcSlug'] else '/'
 epc_name=r.get('epcLocation',name)
 nextrows=[rows[(i+j)%len(rows)] for j in [1,2,3]]
 related=''.join(f'<a href="/{x["slug"]}/">TM44 {e(x["location"])} →</a>' for x in nextrows)
 local=f'''<section class="tm44-local"><p class="kicker">The property brief · {e(name)}</p><h2>{e(r['focus'])}</h2><p>{e(r['context'])}</p><div class="tm44-access"><h3>Plan access before the visit</h3><p>{e(r['access'])}</p></div></section>'''
 prepare=f'''<section class="tm44-prepare stone"><div><p class="kicker">A useful first enquiry</p><h2>What to send for your {e(name)} property</h2><p>Start with the full address, current building use and the part of the premises you manage. Explain the reason for your enquiry and any date you are working towards.</p></div><ol><li><b>Equipment and served rooms</b><p>Available cooling capacities, model references and a schedule connecting the plant to occupied areas. Include separate buildings and shared systems where relevant.</p></li><li><b>Earlier records and changes</b><p>The previous TM44 report, maintenance information and details of replacement equipment or altered layouts. Explain any missing documents.</p></li><li><b>Control and permissions</b><p>Who controls the equipment, who holds the records and who can authorise room and plant access. Describe restrictions before requesting a visit.</p></li></ol></section>'''
 scope='''<section class="tm44-scope"><p class="kicker">Air-conditioning energy assessment</p><h2>Understand what the inspection covers.</h2><div><article><h3>Start with the system</h3><p>TM44 concerns the energy performance of air conditioning. The assessment considers efficiency, sizing, controls and operation in relation to the areas served. It is an inspection and report, rather than an instruction to carry out repairs.</p></article><article><h3>Check whether it applies</h3><p>In England, the requirement applies to systems with an effective rated cooling output of more than 12kW. Individual units under common technical control can need to be considered together. A small-looking installation is not enough evidence to decide the position.</p></article><article><h3>Keep the work distinct</h3><p>A commercial EPC, refrigerant leak check and routine maintenance serve different purposes. Tell us which records or services you need so the proposed scope does not imply that one assessment replaces another.</p></article></div></section>'''
 faqs=f'''<section class="detail-faqs"><p class="kicker">Your questions</p><h2>TM44 enquiries in {e(name)}</h2><details><summary>What should I explain about {e(r['focus'].lower())}?</summary><p>{e(r['access'])} The quotation should identify the premises and equipment included, with responsibility and permissions confirmed before a visit.</p></details><details><summary>Can you quote if I do not know the cooling capacity?</summary><p>Send the available asset information, model numbers and accessible photographs. Explain what you do not know. The equipment details need review before the inspection requirement and scope can be confirmed.</p></details><details><summary>How often do qualifying systems need inspection?</summary><p>Government guidance specifies inspections at intervals no more than five years apart for systems in scope. Provide the earlier report so its date, coverage and subsequent installation changes can be reviewed.</p></details><details><summary>Does requesting a quotation confirm an appointment?</summary><p>No. The property details, agreed scope, price and access arrangements need confirmation. A statutory report must be prepared by an appropriately accredited air-conditioning energy assessor; the quotation should confirm the delivery arrangements.</p></details><p class="tm44-source">Read the <a href="{GUIDANCE}">government air-conditioning inspection guidance</a> for the statutory requirements. Use the guidance alongside the current equipment records when reviewing your inspection requirement.</p></section>'''
 body=f'''<main class="tm44-location tm44-layout-{r['layout']}"><section class="tm44-hero dark"><nav class="location-breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/tm44-locations/">TM44 locations</a><span aria-hidden="true">/</span><span aria-current="page">{e(name)}</span></nav><div class="tm44-hero-grid"><div><p class="kicker">Existing commercial buildings</p><h1>{e(r['h1'])}</h1><p class="lead">Air-conditioning energy inspections for existing business premises in {e(name)}. Build a clear property brief, review the system records and request a quotation matched to the installation.</p><a class="button brass-button" href="/quote">Request a TM44 quote →</a></div><aside><p class="kicker">Scope comes first</p><h2>{e(r['focus'])}</h2><p>{e(r['access'])}</p><a href="/tm44-inspection-birmingham/">Explore the main Birmingham TM44 service →</a></aside></div></section><div class="tm44-editorial">{prepare+local if r['layout']==1 else local+prepare}</div>{faqs+scope if r['layout']==2 else scope+faqs}<section class="detail-related"><p class="kicker">Related assessments and coverage</p><h2>Keep the right services connected.</h2><div><a href="{epc_href}">Commercial EPC {e(epc_name)} →</a><a href="/f-gas-leak-check-birmingham/">F-Gas leak checks →</a><a href="/commercial-energy-audit-birmingham/">Commercial energy audits →</a></div><div class="tm44-nearby">{related}</div><a class="text-link" href="/tm44-locations/">All TM44 location guides →</a></section><section class="detail-quote dark"><div><p class="kicker">Your next step</p><h2>Arrange the scope for {e(name)}.</h2><p>Select TM44 in the Birmingham quote form and include your property address, system information and access constraints. Existing reports can help explain what needs reviewing.</p><p>The enquiry is a request for a property-specific quotation. Availability, deliverables and any separate work are agreed before the instruction proceeds.</p></div><a class="button brass-button" href="/quote">Quote &amp; booking →</a></section></main>'''
 schema={'@context':'https://schema.org','@graph':[{'@type':'Service','name':r['h1'],'serviceType':'TM44 air-conditioning energy inspection','url':url,'description':r['description'],'areaServed':{'@type':'Place','name':name},'provider':{'@type':'Organization','name':'Birmingham Commercial EPC','url':ORIGIN+'/'}},breadcrumbs(name,url)]}
 write_page(r['slug'],r['title'],r['description'],body,schema)
items='<li><a href="/tm44-inspection-birmingham/"><span>Birmingham</span><span aria-hidden="true">↗</span></a><p>Our main Birmingham TM44 inspection service</p></li>'+''.join(f'<li><a href="/{r["slug"]}/"><span>{e(r["location"])}</span><span aria-hidden="true">↗</span></a><p>{e(r["focus"])}</p></li>' for r in sorted(rows,key=lambda r:r['location']))
write_page('tm44-locations','TM44 Inspection Locations | Birmingham & West Midlands',f'TM44 inspections in Birmingham and {len(rows)} main nearby towns and cities. Find your location and request an air-conditioning inspection quote.',f'''<main class="tm44-directory"><section class="tm44-hero dark"><p class="kicker">Birmingham &amp; nearby towns and cities</p><h1>TM44 inspection locations</h1><p class="lead">Find your property area and prepare a useful air-conditioning inspection enquiry. These guides cover existing commercial premises; scope and appointment arrangements depend on your building and systems.</p><div class="actions"><a class="button brass-button" href="/quote">Request a TM44 quote →</a><a href="/tm44-inspection-birmingham/">Birmingham TM44 service →</a></div></section><section class="section"><p class="kicker">Birmingham + {len(rows)} main towns &amp; cities</p><h2>Birmingham and the main nearby towns.</h2><ul class="tm44-directory-grid">{items}</ul></section></main>''',{'@context':'https://schema.org','@type':'CollectionPage','name':'TM44 inspection locations','url':ORIGIN+'/tm44-locations/'})
def insert_block(path,marker,block,before):
 s=path.read_text();pattern=rf'<!-- {marker}:start -->.*?<!-- {marker}:end -->';wrapped=f'<!-- {marker}:start -->{block}<!-- {marker}:end -->'
 if re.search(pattern,s,re.S):s=re.sub(pattern,lambda _:wrapped,s,flags=re.S)
 else:s=s.replace(before,wrapped+before,1)
 path.write_text(s)
insert_block(ROOT/'tm44-inspection-birmingham/index.html','tm44-coverage','<section class="tm44-coverage stone"><p class="kicker">Find your property area</p><h2>TM44 coverage around Birmingham</h2><p>Find Birmingham and the main nearby towns and cities, including Solihull, Wolverhampton, Coventry and Tamworth.</p><a class="button dark-button" href="/tm44-locations/">Explore TM44 locations →</a></section>','<section class="detail-faqs">')
insert_block(ROOT/'locations/index.html','tm44-directory-link','<section class="tm44-coverage stone"><p class="kicker">Looking for air-conditioning inspections?</p><h2>TM44 has its own location guides.</h2><p>Air-conditioning inspections and Commercial EPCs are separate services. Start with the guide for the assessment you need.</p><a class="button dark-button" href="/tm44-locations/">Find a TM44 location →</a></section>','</main>')
insert_block(ROOT/'services/index.html','tm44-service-link','<section class="tm44-coverage stone"><p class="kicker">Air-conditioning energy inspections</p><h2>Find your TM44 inspection area.</h2><p>Find Birmingham and nearby main towns and cities, then request a system-specific quotation.</p><a class="button dark-button" href="/tm44-locations/">TM44 locations →</a></section>','</main>')
for r in rows:
 if not r['epcSlug']:continue
 insert_block(ROOT/r['epcSlug']/'index.html','tm44-related','<section class="tm44-coverage stone"><p class="kicker">Air-conditioning in the same property?</p><h2>TM44 inspections in '+e(r['location'])+'</h2><p>A commercial EPC does not replace an air-conditioning energy inspection. Explore the system information and access details to prepare.</p><a class="text-link" href="/'+r['slug']+'/">TM44 '+e(r['location'])+' →</a></section>','</main>')
ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';ET.register_namespace('',ns[1:-1]);tree=ET.parse(ROOT/'sitemap.xml');urls={x.text for x in tree.findall('.//'+ns+'loc')}
for node in list(tree.getroot()):
 loc=node.find(ns+'loc')
 if loc is not None and loc.text.startswith(ORIGIN+'/tm44-inspections-') and loc.text not in {f'{ORIGIN}/{slug}/' for slug in allowed}:tree.getroot().remove(node)
urls={x.text for x in tree.findall('.//'+ns+'loc')}
for slug in ['tm44-locations',*[r['slug'] for r in rows]]:
 url=f'{ORIGIN}/{slug}/'
 if url not in urls:ET.SubElement(ET.SubElement(tree.getroot(),ns+'url'),ns+'loc').text=url
ET.indent(tree);tree.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
with (ROOT/'reports/tm44-locations-metadata.csv').open('w') as f:
 fields=['location','slug','h1','title','description'];writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");writer.writeheader();writer.writerows({k:r[k] for k in fields} for r in rows)
# Refresh stylesheet URLs on existing entry points as well as generated pages.
for p in [*ROOT.glob('*.html'),*ROOT.glob('*/index.html')]:
 p.write_text(re.sub(r'(/styles.css|(?<![/\w])styles.css)(?:\?[^\"\s]*)?',r'\1?v=20261103-tm44',p.read_text()))
print(f'Rendered {len(rows)} Birmingham-area TM44 location pages and their directory.')
