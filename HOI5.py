#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOI5 Prototype: Europe 1991 — SEPARATISM & ECONOMY
Natural Earth admin1, batched draw, spatial grid, full separatist mechanics.
Windows 98 style, pure Python + tkinter.
"""

import json, random, math
import tkinter as tk
from tkinter import font, messagebox, simpledialog

# ---------------------------------------------------------------------------
# FAST JSON
# ---------------------------------------------------------------------------
try:
    import orjson as _json
    def load_json(path):
        with open(path, 'rb') as f:
            return _json.loads(f.read())
except Exception:
    def load_json(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

# ---------------------------------------------------------------------------
# DATA & MAPPINGS
# ---------------------------------------------------------------------------
EUROPE_ISO3 = {
    'AND','ALB','AUT','BIH','BEL','BGR','BLR','CHE','CYP','CZE',
    'DEU','DNK','EST','ESP','FIN','FRA','GBR','GRC','HRV','HUN',
    'IRL','ISL','ITA','LTU','LUX','LVA','MDA','MKD','MLT','MNE',
    'NLD','NOR','POL','PRT','ROU','SRB','RUS','SWE','SVK','SVN',
    'TUR','UKR'
}

CODE_TO_COUNTRY = {
    'AND':'Andorra','ALB':'Albania','AUT':'Austria','BIH':'Bosnia and Herz.',
    'BEL':'Belgium','BGR':'Bulgaria','BLR':'Belarus','CHE':'Switzerland',
    'CYP':'Cyprus','CZE':'Czech Republic','DEU':'Germany','DNK':'Denmark',
    'EST':'Estonia','ESP':'Spain','FIN':'Finland','FRA':'France',
    'GBR':'United Kingdom','GRC':'Greece','HRV':'Croatia','HUN':'Hungary',
    'IRL':'Ireland','ISL':'Iceland','ITA':'Italy','LTU':'Lithuania',
    'LUX':'Luxembourg','LVA':'Latvia','MDA':'Moldova','MKD':'Macedonia',
    'MLT':'Malta','MNE':'Montenegro','NLD':'Netherlands','NOR':'Norway',
    'POL':'Poland','PRT':'Portugal','ROU':'Romania','SRB':'Serbia',
    'RUS':'Russia','SWE':'Sweden','SVK':'Slovakia','SVN':'Slovenia',
    'TUR':'Turkey','UKR':'Ukraine',
}

OWNER_MAP = {
    'RUS':'USSR','UKR':'USSR','BLR':'USSR','MDA':'USSR',
    'EST':'USSR','LVA':'USSR','LTU':'USSR',
    'CZE':'Czechoslovakia','SVK':'Czechoslovakia',
    'SVN':'Yugoslavia','HRV':'Yugoslavia','BIH':'Yugoslavia',
    'MKD':'Yugoslavia','MNE':'Yugoslavia','SRB':'Yugoslavia',
}

OWNER_COLORS = {
    'USSR':'#CC3333','Yugoslavia':'#3366CC','Czechoslovakia':'#990000',
    'Germany':'#FFCC00','Poland':'#DC143C','France':'#0055A4',
    'United Kingdom':'#00247D','Italy':'#006600','Spain':'#AA151B',
    'Turkey':'#E30A17','Greece':'#0D5EAF','Romania':'#FCD116',
    'Hungary':'#436F4D','Bulgaria':'#FFFFFF','Albania':'#C41E3A',
    'Sweden':'#006AA7','Norway':'#EF2B2D','Finland':'#003580',
    'Denmark':'#C60C30','Ireland':'#169B62','Portugal':'#FF0000',
    'Netherlands':'#21468B','Belgium':'#000000','Austria':'#ED2939',
    'Switzerland':'#FF0000','Cyprus':'#D57800','Luxembourg':'#00A1DE',
    'Malta':'#CF142B','Iceland':'#02529C','Andorra':'#0018A8',
    'Serbia':'#C6363C','Macedonia':'#D20000','Montenegro':'#C8102E',
    'Bosnia and Herz.':'#002395','Croatia':'#171796','Slovenia':'#FF0000',
    'Belarus':'#009A3D','Ukraine':'#005BBB','Moldova':'#0033A0',
    'Estonia':'#0072CE','Latvia':'#9E3039','Lithuania':'#C1272D',
    'Czech Republic':'#11457E','Slovakia':'#0B4EA2',
}

BLOCKS = {
    'USSR':'Warsaw Pact','Poland':'Warsaw Pact','Czechoslovakia':'Warsaw Pact',
    'Hungary':'Warsaw Pact','Romania':'Warsaw Pact','Bulgaria':'Warsaw Pact',
    'Albania':'Warsaw Pact','Yugoslavia':'Non-Aligned',
    'Germany':'NATO','France':'NATO','United Kingdom':'NATO','Italy':'NATO',
    'Spain':'NATO','Portugal':'NATO','Netherlands':'NATO','Belgium':'NATO',
    'Luxembourg':'NATO','Denmark':'NATO','Norway':'NATO','Greece':'NATO',
    'Turkey':'NATO','Iceland':'NATO',
    'Sweden':'Neutral','Finland':'Neutral','Ireland':'Neutral',
    'Austria':'Neutral','Switzerland':'Neutral','Cyprus':'Neutral',
    'Malta':'Neutral','Andorra':'Neutral',
    'Estonia':'Warsaw Pact','Latvia':'Warsaw Pact','Lithuania':'Warsaw Pact',
    'Ukraine':'Warsaw Pact','Belarus':'Warsaw Pact','Moldova':'Warsaw Pact',
    'Czech Republic':'Warsaw Pact','Slovakia':'Warsaw Pact',
    'Slovenia':'Non-Aligned','Croatia':'Non-Aligned',
    'Bosnia and Herz.':'Non-Aligned','Macedonia':'Non-Aligned',
    'Serbia':'Non-Aligned','Montenegro':'Non-Aligned',
    'Russia':'Neutral',
}

BASE_DISSENT = {
    'Estonia':40,'Latvia':35,'Lithuania':45,'Ukraine':20,'Belarus':10,
    'Moldova':15,'Russia':0,
    'Slovenia':30,'Croatia':25,'Bosnia and Herz.':15,'Macedonia':8,
    'Montenegro':3,'Serbia':0,'Kosovo':25,
    'Czech Republic':5,'Slovakia':6,
    'Scotland':20,'Wales':15,'Northern Ireland':35,  # conceptual
}

# Currencies by owner country
CURRENCIES = {
    'USSR':'руб.','United Kingdom':'£','Germany':'DM','France':'₣',
    'Italy':'₤','Spain':'₧','Poland':'zł','Yugoslavia':'дин.',
    'Czechoslovakia':'Kčs','Hungary':'Ft','Romania':'lei','Bulgaria':'лв',
    'Albania':'lek','Greece':'₯','Turkey':'₺','Sweden':'kr','Norway':'kr',
    'Denmark':'kr','Finland':'mk','Netherlands':'ƒ','Belgium':'₣','Austria':'Sch',
    'Switzerland':'₣','Portugal':'₰','Ireland':'£','Luxembourg':'₣',
    'Iceland':'kr','Cyprus':'£','Malta':'₤','Andorra':'₣',
    'Estonia':'руб.','Latvia':'руб.','Lithuania':'руб.','Belarus':'руб.',
    'Ukraine':'руб.','Moldova':'руб.','Russia':'руб.',
    'Czech Republic':'Kčs','Slovakia':'Kčs',
    'Slovenia':'дин.','Croatia':'дин.','Bosnia and Herz.':'дин.',
    'Macedonia':'дин.','Serbia':'дин.','Montenegro':'дин.',
}

def get_currency(owner):
    return CURRENCIES.get(owner, 'coins')

# ---------------------------------------------------------------------------
# UTILS
# ---------------------------------------------------------------------------
def generate_color(seed: str) -> str:
    rand = random.Random(seed)
    r = rand.randint(90, 210)
    g = rand.randint(90, 210)
    b = rand.randint(90, 210)
    return f'#{r:02x}{g:02x}{b:02x}'


def point_in_polygon(x, y, poly):
    inside = False
    n = len(poly)
    if n == 0:
        return False
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


# ---------------------------------------------------------------------------
# APP
# ---------------------------------------------------------------------------
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("HOI5: 1991 — SEPARATISM")
        root.geometry("1360x940")
        root.configure(bg='#c0c0c0')

        self.font = font.Font(family="MS Sans Serif", size=9)
        self.font_bold = font.Font(family="MS Sans Serif", size=9, weight="bold")
        self.font_title = font.Font(family="MS Sans Serif", size=12, weight="bold")

        self.selected = None
        self.highlighted = None
        self.date = {"day": 1, "month": 1, "year": 1991}
        self.turn = 1
        self.map_mode = 'political'

        self.min_lon = -12.0
        self.max_lon = 42.0
        self.min_lat = 33.0
        self.max_lat = 73.0
        self.map_w = 980
        self.map_h = 720
        self.scale_x = self.map_w / (self.max_lon - self.min_lon)
        self.scale_y = self.map_h / (self.max_lat - self.min_lat)

        self.grid_step = 50
        self.spatial_grid = {}
        self._draw_queue = []
        self._drawing = False
        self.regions = []
        self.owner_colors = {}

        # Player state
        self.player = None          # chosen owner name
        self.budget = 0
        self.currency = 'coins'
        self.income = 100           # base income per turn

        self.build_ui()
        self.show_nation_picker()

    # ------------------------------------------------------------------
    def build_ui(self):
        # Toolbar
        toolbar = tk.Frame(self.root, bg='#c0c0c0', relief='raised', bd=2)
        toolbar.pack(side='top', fill='x', padx=4, pady=2)

        tk.Button(toolbar, text='⏵ Next Turn', command=self.next_turn,
                  bg='#c0c0c0', font=self.font, relief='raised', bd=2).pack(side='left', padx=2, pady=2)
        tk.Button(toolbar, text='🗺 Political', command=lambda: self.set_map_mode('political'),
                  bg='#c0c0c0', font=self.font, relief='raised', bd=2).pack(side='left', padx=2, pady=2)
        tk.Button(toolbar, text='💰 Economic', command=lambda: self.set_map_mode('economic'),
                  bg='#c0c0c0', font=self.font, relief='raised', bd=2).pack(side='left', padx=2, pady=2)
        tk.Button(toolbar, text='⚔ Military', command=lambda: self.set_map_mode('military'),
                  bg='#c0c0c0', font=self.font, relief='raised', bd=2).pack(side='left', padx=2, pady=2)

        self.lbl_budget = tk.Label(toolbar, text='Select nation →', bg='#c0c0c0',
                                     fg='#800000', font=self.font_bold)
        self.lbl_budget.pack(side='left', padx=10)

        self.lbl_title = tk.Label(toolbar, text='IRON CURTAIN: 1991 — SEPARATISM',
                                  bg='#c0c0c0', fg='#000080', font=self.font_title)
        self.lbl_title.pack(side='right', padx=10)

        # Main
        main = tk.Frame(self.root, bg='#c0c0c0')
        main.pack(side='top', fill='both', expand=True, padx=4, pady=4)

        # Left
        left = tk.Frame(main, bg='#c0c0c0', width=240)
        left.pack(side='left', fill='y', padx=2, pady=2)
        left.pack_propagate(False)
        lf = tk.Frame(left, bg='#c0c0c0', relief='sunken', bd=2)
        lf.pack(fill='both', expand=True, padx=2, pady=2)
        tk.Label(lf, text=' NATIONS', bg='#000080', fg='white',
                 font=self.font_bold, anchor='w').pack(fill='x')
        self.nation_list = tk.Listbox(lf, bg='white', fg='black', font=self.font,
                                      selectmode='single', exportselection=False,
                                      relief='sunken', bd=1)
        self.nation_list.pack(fill='both', expand=True, padx=4, pady=4)
        self.nation_list.bind('<<ListboxSelect>>', self.on_nation_select)

        # Center
        center = tk.Frame(main, bg='#c0c0c0', relief='sunken', bd=2)
        center.pack(side='left', fill='both', expand=True, padx=4, pady=2)
        self.canvas = tk.Canvas(center, bg='#87CEEB', width=self.map_w, height=self.map_h,
                               highlightthickness=0)
        self.canvas.pack(padx=2, pady=2)

        # Right
        right = tk.Frame(main, bg='#c0c0c0', width=300)
        right.pack(side='right', fill='y', padx=2, pady=2)
        right.pack_propagate(False)
        rf = tk.Frame(right, bg='#c0c0c0', relief='sunken', bd=2)
        rf.pack(fill='both', expand=True, padx=2, pady=2)
        tk.Label(rf, text=' REGION INFO', bg='#000080', fg='white',
                 font=self.font_bold, anchor='w').pack(fill='x')

        self.info_region = tk.Label(rf, text='Region: –', bg='#c0c0c0', font=self.font, anchor='w')
        self.info_region.pack(fill='x', padx=8, pady=1)
        self.info_country = tk.Label(rf, text='Country: –', bg='#c0c0c0', font=self.font, anchor='w')
        self.info_country.pack(fill='x', padx=8, pady=1)
        self.info_owner = tk.Label(rf, text='Owner: –', bg='#c0c0c0', font=self.font, anchor='w')
        self.info_owner.pack(fill='x', padx=8, pady=1)
        self.info_block = tk.Label(rf, text='Block: –', bg='#c0c0c0', font=self.font, anchor='w')
        self.info_block.pack(fill='x', padx=8, pady=1)
        self.info_dissent = tk.Label(rf, text='Dissent: –', bg='#c0c0c0', font=self.font, anchor='w')
        self.info_dissent.pack(fill='x', padx=8, pady=1)
        self.info_pop = tk.Label(rf, text='Population: –', bg='#c0c0c0', font=self.font, anchor='w')
        self.info_pop.pack(fill='x', padx=8, pady=1)
        self.info_status = tk.Label(rf, text='Status: –', bg='#c0c0c0', font=self.font, anchor='w')
        self.info_status.pack(fill='x', padx=8, pady=1)

        sep = tk.Frame(rf, bg='#808080', height=2, relief='sunken', bd=1)
        sep.pack(fill='x', padx=4, pady=6)

        # Action buttons (shown only when region selected)
        self.btn_fund = tk.Button(rf, text='💰 Fund Separatists', command=self.on_fund,
                                  bg='#c0c0c0', font=self.font, relief='raised', bd=2, state='disabled')
        self.btn_fund.pack(fill='x', padx=8, pady=2)

        self.btn_stabilize = tk.Button(rf, text='🛡 Stabilize', command=self.on_stabilize,
                                       bg='#c0c0c0', font=self.font, relief='raised', bd=2, state='disabled')
        self.btn_stabilize.pack(fill='x', padx=8, pady=2)

        self.lbl_orders = tk.Label(rf, text='Select a region.',
                                   bg='#c0c0c0', fg='#555555', font=self.font,
                                   wraplength=260, justify='left')
        self.lbl_orders.pack(fill='x', padx=8, pady=4)

        # Status bar
        self.status = tk.Frame(self.root, bg='#c0c0c0', relief='sunken', bd=1)
        self.status.pack(side='bottom', fill='x')
        self.status_left = tk.Label(self.status, text='', bg='#c0c0c0', font=self.font, anchor='w')
        self.status_left.pack(side='left', padx=4)

    # ------------------------------------------------------------------
    def show_nation_picker(self):
        """Modal Win98-style nation picker."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Choose Your Nation")
        dlg.geometry("360x420")
        dlg.configure(bg='#c0c0c0')
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text=' SELECT YOUR NATION', bg='#000080', fg='white',
                 font=self.font_bold, anchor='w').pack(fill='x', padx=4, pady=4)

        lb = tk.Listbox(dlg, bg='white', fg='black', font=self.font, relief='sunken', bd=1)
        lb.pack(fill='both', expand=True, padx=8, pady=4)

        # Available major nations (sorted)
        nations = sorted(OWNER_COLORS.keys())
        for n in nations:
            lb.insert('end', n)

        def on_ok():
            sel = lb.curselection()
            if not sel:
                return
            self.player = lb.get(sel[0])
            self.currency = get_currency(self.player)
            self.budget = 2000  # starting budget
            self.update_budget_label()
            dlg.destroy()
            self.update_status("Loading data...")
            self.root.after(100, self._start_background_load)

        def on_cancel():
            dlg.destroy()
            self.root.destroy()

        btn_frame = tk.Frame(dlg, bg='#c0c0c0')
        btn_frame.pack(fill='x', padx=8, pady=8)
        tk.Button(btn_frame, text='OK', command=on_ok,
                  bg='#c0c0c0', font=self.font, relief='raised', bd=2, width=10).pack(side='left')
        tk.Button(btn_frame, text='Cancel', command=on_cancel,
                  bg='#c0c0c0', font=self.font, relief='raised', bd=2, width=10).pack(side='right')

        # Select USSR by default (index 0 if sorted alphabetically — not always)
        # Find USSR
        try:
            idx = nations.index('USSR')
            lb.selection_set(idx)
            lb.see(idx)
        except ValueError:
            pass

    # ------------------------------------------------------------------
    def update_budget_label(self):
        self.lbl_budget.config(text=f"Budget: {self.budget:,} {self.currency}")

    # ------------------------------------------------------------------
    def update_status(self, extra=""):
        d = f"{self.date['day']:02d}.{self.date['month']:02d}.{self.date['year']}"
        regions = getattr(self, 'regions', [])
        base = f'Date: {d}  |  Turn: {self.turn}  |  Regions: {len(regions)}'
        self.status_left.config(text=base + (f"  |  {extra}" if extra else ""))

    # ------------------------------------------------------------------
    def _start_background_load(self):
        data = load_json('ne_10m_admin1.json')

        self.update_status("Projecting regions...")
        self.root.update_idletasks()

        owners = set()
        total_pts = 0

        for feat in data['features']:
            props = feat['properties']
            cc = props.get('adm0_a3', '')
            if cc not in EUROPE_ISO3:
                continue
            region_name = props.get('name', 'Unknown')
            country = CODE_TO_COUNTRY.get(cc, cc)
            owner = OWNER_MAP.get(cc, country)
            owners.add(owner)

            geom = feat['geometry']
            polys = []
            if geom['type'] == 'Polygon':
                for ring in geom['coordinates']:
                    pts = [(float(lon), float(lat)) for lon, lat in ring]
                    polys.append(pts)
                    total_pts += len(pts)
            elif geom['type'] == 'MultiPolygon':
                for mpoly in geom['coordinates']:
                    for ring in mpoly:
                        pts = [(float(lon), float(lat)) for lon, lat in ring]
                        polys.append(pts)
                        total_pts += len(pts)

            canvas_polys = []
            bbox = [1e9, 1e9, -1e9, -1e9]
            for poly in polys:
                proj = []
                for lon, lat in poly:
                    x = (lon - self.min_lon) * self.scale_x
                    y = (self.max_lat - lat) * self.scale_y
                    proj.append((x, y))
                    if x < bbox[0]: bbox[0] = x
                    if y < bbox[1]: bbox[1] = y
                    if x > bbox[2]: bbox[2] = x
                    if y > bbox[3]: bbox[3] = y
                canvas_polys.append(proj)

            # dynamic state
            pop = random.Random(region_name).randint(50_000, 4_000_000)
            base_diss = BASE_DISSENT.get(country, 0)
            # add slight randomness to starting dissent
            start_diss = min(100, max(0, base_diss + random.Random(region_name).randint(-5, 5)))

            self.regions.append({
                'name': region_name,
                'country': country,
                'owner': owner,
                'cc': cc,
                'polys': canvas_polys,
                'bbox': bbox,
                'oids': [],
                'population': pop,
                'dissent': start_diss,
                'funded_by': None,   # player who funded separatists here
            })

        self.owner_colors = {}
        for o in sorted(owners):
            self.owner_colors[o] = OWNER_COLORS.get(o, generate_color(o))

        self.update_status(f"Built {len(self.regions)} regions, {total_pts} pts. Indexing...")
        self.root.update_idletasks()

        self._build_spatial_grid()
        self.populate_nation_list()

        # Grid lines
        for lon in range(-10, 41, 10):
            x = (lon - self.min_lon) * self.scale_x
            self.canvas.create_line(x, 0, x, self.map_h, fill='#70A8C8', dash=(2, 4), tags='grid')
        for lat in range(35, 71, 10):
            y = (self.max_lat - lat) * self.scale_y
            self.canvas.create_line(0, y, self.map_w, y, fill='#70A8C8', dash=(2, 4), tags='grid')

        self._draw_queue = list(range(len(self.regions)))
        self._drawing = True
        self._draw_batch(batch_size=120)

    # ------------------------------------------------------------------
    def _build_spatial_grid(self):
        self.spatial_grid.clear()
        step = self.grid_step
        for idx, region in enumerate(self.regions):
            x0, y0, x1, y1 = region['bbox']
            gx0 = max(0, int(x0 // step))
            gy0 = max(0, int(y0 // step))
            gx1 = int(x1 // step) + 1
            gy1 = int(y1 // step) + 1
            for gx in range(gx0, gx1 + 1):
                for gy in range(gy0, gy1 + 1):
                    self.spatial_grid.setdefault((gx, gy), []).append(idx)

    # ------------------------------------------------------------------
    def _draw_batch(self, batch_size=120):
        if not self._draw_queue:
            self._drawing = False
            self.update_status("Ready.")
            self.canvas.bind('<Motion>', self.on_mouse_move)
            self.canvas.bind('<Button-1>', self.on_click)
            return

        count = 0
        while self._draw_queue and count < batch_size:
            idx = self._draw_queue.pop(0)
            region = self.regions[idx]
            color = self.owner_colors.get(region['owner'], generate_color(region['owner']))
            for poly in region['polys']:
                flat = [c for p in poly for c in p]
                oid = self.canvas.create_polygon(
                    flat, fill=color, outline='',
                    tags=('region', region['name'])
                )
                region['oids'].append(oid)
            count += 1

        done = len(self.regions) - len(self._draw_queue)
        self.update_status(f"Drawing map... {done}/{len(self.regions)}")
        self.root.after(1, lambda: self._draw_batch(batch_size))

    # ------------------------------------------------------------------
    def populate_nation_list(self):
        self.nation_list.delete(0, 'end')
        for owner in sorted(self.owner_colors.keys()):
            self.nation_list.insert('end', owner)

    def next_turn(self):
        if self._drawing:
            return
        self.turn += 1
        self.date['day'] += 7
        if self.date['day'] > 30:
            self.date['day'] = 1
            self.date['month'] += 1
            if self.date['month'] > 12:
                self.date['month'] = 1
                self.date['year'] += 1

        # Economy: income from owned regions
        owned = sum(1 for r in self.regions if r['owner'] == self.player)
        self.income = 100 + owned * 15
        self.budget += self.income
        self.update_budget_label()

        # Dissent decay / processing
        for region in self.regions:
            if region['owner'] == self.player:
                # stabilize slowly
                region['dissent'] = max(0, region['dissent'] - 3)
            else:
                # natural decay if not funded
                if region['funded_by'] is None:
                    region['dissent'] = max(0, region['dissent'] - 2)
                # if fully dissent and funded — chance to break away
                if region['dissent'] >= 100 and region['funded_by'] == self.player:
                    self._breakaway(region)

        # Refresh selection UI if active
        if self.selected:
            self._refresh_selection_ui()
        self.set_map_mode(self.map_mode)  # redraw colors if owners changed
        self.update_status(f"Income: +{self.income} {self.currency}")

    def _breakaway(self, region):
        old_owner = region['owner']
        new_owner = region['name'] + ' Republic'
        region['owner'] = new_owner
        region['funded_by'] = None
        region['dissent'] = 0
        # assign color for new micro-state
        if new_owner not in self.owner_colors:
            self.owner_colors[new_owner] = generate_color(new_owner)
        # update nation list
        self.populate_nation_list()
        # flash on map
        for oid in region['oids']:
            self.canvas.itemconfig(oid, fill=self.owner_colors[new_owner])
        # message
        self.lbl_orders.config(
            text=f"🔥 BREAKAWAY! {region['name']} declared independence from {old_owner}!",
            fg='#AA0000'
        )

    def set_map_mode(self, mode):
        if self._drawing:
            return
        self.map_mode = mode
        if mode == 'political':
            for region in self.regions:
                color = self.owner_colors.get(region['owner'], generate_color(region['owner']))
                for oid in region['oids']:
                    self.canvas.itemconfig(oid, fill=color)
        elif mode == 'economic':
            for region in self.regions:
                seed = hash(region['name'] + 'eco')
                rand = random.Random(seed)
                r = rand.randint(50, 220); g = rand.randint(50, 220); b = rand.randint(50, 220)
                color = f'#{r:02x}{g:02x}{b:02x}'
                for oid in region['oids']:
                    self.canvas.itemconfig(oid, fill=color)
        elif mode == 'military':
            for region in self.regions:
                seed = hash(region['name'] + 'mil')
                rand = random.Random(seed)
                v = rand.randint(40, 200)
                color = f'#{v:02x}{v//2:02x}{v//3:02x}'
                for oid in region['oids']:
                    self.canvas.itemconfig(oid, fill=color)
        if self.selected:
            for oid in self.selected['oids']:
                self.canvas.itemconfig(oid, outline='white', width=2)
                self.canvas.tag_raise(oid)

    # ------------------------------------------------------------------
    def _hit_test(self, x, y):
        step = self.grid_step
        gx = int(x // step)
        gy = int(y // step)
        candidates = set()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                candidates.update(self.spatial_grid.get((gx + dx, gy + dy), []))
        for idx in sorted(candidates, reverse=True):
            region = self.regions[idx]
            if x < region['bbox'][0] or x > region['bbox'][2] or y < region['bbox'][1] or y > region['bbox'][3]:
                continue
            for poly in region['polys']:
                if point_in_polygon(x, y, poly):
                    return region
        return None

    def on_mouse_move(self, event):
        if self._drawing:
            return
        x, y = event.x, event.y
        found = self._hit_test(x, y)
        if found:
            self._highlight(found)
            self.canvas.config(cursor='hand2')
        else:
            self._unhighlight()
            self.canvas.config(cursor='')

    def on_click(self, event):
        if self._drawing:
            return
        x, y = event.x, event.y
        found = self._hit_test(x, y)
        if found:
            self._select(found)
        else:
            self._deselect()

    def _highlight(self, region):
        if self.highlighted == region:
            return
        if self.highlighted and self.highlighted != self.selected:
            for oid in self.highlighted['oids']:
                self.canvas.itemconfig(oid, outline='')
        self.highlighted = region
        for oid in region['oids']:
            self.canvas.itemconfig(oid, outline='#FFD700', width=2)
            self.canvas.tag_raise(oid)

    def _unhighlight(self):
        if self.highlighted and self.highlighted != self.selected:
            for oid in self.highlighted['oids']:
                self.canvas.itemconfig(oid, outline='')
        self.highlighted = None

    def _select(self, region):
        if self.selected and self.selected != region:
            for oid in self.selected['oids']:
                self.canvas.itemconfig(oid, outline='')
        self.selected = region
        self.highlighted = region
        for oid in region['oids']:
            self.canvas.itemconfig(oid, outline='white', width=2)
            self.canvas.tag_raise(oid)

        self._refresh_selection_ui()

        try:
            owners = sorted(self.owner_colors.keys())
            idx = owners.index(region['owner'])
            self.nation_list.selection_clear(0, 'end')
            self.nation_list.selection_set(idx)
            self.nation_list.see(idx)
        except ValueError:
            pass

    def _refresh_selection_ui(self):
        region = self.selected
        if not region:
            return
        self.info_region.config(text=f'Region: {region["name"]}')
        self.info_country.config(text=f'Country: {region["country"]}')
        self.info_owner.config(text=f'Owner: {region["owner"]}')
        block = BLOCKS.get(region['owner'], 'Neutral')
        self.info_block.config(text=f'Block: {block}')
        self.info_dissent.config(text=f'Dissent: {region["dissent"]:.0f}%')
        self.info_pop.config(text=f'Population: {region["population"]:,}')

        if region['dissent'] >= 100:
            status = 'REVOLUTION! Ready to break away'
        elif region['dissent'] >= 60:
            status = 'Severe unrest'
        elif region['dissent'] >= 30:
            status = 'Growing separatism'
        elif block == 'Warsaw Pact':
            status = 'Communist Satellite'
        elif block == 'NATO':
            status = 'Democratic Ally'
        else:
            status = 'Neutral / Non-Aligned'
        if region['owner'] != region['country'] and region['cc'] in OWNER_MAP:
            status += ' (Occupied)'
        self.info_status.config(text=f'Status: {status}')

        # Action buttons logic
        if region['owner'] == self.player:
            # Own region
            self.btn_fund.config(state='disabled', text='💰 Fund Separatists')
            cost = max(20, region['population'] // 200000)
            self.btn_stabilize.config(state='normal', text=f'🛡 Stabilize (-{cost} {self.currency})')
        else:
            # Foreign region
            self.btn_stabilize.config(state='disabled', text='🛡 Stabilize')
            cost = max(50, region['population'] // 100000)
            if self.budget >= cost:
                self.btn_fund.config(state='normal', text=f'💰 Fund Sep. ({cost} {self.currency})')
            else:
                self.btn_fund.config(state='disabled', text=f'💰 Fund Sep. ({cost} {self.currency}) — BROKE')

        hint = f'Selected: {region["name"]}, {region["country"]}.\nClick elsewhere to deselect.'
        if region['funded_by'] == self.player:
            hint += '\n✅ You are funding separatists here!'
        self.lbl_orders.config(text=hint, fg='#000000')

    def _deselect(self):
        if self.selected:
            for oid in self.selected['oids']:
                self.canvas.itemconfig(oid, outline='')
        self.selected = None
        self.highlighted = None
        self.info_region.config(text='Region: –')
        self.info_country.config(text='Country: –')
        self.info_owner.config(text='Owner: –')
        self.info_block.config(text='Block: –')
        self.info_dissent.config(text='Dissent: –')
        self.info_pop.config(text='Population: –')
        self.info_status.config(text='Status: –')
        self.lbl_orders.config(text='Select a region.', fg='#555555')
        self.btn_fund.config(state='disabled', text='💰 Fund Separatists')
        self.btn_stabilize.config(state='disabled', text='🛡 Stabilize')
        self.nation_list.selection_clear(0, 'end')

    def on_fund(self):
        if not self.selected or self.selected['owner'] == self.player:
            return
        region = self.selected
        cost = max(50, region['population'] // 100000)
        if self.budget < cost:
            return
        self.budget -= cost
        self.update_budget_label()
        region['funded_by'] = self.player
        boost = random.randint(15, 35)
        region['dissent'] = min(100, region['dissent'] + boost)
        self._refresh_selection_ui()
        self.lbl_orders.config(
            text=f'💸 Funded separatists in {region["name"]}! Dissent +{boost}% ({cost} {self.currency} spent)',
            fg='#008800'
        )

    def on_stabilize(self):
        if not self.selected or self.selected['owner'] != self.player:
            return
        region = self.selected
        cost = max(20, region['population'] // 200000)
        if self.budget < cost:
            return
        self.budget -= cost
        self.update_budget_label()
        region['dissent'] = max(0, region['dissent'] - 25)
        region['funded_by'] = None
        self._refresh_selection_ui()
        self.lbl_orders.config(
            text=f'🛡 Stabilized {region["name"]}! Dissent -25% ({cost} {self.currency} spent)',
            fg='#000088'
        )

    def on_nation_select(self, event):
        if self._drawing:
            return
        sel = self.nation_list.curselection()
        if not sel:
            return
        owner = self.nation_list.get(sel[0])
        for region in self.regions:
            if region['owner'] == owner:
                self._select(region)
                for oid in region['oids']:
                    self.canvas.tag_raise(oid)
                return


# ---------------------------------------------------------------------------
def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == '__main__':
    main()
