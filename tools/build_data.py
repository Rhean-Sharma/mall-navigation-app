#!/usr/bin/env python3
"""Digitize the Woodbury Common map: stores, suites, walkway graph, districts.
Outputs data.json and a verification overlay render."""
import json, re, math
from PIL import Image, ImageDraw

# ---------------- suite coordinates (map px, 1870x1640) ----------------
SUITES = {
  # Adirondacks — outer (west/north) row
  '850': (522,196), '912': (537,263), '920': (526,287), '924': (515,311), '928': (504,327),
  '934': (456,387),
  '950': (506,539), '954': (516,564), '960': (527,589), '964': (539,613), '968': (548,639),
  '974': (536,690),
  # Adirondacks — inner row, north side (faces upper walkway)
  '846': (619,244), '844': (633,256), '842': (648,268), '836': (681,280), '832': (707,291),
  '830': (730,302), '826': (750,313), '822': (773,337), '818': (795,339), '812': (815,354),
  '808': (837,363), '804': (859,372), '802': (885,363),
  # Adirondacks — inner row, south side
  '835': (591,328), '831': (616,324), '825': (633,337), '821': (659,348), '815': (678,359),
  '813': (704,374), '807': (730,384), '803': (748,395), '801': (770,410),
  '839': (585,343), '841': (570,364), '843': (564,384),
  # Adirondacks — inner row, east side (faces lower walkway)
  '847': (552,438), '851': (563,467), '861': (579,495), '865': (585,513), '869': (591,532),
  '873': (601,553), '877': (609,573), '881': (619,593), '883': (624,613), '885': (633,633),
  '889': (659,648),
  # Market Hall
  'MH1': (619,948), 'MH2': (559,853), 'MH3': (544,817), 'MH4': (541,785), 'MH5': (589,750),
  'MH6': (727,687), 'MH7': (728,706), 'MH8': (741,717), 'MH9': (748,736), 'MH10': (763,756),
  '337': (580,904), 'MH': (693,830),
  # Hudson Valley — west cluster (Gucci/UGG/Moncler)
  '302': (867,458), '312': (756,505), '318': (733,533), '300': (833,535), '298': (885,539),
  '322': (744,570), '324': (754,590), '326': (763,611), '296': (876,578),
  '332': (838,666), '340': (796,695), '342': (772,705),
  # Hudson Valley — south row near Market Hall
  '349': (830,813), '347': (850,822), '345': (868,819), '341': (881,810),
  '321': (1037,738), '327': (1013,752), '329': (987,757), '331': (970,768), '333': (950,778),
  '335': (926,787), '315': (1067,772), '311': (1128,719), '313': (1128,737),
  'K107': (1167,687), '303': (1195,740), '283': (1326,818),
  # Hudson Valley — north row
  '280': (979,595), '276': (1024,632), '266': (1090,625), '254': (1228,627), '258': (1173,643),
  '250': (1280,646), '240': (1322,580), '236': (1369,616), '234': (1370,646), '230': (1405,636),
  '228': (1428,636), '226': (1454,646), '224': (1481,647), '218': (1495,659), '216': (1513,627),
  '214': (1532,605), '212': (1557,615), '208': (1593,615),
  # Hudson Valley — east
  '201': (1748,544), '203': (1750,579), '207': (1753,613), '209': (1753,643),
  '215': (1679,725), '243': (1559,696), '273': (1373,705), '269': (1411,738), '261': (1457,770),
  '255': (1546,767), '223': (1632,799), '231': (1548,930),
  # Saratoga — northwest diagonal row
  '714': (969,322), '712': (981,337), '710': (995,350), '708': (1011,363), '706': (1037,342),
  '702': (1052,317), '700': (1048,298), '694': (1069,280), '692': (1083,261), '690': (1110,254),
  '684': (1133,239), '680': (1144,220), 
  '678': (1168,179), '676': (1180,164), '668': (1220,144), '664': (1241,119),
  '660': (1295,215), '560': (1108,548), '645': (1310,312),
  # Saratoga — middle
  '657': (1180,335), '651': (1211,326), '649': (1244,326), '643': (1287,326), '639': (1289,379),
  '648': (1343,302), '646': (1369,289), '644': (1385,306), '642': (1405,324), '640': (1422,342),
  '636': (1444,363), '632': (1480,363), '626': (1528,346),
  '620': (1570,253), '624': (1570,281), '618': (1641,264), '616': (1638,299),
  '600': (1745,410),
  '661': (1173,401), '633': (1330,416), 'K110': (1432,409),
  '617': (1515,411), '615': (1547,410), '629': (1369,439), '625': (1422,439), '621': (1469,439),
  '619': (1506,431), '611': (1573,426), '607': (1605,424), '601': (1637,432),
  '681': (1017,428), '677': (1036,428), '673': (1053,424), '669': (1070,422), '665': (1087,421),
  '542': (1078,459), '544': (1080,493), '548': (1095,521), '550': (1095,539),
  '584': (1210,458), '580': (1210,494), '512': (1191,531), '264': (1165,582),
  'K112': (965,450), '292': (967,502),
  # Hamptons — west row
  '484': (730,974), '480': (742,1009), '470': (770,1061), '460': (824,1120),
  '465': (800,939), '461': (821,964), '449': (839,1009), '447': (841,1030), '445': (850,1048),
  '443': (883,1057), '454': (906,1133), '452': (970,1139), '448': (995,1174),
  # Hamptons — east cluster
  '400': (1130,760), '401': (1021,795), '404': (1110,820), '405': (1000,835), '412': (1085,844),
  '413': (984,863), '419': (972,885), '423': (967,910), '431': (953,942), '433': (956,972),
  '435': (926,998), '439': (981,1028), '441': (974,1060), 'K113': (1000,981),
  '422': (1064,943), '430': (1064,981), '434': (1039,1017), '442': (1067,1072),
  # Niagara
  '101': (1550,1060), '107': (1539,1094), '109': (1530,1115), '111': (1539,1141),
  '112': (1539,1160), '113': (1539,1178), '121': (1539,1195), '123': (1541,1216),
  '127': (1541,1236), '135': (1541,1254), '139': (1541,1270),
  '145': (1506,1342), '147': (1490,1360), '151': (1473,1373), '155': (1456,1391),
  '157': (1436,1409), '161': (1421,1426), '165': (1383,1427), '169': (1364,1443),
  '173': (1348,1458), '177': (1330,1475), '181': (1312,1490),
  '185': (1237,1390), '189': (1193,1339), '191': (1173,1313), '193': (1159,1291),
  '195': (1136,1276), '197': (1117,1259), '199': (1091,1228),
}

# which district each suite belongs to (by number pattern)
def district_of(s):
    if s.startswith('MH') or s == '337': return 'markethall'
    if s.startswith('K'):
        return {'K107':'hudson','K110':'saratoga','K112':'saratoga','K113':'hamptons'}.get(s,'hudson')
    n = int(s)
    if 100 <= n < 200: return 'niagara'
    if 200 <= n < 300: return 'hudson'
    if 300 <= n < 400: return 'hudson'
    if 400 <= n < 500: return 'hamptons'
    if 500 <= n < 720: return 'saratoga'
    if 800 <= n < 1000: return 'adirondacks'
    return 'hudson'

# ---------------- walkway graph ----------------
NODES = {
  # Adirondacks upper walkway (Saks -> east entry)
  'A1': (560,205), 'A2': (615,245), 'A3': (668,285), 'A4': (722,318), 'A5': (778,348),
  'A6': (836,370), 'A7': (884,382), 'A8': (930,360),
  # Adirondacks lower walkway (Welcome Center -> Market Hall)
  'L1': (478,483), 'L2': (520,530), 'L3': (558,578), 'L4': (596,626), 'L5': (634,672),
  'L6': (676,712),
  # Gucci/UGG corridor (upper elbow -> Market Hall NE)
  'G1': (836,428), 'G2': (790,485), 'G3': (775,545), 'G4': (790,610), 'G5': (800,660),
  'G6': (786,710),
  # Market Hall ring
  'MN': (712,742), 'ME': (790,760), 'MS': (648,930), 'MW': (596,800),
  # central / gazebo
  'C1': (870,730), 'C2': (940,712),
  # corridor from Adk east entry down past K112 to LOFT/gazebo
  'D1': (965,405), 'D2': (990,470), 'D3': (1000,545), 'D4': (985,620),
  # Hudson Valley main corridor (gazebo -> east)
  'H1': (1060,672), 'H2': (1160,668), 'H3': (1260,668), 'H4': (1350,660), 'H5': (1450,655),
  'H6': (1560,650), 'H7': (1650,635), 'H8': (1700,600),
  # mid corridor (south of Saratoga, north of HV north row)
  'M1': (1090,555), 'M2': (1150,558), 'M3': (1265,552), 'M4': (1390,540), 'M5': (1500,548),
  'M6': (1600,555), 'M7': (1680,560),
  # Saratoga inner corridor (Puma/Reebok row)
  'K1': (1305,405), 'K2': (1400,395), 'K3': (1500,395), 'K4': (1590,398), 'K5': (1680,420),
  # Saratoga north loop
  'N1': (1005,360), 'N2': (1060,330), 'N3': (1120,290), 'N4': (1180,242), 'N5': (1237,192),
  'N6': (1318,278), 'N7': (1368,308), 'N8': (1436,372), 'N9': (1500,352), 'N10': (1558,322),
  'N11': (1600,295), 'N12': (1640,340), 'N13': (1660,380),
  # vertical connector K1 area down to M3
  'V1': (1268,480),
  # southeast chain to Tommy Hilfiger / Niagara
  'SE1': (1445,700), 'SE2': (1495,755), 'SE3': (1530,812), 'SE4': (1488,872),
  'SE5': (1492,950), 'SE6': (1528,1008),
  'CH': (1640,762),
  # Hamptons
  'HA1': (688,948), 'HA2': (742,995), 'HA3': (790,1042), 'HA4': (836,1086), 'HA5': (890,1108),
  'HA6': (958,1116), 'HA7': (1006,1140), 'HA8': (1030,1190),
  # Hamptons north-south link (east cluster corridor)
  'P1': (1078,712), 'P2': (1072,778), 'P3': (1048,842), 'P4': (1028,902), 'P5': (1016,962),
  'P6': (1004,1022), 'P7': (985,1080),
  'PE': (1130,912),   # east entry from Blue lot 1-11
  # Niagara loop
  'X1': (1068,1232), 'X2': (1122,1284), 'X3': (1176,1330), 'X4': (1232,1372),
  'X5': (1290,1416), 'X6': (1348,1452), 'X7': (1408,1420), 'X8': (1462,1388),
  'X9': (1498,1340), 'X10': (1508,1272), 'X11': (1512,1195), 'X12': (1515,1120),
  'X13': (1520,1055),
}
EDGES = [
 ('A1','A2'),('A2','A3'),('A3','A4'),('A4','A5'),('A5','A6'),('A6','A7'),('A7','A8'),
 ('A6','G1'),('A7','G1'),
 ('L1','L2'),('L2','L3'),('L3','L4'),('L4','L5'),('L5','L6'),('L6','MN'),
 ('G1','G2'),('G2','G3'),('G3','G4'),('G4','G5'),('G5','G6'),('G6','ME'),('G6','MN'),
 ('L6','MW'),('MW','MS'),('MS','HA1'),('MN','ME'),
 ('ME','C1'),('C1','C2'),('G5','C1'),
 ('A8','D1'),('D1','D2'),('D2','D3'),('D3','D4'),('D4','C2'),
 ('D3','M1'),
 ('C2','H1'),('H1','H2'),('H2','H3'),('H3','H4'),('H4','H5'),('H5','H6'),('H6','H7'),('H7','H8'),
 ('M1','M2'),('M2','M3'),('M3','M4'),('M4','M5'),('M5','M6'),('M6','M7'),('M7','H8'),
 ('M2','H2'),('M6','H6'),
 ('K1','K2'),('K2','K3'),('K3','K4'),('K4','K5'),
 ('K1','V1'),('V1','M3'),
 ('A8','N1'),('N1','N2'),('N2','N3'),('N3','N4'),('N4','N5'),('N5','N6'),('N6','N7'),
 ('N7','N8'),('N8','N9'),('N9','N10'),('N10','N11'),('N11','N12'),('N12','N13'),('N13','K5'),
 ('N7','K1'),('N8','K2'),('N1','D1'),
 ('H7','CH'),('CH','SE3'),
 ('H5','SE1'),('SE1','SE2'),('SE2','SE3'),('SE3','SE4'),('SE4','SE5'),('SE5','SE6'),
 ('SE6','X13'),
 ('HA1','HA2'),('HA2','HA3'),('HA3','HA4'),('HA4','HA5'),('HA5','HA6'),('HA6','HA7'),
 ('HA7','HA8'),('HA8','X1'),
 ('H1','P1'),('P1','P2'),('P2','P3'),('P3','P4'),('P4','P5'),('P5','P6'),('P6','P7'),
 ('P7','HA6'),('PE','P4'),
 ('X1','X2'),('X2','X3'),('X3','X4'),('X4','X5'),('X5','X6'),('X6','X7'),('X7','X8'),
 ('X8','X9'),('X9','X10'),('X10','X11'),('X11','X12'),('X12','X13'),
]

# entries (walk-in points from parking) -> nearest graph node + label
ENTRIES = {
  'welcome': {'node':'L1','xy':(467,478)},
  'adk_east': {'node':'A8','xy':(930,356)},
  'saratoga_n': {'node':'N5','xy':(1244,172)},
  'saratoga_ne': {'node':'N11','xy':(1605,281)},
  'hv_se': {'node':'SE3','xy':(1528,826)},
  'niagara_n': {'node':'SE6','xy':(1560,1010)},
  'hamptons_e': {'node':'PE','xy':(1150,905)},
  'hamptons_s': {'node':'HA8','xy':(1026,1117)},
  'shake': {'node':'X1','xy':(1044,1236)},
}

PARKING = [
  {'id':'green3151','name':'Green Parking Lot 31–51','color':'#2d5b2d','node':'A1','xy':(340,240)},
  {'id':'green2630','name':'Green Parking Lot 26–30','color':'#2d5b2d','node':'L1','xy':(360,600)},
  {'id':'gold1925','name':'Gold Parking Lot 19–25','color':'#f39c2c','node':'HA4','xy':(640,1190)},
  {'id':'blue111','name':'Blue Parking Lot 1–11','color':'#4a5fc0','node':'PE','xy':(1230,975)},
  {'id':'blue1213','name':'Blue Parking Lot 12–13','color':'#4a5fc0','node':'X1','xy':(1095,1390)},
  {'id':'red5866','name':'Red Parking Lot 58–66','color':'#cc1236','node':'N5','xy':(1360,120)},
  {'id':'deck','name':'Parking Deck','color':'#444444','node':'N11','xy':(1660,150)},
]

AMENITIES = [
  {'id':'welcome','name':'Welcome Center','icon':'ℹ️','xy':(419,448),'node':'L1'},
  {'id':'markethall','name':'Market Hall Food Court','icon':'🍽️','xy':(693,830),'node':'MS'},
  {'id':'gazebo','name':'Gazebo','icon':'🏛️','xy':(940,700),'node':'C2'},
  {'id':'rr_adk','name':'Restrooms — Adirondacks','icon':'🚻','xy':(592,262),'node':'A2'},
  {'id':'rr_fam_adk','name':'Family Restroom — Adirondacks','icon':'🚻','xy':(873,324),'node':'A7'},
  {'id':'rr_sar','name':'Family Restroom — Saratoga','icon':'🚻','xy':(1279,450),'node':'K1'},
  {'id':'rr_hv','name':'Family Restroom — Hudson Valley','icon':'🚻','xy':(1628,550),'node':'M7'},
  {'id':'rr_ham','name':'Family Restroom — Hamptons','icon':'🚻','xy':(891,1015),'node':'HA5'},
  {'id':'rr_nia','name':'Restrooms — Niagara','icon':'🚻','xy':(1322,1433),'node':'X6'},
  {'id':'rr_tommy','name':'Family Restroom — near Tommy Hilfiger','icon':'🚻','xy':(1542,1006),'node':'SE6'},
  {'id':'atm_adk','name':'ATM — Adirondacks','icon':'🏧','xy':(574,280),'node':'A2'},
  {'id':'atm_sar','name':'ATM — Saratoga','icon':'🏧','xy':(1158,273),'node':'N3'},
  {'id':'atm_hv','name':'ATM — Hudson Valley','icon':'🏧','xy':(1137,690),'node':'H1'},
]

DISTRICTS = {
 'adirondacks': {'name':'Adirondacks','color':'#2d5b2d',
   'poly':[(420,60),(660,60),(700,120),(920,230),(940,330),(900,420),(800,460),(790,640),(700,700),(620,700),(430,500),(390,430),(560,390),(470,300)]},
 'saratoga': {'name':'Saratoga','color':'#cc1236',
   'poly':[(950,340),(1140,190),(1240,100),(1310,160),(1440,250),(1600,230),(1680,250),(1700,320),(1790,360),(1790,470),(1600,480),(1300,500),(1230,560),(1130,560),(1040,470),(950,440)]},
 'hudson': {'name':'Hudson Valley','color':'#6b4a2f',
   'poly':[(720,470),(900,440),(960,470),(960,560),(1130,570),(1230,570),(1300,545),(1610,570),(1700,520),(1790,520),(1790,660),(1700,680),(1660,820),(1600,850),(1500,990),(1470,950),(1450,800),(1360,740),(1200,770),(1080,700),(940,730),(820,850),(770,780),(810,690),(720,640)]},
 'hamptons': {'name':'Hamptons','color':'#f39c2c',
   'poly':[(700,930),(950,760),(1010,760),(1150,790),(1150,940),(1100,1110),(1030,1210),(950,1200),(880,1130),(700,1100)]},
 'niagara': {'name':'Niagara','color':'#4a5fc0',
   'poly':[(1040,1210),(1120,1230),(1240,1330),(1330,1400),(1420,1370),(1480,1300),(1500,1030),(1600,1020),(1610,1300),(1450,1460),(1380,1580),(1290,1470),(1160,1380),(1050,1290)]},
 'markethall': {'name':'Market Hall','color':'#8a8a8a',
   'poly':[(560,700),(700,690),(800,720),(830,790),(700,980),(620,980),(540,880),(540,760)]},
}

# ---------------- directory parsing ----------------
def parse_directory(path):
    txt = open(path).read()
    lines = txt.splitlines()
    stores = []
    cell_re = re.compile(r'(K1\d\d|MH\d{0,2}|\d{3})\s{2,}(.+)')
    for li, line in enumerate(lines[:105]):
        # split into cells on 3+ spaces, track offsets
        for m in re.finditer(r'(?:^|(?<=^\s)|(?<=\s{2}))(K1\d\d|MH\d{0,2}|\d{3})\s+(\S.*?)(?=\s{2,}[\d(]|\s*$)', line):
            suite, name = m.group(1), m.group(2).strip()
            name = re.sub(r'\s{2,}', ' ', name)
            name = re.sub(r'\s+\(?\d[\d\s()\-]*$', '', name)
            name = name.rstrip('*').strip()
            if not name or len(name) < 2 or not re.search(r'[A-Za-z]', name): continue
            if m.start(1) > 2 and line[m.start(1)-3] not in ' \t': continue
            offset = m.start(1)
            stores.append({'suite': suite, 'name': name, 'line': li+1, 'off': offset})
    return stores

def categorize(s):
    off, line = s['off'], s['line']
    if off < 55: return 'Fashion & Sportswear'
    if off < 125: return 'Fashion & Sportswear'
    if off < 190: return 'Shoes' if line >= 45 else 'Fashion & Sportswear'
    if off < 253: return 'Kids' if line >= 87 else ('Accessories & Jewelry' if line >= 13 else 'Fashion & Sportswear')
    if off < 320:
        if line <= 5: return 'Kids'
        if line <= 25: return 'Luggage & Leather'
        if line <= 52: return 'Home'
        return 'Beauty & Gifts'
    return 'Food & Drink'

stores = parse_directory('directory.txt')
for s in stores:
    s['cat'] = categorize(s)
    del s['off']; del s['line']

# dedupe identical suite+name
seen = set(); uniq = []
for s in stores:
    k = (s['suite'], s['name'].lower())
    if k in seen: continue
    seen.add(k); uniq.append(s)
stores = uniq

# attach coords
missing = []
for s in stores:
    xy = SUITES.get(s['suite'])
    if xy: s['x'], s['y'] = xy
    else: missing.append(s)
print(f"{len(stores)} stores parsed, {len(missing)} missing coords:")
for s in missing: print('  ', s['suite'], s['name'], s['cat'])

# nearest graph node per store
def nearest_node(x, y):
    best, bd = None, 1e18
    for nid,(nx,ny) in NODES.items():
        d = (nx-x)**2 + (ny-y)**2
        if d < bd: bd, best = d, nid
    return best
for s in stores:
    if 'x' in s:
        s['node'] = nearest_node(s['x'], s['y'])
        s['district'] = district_of(s['suite'])

data = {
  'nodes': NODES, 'edges': EDGES, 'stores': stores, 'districts': DISTRICTS,
  'parking': PARKING, 'amenities': AMENITIES, 'entries': ENTRIES, 'suites': SUITES,
}
json.dump(data, open('data.json','w'))
print('categories:', {c: sum(1 for s in stores if s['cat']==c) for c in set(s['cat'] for s in stores)})

# ---------------- verification overlay ----------------
im = Image.open('map_clean.jpg').convert('RGB')
d = ImageDraw.Draw(im, 'RGBA')
for dk, dv in DISTRICTS.items():
    d.polygon(dv['poly'], outline=(255,0,255,255))
for a,b in EDGES:
    d.line([NODES[a], NODES[b]], fill=(0,120,255,255), width=5)
for nid,(x,y) in NODES.items():
    d.ellipse((x-7,y-7,x+7,y+7), fill=(0,60,220,255))
    d.text((x+8,y-14), nid, fill=(0,0,180,255))
for sid,(x,y) in SUITES.items():
    d.ellipse((x-4,y-4,x+4,y+4), fill=(255,0,0,255))
im.save('verify_overlay.jpg', quality=80)
print('overlay written')
