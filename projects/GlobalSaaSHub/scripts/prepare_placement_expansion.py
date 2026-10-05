"""Add bounded owner-authorized house placements; never create paid orders.

The existing three fixed placements and their event definitions are unchanged.
"""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
import argparse,json,re
from prepare_coshuma_promotions import image_size
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
 'tool-rotation':('tool/pipedrive.html','rotating'),
 'guide-rotation':('best/claap-sales-follow-up-ai.html','rotating'),
 'compare-rotation':('compare/semrush-vs-frase.html','rotating'),
 'buyer-hub-fixed':('best/index.html','fixed'),
 'comparison-hub-fixed':('compare/index.html','fixed')}
DESTINATIONS={'/best/index.html','/compare/','/best/claap-sales-follow-up-ai.html#claap-3-call-checklist'}
ASSETS={'/promotions/house-wide-guides.webp','/promotions/house-wide-checklist.webp','/promotions/house-wide-comparisons.webp'}
CSS='<link rel="stylesheet" href="/house-placements.css" />'
JS='<script defer src="/house-placements.js"></script>'
BLOCK=re.compile(r'\n?<!-- HOUSE_PLACEMENT_START:[a-z-]+ -->.*?<!-- HOUSE_PLACEMENT_END -->',re.S)

def load_config():
 data=json.loads((ROOT/'data/placement-expansion.json').read_text(encoding='utf-8'))
 if data.get('schema_version')!=1 or type(data.get('house_enabled')) is not bool or data.get('paid_bookings_open') is not False:raise ValueError('House-only configuration required')
 rows=data['slots'];creatives=data['creatives']
 if len(rows)!=5 or {r['id'] for r in rows}!=set(EXPECTED):raise ValueError('Five exact positions required')
 if len({c['id'] for c in creatives})!=len(creatives):raise ValueError('Duplicate creative ID')
 by_id={c['id']:c for c in creatives}
 for c in creatives:
  if c['advertiser']!='COSHUMA' or c['destination'] not in DESTINATIONS or c['image'] not in ASSETS:raise ValueError('Only approved first-party creative is permitted')
  for key,low,high in [('title',5,80),('description',20,240),('button',2,30),('alt',10,160)]:
   value=c[key]
   if not isinstance(value,str) or not low<=len(value)<=high or any(ch in value for ch in '<>\r\n'):raise ValueError('Invalid plain-text creative')
  image=ROOT/'public'/c['image'].lstrip('/')
  if image_size(image)!=(1200,400) or image.stat().st_size>400000 or (c['width'],c['height'])!=(1200,400):raise ValueError('Invalid image')
 for r in rows:
  if (r['file'],r['mode'])!=EXPECTED[r['id']]:raise ValueError('Unapproved page or mode')
  cap=3 if r['mode']=='rotating' else 1
  if r['capacity']!=cap or r['interval_ms']!=(8000 if cap==3 else 0) or r['rate_usd'] is not None:raise ValueError('Invalid capacity, timing or unapproved rate')
  if not 1<=len(r['creative_ids'])<=cap or len(set(r['creative_ids']))!=len(r['creative_ids']) or not set(r['creative_ids'])<=set(by_id):raise ValueError('Over-capacity or invalid creatives')
 return data

class SectionBeforeHeading(HTMLParser):
 def __init__(self,text,heading):
  super().__init__(convert_charrefs=True);self.stack=[];self.target=heading;self.active=None;self.found=[];self.lines=[0]
  for m in re.finditer('\n',text):self.lines.append(m.end())
 def offset_at(self):
  line,col=self.getpos();return self.lines[line-1]+col
 def handle_starttag(self,tag,attrs):
  if tag=='section':self.stack.append(self.offset_at())
  if tag in ('h1','h2','h3'):self.active=[tag,[],self.stack[-1] if self.stack else None]
 def handle_data(self,text):
  if self.active:self.active[1].append(text)
 def handle_endtag(self,tag):
  if self.active and tag==self.active[0]:
   if ' '.join(''.join(self.active[1]).split())==' '.join(self.target.split()):self.found.append(self.active[2])
   self.active=None
  if tag=='section' and self.stack:self.stack.pop()

def render_slot(row,creatives):
 sid=row['id'];mode=row['mode'];items=[creatives[i] for i in row['creative_ids']];n=len(items)
 controls=''
 if mode=='rotating':
  controls=f'''<div class="house-slot__controls" data-house-controls hidden><button type="button" data-house-play>Pause rotation</button><button type="button" data-house-prev aria-label="Previous advertisement">Previous</button><span data-house-count>1 / {n}</span><button type="button" data-house-next aria-label="Next advertisement">Next</button></div>'''
 slides=[]
 for i,c in enumerate(items):
  e=lambda k:escape(str(c[k]),quote=True)
  hidden=' hidden' if i else ''
  slides.append(f'''<article id="{sid}-slide-{i}" class="house-slot__slide" data-house-slide="{e('id')}" role="group" aria-roledescription="slide" aria-label="{i+1} of {n}"{hidden}><img src="{e('image')}" width="1200" height="400" alt="{e('alt')}" loading="lazy" decoding="async"/><div class="house-slot__copy"><h2>{e('title')}</h2><p>{e('description')}</p><a class="house-slot__button" data-house-link href="{e('destination')}">{e('button')}</a></div></article>''')
 return f'''\n<!-- HOUSE_PLACEMENT_START:{sid} -->
<aside id="{sid}" class="house-slot" data-house-slot="{sid}" data-house-mode="{mode}" aria-label="COSHUMA {mode} advertisements" role="region" aria-roledescription="{'carousel' if mode=='rotating' else 'advertisement'}">
<div class="house-slot__top"><span>Advertisement &middot; COSHUMA</span><span class="house-slot__type">{'Rotating placement' if mode=='rotating' else 'Fixed placement'}</span></div>
{controls}<div class="house-slot__slides" data-house-slides aria-live="off">{''.join(slides)}</div>
<div class="house-slot__interest"><span>{'Shared rotation · up to 3 campaigns' if mode=='rotating' else 'One campaign in this position'} &middot; House demonstration</span><a href="/advertise.html?placement={sid}#inquire" data-house-inquiry>Explore this placement &rarr;</a></div>
</aside>
<!-- HOUSE_PLACEMENT_END -->'''

def prepare(text,row,creatives,enabled=True):
 clean=BLOCK.sub('',text).replace(CSS,'').replace(JS,'')
 if not enabled:return clean
 parser=SectionBeforeHeading(clean,row['before_heading']);parser.feed(clean)
 if len(parser.found)!=1 or parser.found[0] is None:raise ValueError('Placement anchor changed: '+row['id'])
 at=parser.found[0]
 if clean.count('</head>')!=1 or clean.count('</body>')!=1:raise ValueError('Malformed document')
 result=clean[:at]+render_slot(row,creatives)+clean[at:]
 return result.replace('</head>',CSS+'</head>',1).replace('</body>',JS+'</body>',1)

def inventory_section(data):
 existing=[('tool-primary','Pipedrive / introduction','Fixed','/tool/pipedrive.html','600 × 600 · 300 KB'),('buyer-intent-top','Claap / introduction','Fixed','/best/claap-sales-follow-up-ai.html','1200 × 675 · 500 KB'),('compare-decision-premium','Semrush / Frase / before sources','Fixed','/compare/semrush-vs-frase.html','1200 × 400 · 400 KB')]
 rows=[]
 for sid,label,mode,page,spec in existing:
  rows.append(f'<tr><th scope="row">{escape(label)}</th><td>{mode}</td><td>1</td><td>{spec}</td><td><a data-live-example href="{page}#coshuma-promotion">View</a></td></tr>')
 for r in data['slots']:
  rows.append(f'<tr><th scope="row">{escape(r["id"].replace("-"," ").title())}<span class="house-inventory__where">{escape(r["position"])}</span></th><td>{r["mode"].title()}</td><td>{r["capacity"]}</td><td>1200 × 400 · 400 KB</td><td><a data-live-example href="{r["page"]}#{r["id"]}">View</a> · <a href="#inquire" data-choose-placement="{r["id"]}">Inquire</a></td></tr>')
 return '''<section id="placement-formats" class="section" aria-labelledby="placement-formats-title"><p class="eyebrow">Five fixed positions. Three rotating positions.</p><h2 id="placement-formats-title">Choose exclusive space or a shared rotation.</h2><p class="section-intro">A fixed position shows one campaign. A rotating position can share up to three campaigns, showing one at a time. These are live COSHUMA house demonstrations, not paid-client results or an invitation to pay.</p><div class="table-wrap"><table class="house-inventory"><caption>Eight positions on five pages. Maximum two ad positions per page. File sizes below are pixels and KB, not on-screen display sizes.</caption><thead><tr><th scope="col">Position</th><th scope="col">Format</th><th scope="col">Capacity</th><th scope="col">Image file</th><th scope="col">Explore</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div><div class="scope-row"><div><strong>Fixed means one campaign in that position.</strong><p>No rotation. This is exclusivity for the named position, not for the page, category or entire site. It does not guarantee that every visitor sees the ad.</p></div><div><strong>Rotation shares the position, not the results.</strong><p>The default interval is eight seconds while the unit is in view. Hover, keyboard focus, user pause, reduced-motion settings and inactive tabs can stop rotation. With three campaigns, a full uninterrupted cycle takes 24 seconds.</p></div><div><strong>Agree on the format before booking.</strong><p>A fixed booking is not silently converted into shared rotation. The number of campaigns, dates, reporting rules and price must be agreed first. No reach, click or one-third-impression guarantee is made.</p></div></div><p class="note">The starting slide is selected randomly on each page load; eligible slides take equal-length turns. This is not a guarantee of equal impressions across visitors. Only the visible creative can earn a measured impression. New positions and rotating campaigns require a separate quote; existing text-ad planning rates below must not be treated as rotating-ad prices. Paid image bookings remain closed.</p></section>'''

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--verify',type=Path);args=parser.parse_args();data=load_config();creatives={c['id']:c for c in data['creatives']};folder=args.verify or ROOT/'public'
 for row in data['slots']:
  path=folder/row['file'];text=path.read_text(encoding='utf-8')
  if args.verify:
   count=text.count('data-house-slot="'+row['id']+'"')
   if count!=(1 if data['house_enabled'] else 0):raise ValueError('Missing or duplicate unit: '+row['id'])
   if data['house_enabled']:
    for marker in ['house-placements.js','house-placements.css','data-house-inquiry']:
     if marker not in text:raise ValueError('Lost '+marker)
  else:
   updated=prepare(text,row,creatives,data['house_enabled'])
   if text!=updated:path.write_text(updated,encoding='utf-8')
 page=folder/'advertise.html';text=page.read_text(encoding='utf-8')
 if args.verify:
  if 'id="placement-formats"' not in text:raise ValueError('Inventory guide missing')
 else:
  section=inventory_section(data)
  pattern=r'<!-- HOUSE_INVENTORY_START -->.*?<!-- HOUSE_INVENTORY_END -->'
  replacement='<!-- HOUSE_INVENTORY_START -->'+section+'<!-- HOUSE_INVENTORY_END -->'
  if re.search(pattern,text,re.S):text=re.sub(pattern,lambda m:replacement,text,flags=re.S)
  else:
   anchor='<section id="budgets"';assert text.count(anchor)==1;text=text.replace(anchor,replacement+'\n'+anchor,1)
  page.write_text(text,encoding='utf-8')
 print('Placement expansion: 2 fixed + 3 rotating house units verified. Paid bookings stay closed.')
if __name__=='__main__':main()
