import re, io, difflib
import pandas as pd

AR = str.maketrans("٠١٢٣٤٥٦٧٨٩٫٬", "0123456789.,")
def norm(s): return str(s).translate(AR).strip()
def num(s):
    if s is None or (isinstance(s, float) and pd.isna(s)): return None
    if isinstance(s, (int, float)): return float(s)
    t = norm(s)
    m = re.search(r"\d[\d.,]*", t)
    if not m: return None
    tok = m.group().strip(".,")
    if "," in tok and "." in tok:
        if tok.rfind(",") > tok.rfind("."): tok = tok.replace(".", "").replace(",", ".")
        else: tok = tok.replace(",", "")
    elif "," in tok:
        parts = tok.split(",")
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3 and len(parts[0]) <= 3):
            tok = tok.replace(",", "")
        else:
            tok = tok.replace(",", ".")
    try:
        return float(tok)
    except ValueError:
        return None

# ---------- name matching (Arabic/English) ----------
def _fold(t):
    return (t.replace("\u0623", "\u0627").replace("\u0625", "\u0627").replace("\u0622", "\u0627").replace("\u0671", "\u0627")
             .replace("\u0649", "\u064a").replace("\u0626", "\u064a").replace("\u0624", "\u0648").replace("\u0629", "\u0647"))

_FORM = """mg mcg ml gm g iu tab tabs tablet tablets cap caps capsule capsules strip strips
amp amps ampoule ampoules syrup cream ointment drops spray supp sachet sachets vial
inhaler inhalers gel lotion shampoo solution suspension emulsion patch patches
fc ec sc cr sr xl xr im iv inf susp soln dose doses turbuhaler evohaler diskus respimat
nebules pen pens prefilled cartridge cartridges powder infusion for
film coated enteric soft hard nasal
دوسي دوسيس توربوهالير تيربوهالر جرعه جرعات قلم اقلام انبوله
مجم ملجم جم جرام مل قرص أقراص كبسولة كبسولات شريط شرائط أمبول امبولات شراب نقط قطرة
كريم مرهم بخاخ لبوس تحاميل فيال زجاجة"""
FORM_WORDS = set(_fold(w) for w in _FORM.split())

# canonical English key -> common Arabic name. Covers the common Egyptian pharmacy
# brands; the manual linking panel + روابط.xlsx file cover anything missing from it.
_ALIAS_AR = {
    "panadol": "بانادول", "panadol extra": "بانادول اكسترا", "brufen": "بروفين",
    "cataflam": "كاتافلام", "voltaren": "فولتارين", "aspirin": "اسبرين",
    "aspocid": "اسبوكسيد", "cetal": "سيتال", "solpadeine": "سولبادين",
    "ketofan": "كيتوفان", "mobic": "موبيك", "celebrex": "سيليبريكس",
    "arcoxia": "اركوكسيا", "diclac": "ديكلاك", "rapidus": "رابيدوس",
    "paracetamol": "باراسيتامول", "ibuprofen": "ايبوبروفين", "diclofenac": "ديكلوفيناك",
    "augmentin": "اوجمنتين", "zithromax": "زيثروماكس", "ciprocin": "سيبروسين",
    "flagyl": "فلاجيل", "amoxil": "اموكسيل", "amoxicillin": "اموكسيسيلين",
    "klacid": "كلاسيد", "suprax": "سوبراكس", "unasyn": "يوناسين",
    "vibramycin": "فيبراميسين", "erythrocin": "اريثروميسين", "hi-biotic": "هاي بيوتك",
    "megamox": "ميجاموكس", "tarivid": "تاريفيد", "rocephin": "روسيفين",
    "keflex": "كيفلكس", "zinnat": "زينات", "dalacin": "دالاسين",
    "amrizole": "امريزول", "metronidazole": "ميترونيدازول",
    "nexium": "نيكسيوم", "zantac": "زانتاك", "losec": "لوزيك",
    "pantoloc": "بانتولوك", "controloc": "كونترولوك", "omeprazole": "اوميبرازول",
    "motilium": "موتيليوم", "imodium": "ايموديوم", "smecta": "سميكتا",
    "buscopan": "باسكوبان", "librax": "ليبراكس", "colona": "كولونا",
    "dicetel": "دايسيتيل", "duphalac": "دوفالاك", "gaviscon": "جافيسكون",
    "famotidine": "فاموتيدين", "coloverin": "كولوفيرين", "antinal": "انتينال",
    "entocid": "انتوسيد", "forlax": "فورلاكس", "enterol": "انتيرول",
    "linex": "لينكس",
    "concor": "كونكور", "amlor": "املور", "norvasc": "نورفاسك",
    "coversyl": "كوفرسيل", "zestril": "زيستريل", "capoten": "كابوتين",
    "diovan": "ديوفان", "atacand": "اتاكاند", "micardis": "ميكارديس",
    "losartan": "لوزارتان", "plavix": "بلافيكس", "brilinta": "بريلينتا",
    "cordarone": "كوردارون", "isoptin": "ايزوبتين", "inderal": "اندرال",
    "tenormin": "تينورمين", "tritace": "تريتاس", "lasix": "لازيكس",
    "aldactone": "الداكتون", "natrilix": "ناتريليكس", "cardura": "كارديورا",
    "isoket": "ايزوكيت", "lanoxin": "لانوكسين",
    "lipitor": "ليبيتور", "zocor": "زوكور", "crestor": "كريستور",
    "atorvastatin": "اتورفاستاتين",
    "glucophage": "جلوكوفاج", "metformin": "ميتفورمين", "amaryl": "اماريل",
    "diamicron": "دياميكرون", "januvia": "جانوفيا", "galvus": "جالفوس",
    "trajenta": "تراجينتا", "forxiga": "فوركسيجا", "jardiance": "جارديانس",
    "mixtard": "ميكستارد", "lantus": "لانتوس", "humalog": "هيومالوج",
    "novorapid": "نوفورابيد", "actrapid": "اكترابيد", "insulatard": "انسولاتارد",
    "humulin": "هيومولين", "levemir": "ليفيمير", "insulin": "انسولين",
    "ventolin": "فنتولين", "pulmicort": "بولميكورت", "symbicort": "سيمبيكورت",
    "seretide": "سيريتايد", "singulair": "سينجولير", "montel": "مونتيل",
    "telfast": "تلفاست", "zyrtec": "زيرتيك", "claritine": "كلاريتين",
    "aerius": "ايريوس", "xyzal": "زيزال", "mucosolvan": "ميوكوسولفان",
    "bisolvon": "بيسولفون", "atrovent": "اتروفنت", "spiriva": "سبيريفا",
    "bricanyl": "بريكانيل", "flixotide": "فليكسوتايد",
    "fucidin": "فيوسيدين", "bactroban": "باكتروبان", "dermovate": "ديرموفيت",
    "betnovate": "بيتنوفيت", "elocon": "الوكون", "bepanthen": "بيبانثين",
    "canesten": "كانستين", "daktarin": "داكتارين", "lamisil": "لاميسيل",
    "zovirax": "زوفيراكس",
    "centrum": "سنتروم", "seven seas": "سفن سيز", "feroglobin": "فيروجلوبين",
    "neurobion": "نيوروبيون", "osteocare": "اوستيوكير", "ferose": "فيروز",
    "folic acid": "فوليك اسيد",
    "seroxat": "زيروكسات", "prozac": "بروزاك", "zoloft": "زولوفت",
    "cipralex": "سيبرالكس", "xanax": "زاناكس", "valium": "فاليوم",
    "dogmatil": "دوجماتيل", "stilnox": "ستيلنوكس", "melatonin": "ميلاتونين",
    "viagra": "فياجرا", "cialis": "سياليس", "omnic": "اومنيك",
    "rowatinex": "رواتينكس",
    "tobrex": "توبريكس", "vigamox": "فيجاموكس",
    "primolut nor": "بريمولوت نور", "duphaston": "ديوفاستون", "clomid": "كلوميد",
    "diane": "ديان", "yasmin": "ياسمين", "gynera": "جينيرا",
    "marevan": "ماريفان", "clexane": "كليكسان", "xarelto": "زيرالتو",
    "eliquis": "اليكويس",
    "eltroxin": "التروكسين", "euthyrox": "يوثيروكس", "neomercazole": "نيوميركازول",
    "medrol": "ميدرول", "celestone": "سيليستون", "zyloric": "زايلوريك",
    "myonal": "ميونال", "sirdalud": "سيردالود", "moov": "موف",
    "fastum": "فاستم", "fenistil": "فينيستيل",
    "congestal": "كونجستال", "comtrex": "كومتركس", "strepsils": "ستربسيلز",
    "betadine": "بيتادين", "vermox": "فيرموكس", "zentel": "زينتيل",
    "nasonex": "نازونكس", "avamys": "افاميس", "flixonase": "فليكسونيز",
    "otrivin": "اوتريفين",
}
ALIASES = {c: [c, a] for c, a in _ALIAS_AR.items()}
ALIASES["nexium"].append("نكسيوم")
ALIASES["mixtard"] += ["انسولين ميكستارد", "مكستارد"]
ALIASES["lantus"].append("انسولين لانتوس")
ALIASES["hi-biotic"] += ["hi biotic", "hibiotic"]
ALIASES["folic acid"].append("حمض الفوليك")
ALIASES["betnovate"].append("بيتنوفات")

def _key(s):
    if s is None: return ""
    t = _fold(norm(s).lower())
    t = re.sub(r"\d+(?:[.,]\d+)?", " ", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return " ".join(w for w in t.split() if w not in FORM_WORDS and len(w) > 1)

ALIAS_LOOKUP = {}
for _can, _vars in ALIASES.items():
    for _v in _vars + [_can]:
        ALIAS_LOOKUP[_key(_v)] = _can

def extend_aliases(df):
    """Merge a big name dictionary (columns: en, ar) into ALIAS_LOOKUP. Each row's
    canonical is the cleaned English name; both its Arabic and English spellings map
    to it, so any side of a file can be in either language. Returns rows merged."""
    n = 0
    for _, r in df.iterrows():
        c = _key(r.get("en"))
        if not c: continue
        ka = _key(r.get("ar"))
        ALIAS_LOOKUP[c] = c
        if ka and ka not in ALIAS_LOOKUP: ALIAS_LOOKUP[ka] = c  # first wins: oral forms before powder/IV
        n += 1
    return n

def canon(s):
    """Canonical name key: folded spelling, no strengths/forms/packs, alias-resolved.
    A high-cutoff same-language fuzzy pass against the dictionary catches small
    spelling differences (جارديانس/جارديانسي) without cross-language guessing."""
    k = _key(s)
    if k in ALIAS_LOOKUP: return ALIAS_LOOKUP[k]
    m = difflib.get_close_matches(k, ALIAS_LOOKUP.keys(), n=1, cutoff=0.85)
    if m: return ALIAS_LOOKUP[m[0]]
    return k

LINK_COLS = ["اسم الصنف في العرض", "اسمه في ملف المخزون"]

def links_to_df(mapping):
    """Manual offer->stock links as a small DataFrame the user downloads and re-uploads."""
    return pd.DataFrame([{LINK_COLS[0]: k, LINK_COLS[1]: v} for k, v in (mapping or {}).items()], columns=LINK_COLS)

def df_to_links(df):
    """Parse a links file back into a mapping. Uses the named columns when present,
    otherwise the first two columns. Empty rows are skipped."""
    if df is None or df.empty: return {}
    if all(c in df.columns for c in LINK_COLS):
        a, b = LINK_COLS
    else:
        a, b = list(df.columns)[:2]
    out = {}
    for _, r in df.iterrows():
        x, y = r[a], r[b]
        if pd.isna(x) or pd.isna(y): continue
        x, y = str(x).strip(), str(y).strip()
        if x and y: out[x] = y
    return out

_STR_UNITS = r"(?:mg|mcg|ml|gm|g|iu|جم|مجم|ملجم|مل|وحده|وحدة|%)"

def strength(s):
    """Strength key for a name: unit-tagged numbers (500mg, 1جم) joined by /, else the
    first bare number (كونكور 5 -> '5'). Empty when the name carries no number."""
    if s is None: return ""
    t = _fold(norm(s).lower())
    nums = re.findall(r"(\d+(?:[.,]\d+)?)\s*" + _STR_UNITS, t)
    if nums: return "/".join(x.replace(",", ".") for x in nums)
    m = re.search(r"\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)+", t)  # combined strength: 50/250
    if m: return m.group().replace(",", ".")
    m = re.search(r"\d+(?:[.,]\d+)?", t)
    return m.group().replace(",", ".") if m else ""

def suggest_match(offer_item, stock_items):
    """Best stock-item guess for an unmatched offer item (manual mapping UI)."""
    stock_items = [str(s) for s in stock_items]
    c = canon(offer_item)
    for s in stock_items:
        if canon(s) == c: return s
    cans = [canon(s) for s in stock_items]
    k = difflib.get_close_matches(c, cans, n=1, cutoff=0.6)
    if k: return stock_items[cans.index(k[0])]
    kmap = {_key(s): s for s in stock_items}
    k = difflib.get_close_matches(_key(offer_item), list(kmap), n=1, cutoff=0.7)
    return kmap[k[0]] if k else None

import datetime as dt
def parse_exp(s):
    """returns first-of-month-end date or None. Accepts MM/YYYY, YYYY-MM(-DD), DD/MM/YYYY, Excel dates and serials."""
    if s is None or (isinstance(s, float) and pd.isna(s)): return None
    if isinstance(s, (pd.Timestamp, dt.datetime, dt.date)): return pd.Timestamp(s).date()
    if isinstance(s, (int, float)):
        if 20000 <= float(s) <= 80000: return dt.date(1899, 12, 30) + dt.timedelta(days=int(s))
        return None
    t = norm(s)
    m = re.search(r"(\d{1,2})[/\-.](\d{4})\b", t)
    if m and 1 <= int(m.group(1)) <= 12: return dt.date(int(m.group(2)), int(m.group(1)), 28)
    m = re.search(r"(\d{4})[/\-.](\d{1,2})(?:[/\-.](\d{1,2}))?", t)
    if m and 1 <= int(m.group(2)) <= 12: return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3) or 28))
    m = re.search(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})", t)
    if m and 1 <= int(m.group(2)) <= 12: return dt.date(int(m.group(3)), int(m.group(2)), min(int(m.group(1)), 28))
    return None

def guess_supplier_name(f, fallback=""):
    """Peek at the first rows of an Excel file for a company title line (شركة/مؤسسة/...)
    to pre-fill the supplier name. Falls back to the given fallback (file name)."""
    try:
        pos = f.tell()
        head = pd.read_excel(f, header=None, nrows=6)
        f.seek(pos)
    except Exception:
        try: f.seek(0)
        except Exception: pass
        return fallback
    for _, row in head.iterrows():
        for v in row:
            t = norm(v) if isinstance(v, str) else ""
            if re.search(r"(شرك|مؤسس|للأدوي|للمستلزم|pharma|medical|trading|trade)", t, re.I):
                t = re.split(r"[-–—:|]", t)[0].strip()
                if t: return t
    return fallback

def parse_excel(f, supplier):
    df, m, sheet, nsheets = read_excel_smart(f, ["item", "price"])
    if "item" not in m or "price" not in m: return []
    ci, cp = m["item"], m["price"]
    g = guess_columns(list(df.columns), ["discount", "min_qty", "expiry", "batch"])
    cd, cm, ce, cb = g.get("discount"), g.get("min_qty"), g.get("expiry"), g.get("batch")
    rows = []
    for _, r in df.iterrows():
        p = num(r[cp])
        if pd.isna(r[ci]) or p is None: continue
        rows.append(dict(item=str(r[ci]).strip(), supplier=supplier, price=p,
            discount=(num(r[cd]) or 0) if cd else 0, min_qty=(num(r[cm]) or 0) if cm else 0,
            expiry=parse_exp(r[ce]) if ce else None,
            batch=(str(r[cb]).strip() if cb and not pd.isna(r[cb]) else "")))
    return rows


def parse_pdf(f, supplier):
    import pdfplumber
    rows = []
    with pdfplumber.open(f) as pdf:
        for pg in pdf.pages:
            for t in pg.extract_tables():
                if not t: continue
                h = [str(x or "") for x in t[0]]
                def ix(*ws): return next((i for i, x in enumerate(h) if any(w in x.lower() for w in ws)), None)
                i_i, i_p, i_d, i_m = ix("صنف", "اسم", "منتج", "دواء", "item", "product"), ix("سعر", "تكلفة", "price"), ix("خصم", "discount", "disc"), ix("حد", "كمية", "min", "moq")
                i_e, i_b = ix("صلاحية", "انتهاء", "expiry"), ix("تشغيلة", "باتش", "batch")
                for r in t[1:]:
                    if i_i is None or i_p is None: continue
                    p = num(r[i_p] or "")
                    if p is None: continue
                    rows.append(dict(item=str(r[i_i]).strip(), supplier=supplier, price=p,
                        discount=(num(r[i_d] or "") or 0) if i_d is not None else 0,
                        min_qty=(num(r[i_m] or "") or 0) if i_m is not None else 0,
                        expiry=parse_exp(r[i_e]) if i_e is not None else None,
                        batch=str(r[i_b] or "").strip() if i_b is not None else ""))
    return rows

def parse_whatsapp(text, supplier):
    rows = []
    for line in text.splitlines():
        line = norm(line)
        line = re.sub(r"^\[?[\d/,: \-APM]+\]?\s*[^:]{0,30}:\s", "", line) if re.match(r"^\[?\d", line) else line
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:جنيه|ج\b|EGP)", line)
        if not m: continue
        item = line[:m.start()].strip(" -–:،")
        if not item: continue
        d = re.search(r"خصم\s*(\d+(?:[.,]\d+)?)", line)
        q = re.search(r"(?:أقل كمية|اقل كمية|الحد الأدنى|الحد الادنى)\s*(\d+)", line)
        e = re.search(r"(?:صلاحية|انتهاء|تاريخ الصلاحية)\s*:?\s*([\d/\-.]+)", line)
        b = re.search(r"(?:تشغيلة|باتش|batch)\s*:?\s*([A-Za-z0-9\-]+)", line, re.I)
        rows.append(dict(item=item, supplier=supplier, price=float(m.group(1).replace(",", ".")),
            expiry=parse_exp(e.group(1)) if e else None, batch=b.group(1) if b else "",
            discount=float(d.group(1).replace(",", ".")) if d else 0, min_qty=int(q.group(1)) if q else 0))
    return rows

def fix_stock(stock):
    g = guess_columns(list(stock.columns), ["item", "monthly_sales", "stock"])
    stock = stock.rename(columns={v: k for k, v in g.items()})
    for k in ["item", "stock", "monthly_sales"]:
        if k not in stock.columns: raise ValueError("عمود ناقص في ملف المخزون: " + k)
    for k in ["stock", "monthly_sales"]:
        stock[k] = stock[k].map(num)
    # Same item on several rows (batches, merged cells): merge into one row, summing
    # stock and sales, keeping the first written name. Different strengths of one brand
    # are different items and stay separate.
    stock = stock[["item", "stock", "monthly_sales"]].copy()
    stock["_c"] = stock["item"].map(lambda x: canon(x) + "#" + strength(x))
    stock["_s"] = stock["stock"].fillna(0)
    stock["_m"] = stock["monthly_sales"].fillna(0)
    stock = (stock.groupby("_c", sort=False)
             .agg(item=("item", "first"), stock=("_s", "sum"), monthly_sales=("_m", "sum"))
             .reset_index(drop=True))
    return stock

def compare(offers, stock, cover_days=45, min_months=6, today=None, manual=None):
    manual = manual or {}
    today = today or dt.date.today()
    stock = fix_stock(stock)
    st = {str(r["item"]).strip(): r for _, r in stock.iterrows()}
    base = {}
    strong = {}
    for nm in st:
        c, s = canon(nm), strength(nm)
        base.setdefault(c, []).append(nm)
        strong.setdefault((c, s), nm)
    def pick(c, s):
        """Best stock name for canonical c, preferring the same strength when given."""
        if s and (c, s) in strong: return strong[(c, s)]
        cands = base.get(c)
        if not cands: return None
        if len(cands) == 1: return cands[0]
        for nm in cands:
            if not strength(nm): return nm
        return cands[0]
    out, unmatched = [], []
    for o in offers:
        if o["item"] in manual and manual[o["item"]] in st:
            k = [manual[o["item"]]]
        else:
            c, s = canon(o["item"]), strength(o["item"])
            hit = pick(c, s)
            if not hit:
                kk = difflib.get_close_matches(c, list(base), n=1, cutoff=0.6)
                if kk: hit = pick(kk[0], s)
            if not hit:
                # last resort: same-language fuzzy on stripped keys (no numbers,
                # no forms) so a shared strength like "400" cannot fake a match
                kmap = {_key(x): x for x in st}
                m2 = difflib.get_close_matches(_key(o["item"]), list(kmap), n=1, cutoff=0.7)
                if m2: hit = kmap[m2[0]]
            k = [hit] if hit else []
        if not k: unmatched.append(o); continue
        o = dict(o, item=k[0]); o["net"] = round(o["price"] * (1 - o["discount"] / 100), 2)
        e = o.get("expiry")
        o["months_left"] = round((e - today).days / 30.4, 1) if e else None
        o["short_dated"] = bool(e and o["months_left"] < min_months)
        out.append(o)
    df = pd.DataFrame(out)
    if df.empty: return df, pd.DataFrame(), pd.DataFrame(unmatched)
    rows = []
    for item, g in df.groupby("item"):
        g = g.sort_values("net"); ok = g[~g.short_dated]
        best = (ok if len(ok) else g).iloc[0]; worst = g.iloc[-1]
        note = "" if len(ok) else "كل العروض قريبة الانتهاء"
        s = st[item]; need = max(0, round(s["monthly_sales"] * cover_days / 30 - s["stock"]))
        rows.append({"الصنف": item, "أرخص مورد": best.supplier, "السعر بعد الخصم": best.net,
            "أغلى سعر": worst.net, "التوفير %": round((1 - best.net / worst.net) * 100, 1) if worst.net else 0,
            "الكمية المقترحة": need, "حد أدنى عند الأرخص": best.min_qty, "التكلفة": round(need * best.net, 2),
            "الصلاحية": best.expiry if best.expiry else "", "الأشهر المتبقية": best.months_left, "التشغيلة": best.batch,
            "تنبيه": " | ".join(x for x in ["الكمية أقل من الحد الأدنى" if 0 < need < best.min_qty else "",
                note, f"{int((g.short_dated).sum())} عرض اتستبعد لقرب الانتهاء" if len(ok) and g.short_dated.any() else ""] if x)})
    return df, pd.DataFrame(rows), pd.DataFrame(unmatched)


def reorder_alert(stock, lead_days=7, safety_days=7, cover_days=45):
    """Per item: days of stock left, reorder date, urgency, suggested qty. Works from the stock file alone."""
    stock = fix_stock(stock)
    rows = []
    for _, r in stock.iterrows():
        s, m = num(r["stock"]) or 0, num(r["monthly_sales"]) or 0
        daily = m / 30
        left = round(s / daily, 1) if daily > 0 else None
        need = max(0, round(m * cover_days / 30 - s))
        if left is None: status = "لا مبيعات"
        elif left <= lead_days: status = "عاجل: اطلب النهارده"
        elif left <= lead_days + safety_days: status = "اطلب قريب"
        else: status = "كافي"
        rows.append({"الصنف": r["item"], "المخزون": s, "مبيعات الشهر": m, "أيام متبقية": left,
            "تاريخ النفاد": (dt.date.today() + dt.timedelta(days=int(left))) if left is not None else "",
            "الحالة": status, "الكمية المقترحة": need if status.startswith(("عاجل", "اطلب")) else 0})
    order = {"عاجل: اطلب النهارده": 0, "اطلب قريب": 1, "كافي": 2, "لا مبيعات": 3}
    df = pd.DataFrame(rows)
    return df.sort_values("الحالة", key=lambda s: s.map(order)).reset_index(drop=True)


def build_request_message(ra, supplier="", buyer="", reply_by="", with_expiry=True, min_months=6):
    """Ready-to-send Arabic price request (WhatsApp/email) for the items the reorder alert says to order."""
    df = ra[ra["الكمية المقترحة"] > 0]
    if df.empty: return ""
    lines = [("السلام عليكم" + (" أستاذ/ " + supplier if supplier else "")) + "،", "",
             "محتاجين عرض سعر للأصناف دي:", ""]
    for i, r in enumerate(df.itertuples(index=False), 1):
        lines.append(f"{i}. {r[0]} - الكمية: {int(r[-1])}")
    lines += ["", "لو سمحت وضّح لكل صنف: السعر، الخصم، أقل كمية، وتاريخ التوريد."]
    if with_expiry: lines.append(f"والصلاحية المتبقية لا تقل عن {min_months} شهور، مع رقم التشغيلة.")
    if reply_by: lines.append(f"محتاجين الرد قبل {reply_by}.")
    lines += ["", "شكرًا" + (" - " + buyer if buyer else "")]
    return "\n".join(lines)


def build_order_messages(cmp_df, buyer=""):
    """Final per-supplier order drafts from the comparison table. Draft only: the user
    reviews and sends himself. Items with suggested qty 0 are skipped; a line below the
    supplier's minimum is marked, never silently changed. Returns list of dicts."""
    df = cmp_df[cmp_df["الكمية المقترحة"] > 0]
    out = []
    for sup, g in df.groupby("أرخص مورد", sort=False):
        lines = ["السلام عليكم" + (" أستاذ/ " + str(sup) if sup else "") + "،", "",
                 "نرجو تجهيز الطلب ده:"]
        total = 0
        for r in g.itertuples(index=False):
            item, qty, price, minq = r[0], int(r[5]), float(r[2]), r[6]
            lt = round(qty * price, 2)
            total += lt
            note = "  (أقل من حد الأدنى للمورد: " + str(int(minq)) + ")" if minq and qty < minq else ""
            lines.append(f"- {item}: {qty} × {price:,.2f} = {lt:,.2f} جنيه{note}")
        lines += ["", f"إجمالي الطلب: {total:,.2f} جنيه", "نرجو تأكيد الطلب وموعد التسليم.",
                  "شكرًا" + (" - " + buyer if buyer else "")]
        out.append({"supplier": sup, "message": "\n".join(lines), "total": round(total, 2), "items": len(g)})
    return out


def parse_invoice(f):
    """Invoice/receipt Excel: item + unit price required, qty optional."""
    df, m, sheet, nsheets = read_excel_smart(f, ["item", "price"])
    if "item" not in m or "price" not in m: return []
    g = guess_columns(list(df.columns), ["qty"])
    cq = g.get("qty")
    rows = []
    for _, r in df.iterrows():
        p = num(r[m["price"]])
        if pd.isna(r[m["item"]]) or p is None: continue
        rows.append(dict(item=str(r[m["item"]]).strip(), price=p,
                         qty=(num(r[cq]) if cq else None)))
    return rows

def check_invoice(offers, invoice):
    """Compare invoice lines to the agreed offer. Only exact dictionary matches get a
    price verdict. Fuzzy matches, strength conflicts, multi-strength offers and
    multi-price lines are flagged for manual review (fail closed): they are never
    counted in the over-billing total and never drafted."""
    base = {}
    for o in offers:
        base.setdefault(canon(o["item"]), []).append(o)
    rows = []

    def out(line, status, o=None, net=None, pct=None, val=None, note=""):
        rows.append({"الصنف في الفاتورة": line["item"], "الصنف في العرض": (o or {}).get("item", ""),
            "المورد": (o or {}).get("supplier", ""), "سعر العرض بعد الخصم": net,
            "سعر الفاتورة": line["price"], "الفرق %": pct, "الكمية": line.get("qty"),
            "قيمة الفرق": val, "الحالة": status, "ملاحظة": note})

    for line in invoice:
        c, s = canon(line["item"]), strength(line["item"])
        cands = base.get(c)
        if not cands:
            kk = difflib.get_close_matches(c, list(base), n=1, cutoff=0.6)
            if kk:
                o0 = min(base[kk[0]], key=lambda o: o["price"] * (1 - o.get("discount", 0) / 100))
                out(line, "تحقق: المطابقة مش مؤكدة", o0, note="اتطابق تقريبي مع: " + o0["item"])
            else:
                out(line, "صنف مش في العرض")
            continue
        if s:
            same = [o for o in cands if strength(o["item"]) == s]
            nostr = [o for o in cands if not strength(o["item"])]
            if same:
                cands = same
            elif nostr:
                cands = nostr
            else:
                strengths = sorted({strength(o["item"]) for o in cands})
                out(line, "تحقق: التركيز مختلف", cands[0], note="تركيز العرض: " + "، ".join(strengths))
                continue
        else:
            nostr = [o for o in cands if not strength(o["item"])]
            strengths = sorted({strength(o["item"]) for o in cands if strength(o["item"])})
            if nostr:
                cands = nostr
            elif len(strengths) > 1:
                out(line, "تحقق: التركيز مش محدد في الفاتورة", cands[0],
                    note="تركيزات العرض: " + "، ".join(strengths))
                continue
        nets = sorted({round(o["price"] * (1 - o.get("discount", 0) / 100), 2) for o in cands})
        if len(nets) > 1:
            out(line, "غامض: أكتر من سعر في العروض", cands[0],
                note="الأسعار: " + "، ".join(f"{x:,.2f}" for x in nets))
            continue
        net = nets[0]
        o = next(o for o in cands if round(o["price"] * (1 - o.get("discount", 0) / 100), 2) == net)
        diff = round(line["price"] - net, 2)
        pct = round((line["price"] / net - 1) * 100, 1) if net else 0
        q = line.get("qty")
        if abs(pct) <= 0.5:
            status = "مطابق"
        elif pct > 0:
            status = f"أعلى من العرض بـ {pct}%"
        else:
            status = f"أقل من العرض بـ {abs(pct)}%"
        out(line, status, o, net, pct, round(diff * q, 2) if q else diff)
    return pd.DataFrame(rows)

def draft_invoice_dispute(chk, supplier="", buyer=""):
    """Draft-only message to the supplier listing over-billed lines and items missing
    from the offer. Empty string when the invoice is clean."""
    over = chk[chk["الحالة"].str.startswith("أعلى")]
    missing = chk[chk["الحالة"] == "صنف مش في العرض"]
    if over.empty and missing.empty: return ""
    lines = ["السلام عليكم" + (" أستاذ/ " + supplier if supplier else "") + "،", "",
             "راجعنا الفاتورة على عرض السعر المتفق عليه ولقينا الفروق دي:", ""]
    for _, r in over.iterrows():
        lines.append(f"- {r['الصنف في الفاتورة']}: اتسعّر {r['سعر الفاتورة']} والمتفق عليه {r['سعر العرض بعد الخصم']} (فرق {r['الفرق %']}%)")
    if not missing.empty:
        lines += ["", "أصناف في الفاتورة مش موجودة في العرض أصلًا:"]
        for _, r in missing.iterrows():
            lines.append(f"- {r['الصنف في الفاتورة']} بسعر {r['سعر الفاتورة']}")
    lines += ["", "نرجو التصحيح أو توضيح سبب الفرق.", "شكرًا" + (" - " + buyer if buyer else "")]
    return "\n".join(lines)


STYLES = ["ودي", "حازم", "التزام", "سريع"]

def draft_counter(reply_text, competing_net=None, days_left=None, lead_days=7, supplier="", target_discount=None, style="ودي", confirm_price=None, confirm_discount=None):
    """Rule-based Arabic counter-reply draft. Returns (draft, reasons). Never sent by the app."""
    rows = parse_whatsapp(reply_text, supplier) if reply_text else []
    r = rows[0] if rows else None
    reasons = []
    if r is None:
        import re as _re
        m = _re.search(r"(\d+(?:[.,]\d+)?)\s*(?:جنيه|ج\b|EGP|le\b)", reply_text or "", _re.I)
        p = float(m.group(1).replace(",", ".")) if m else None
        if p is None: return "", ["ما قدرتش أقرا سعر من رد المورد. اكتب الرقم مع كلمة جنيه."]
        r = dict(item="", price=p, discount=0, min_qty=0, expiry=None, batch="")
    if not r["price"] or r["price"] <= 0 or not (0 <= (r.get("discount") or 0) < 100):
        return "", ["السعر أو الخصم في الرد مش منطقي. راجع النص."]
    net = r["price"] * (1 - r["discount"] / 100)
    reasons.append(f"سعر المورد بعد الخصم: {net:.2f}")
    urgent = days_left is not None and days_left <= lead_days
    if days_left is not None:
        reasons.append(f"المخزون يكفي {days_left} يوم، ومدة التوريد {lead_days} يوم: " + ("عاجل، مفيش وقت للشد." if urgent else "عندك وقت للتفاوض."))
    gap = None
    if competing_net:
        gap = (net - competing_net) / net * 100
        reasons.append(f"أقل عرض تاني: {competing_net:.2f} (" + (f"أرخص منك بـ {gap:.1f}%" if gap > 0 else f"أغلى منك بـ {-gap:.1f}%") + ")")
    cheaper = gap is not None and gap > 1
    if style == "تلقائي":
        if urgent:
            style = "سريع"
            reasons.append("اقترحنا أسلوب سريع: المخزون أوشك يخلص ومفيش وقت للشد.")
        elif cheaper:
            style = "حازم"
            reasons.append(f"اقترحنا أسلوب حازم: في عرض تاني أرخص بـ {gap:.1f}% وده موقف قوي ليك.")
        elif days_left is not None and days_left >= lead_days + 14:
            style = "التزام"
            reasons.append("اقترحنا أسلوب التزام: المخزون مريح، نقدر نتفاوض على تكرار الطلبات بأفضل سعر.")
        else:
            style = "ودي"
            reasons.append("اقترحنا أسلوب ودي: الموقف متوازن والأفضل نحافظ على العلاقة.")
        reasons.append("تقدر تغيّر الأسلوب من القايمة لو حابب.")
    if style not in STYLES: style = "ودي"
    reasons.append(f"الأسلوب: {style}")
    tgt = None
    if cheaper:
        tgt = target_discount if target_discount else round(min(gap, 10), 1)
    asks = "مدة السداد، ميعاد التوريد، وتاريخ الصلاحية ورقم التشغيلة"
    mq = r.get("min_qty")
    lines = []
    if style == "ودي":
        lines.append("أهلا بحضرتك، شكرًا على العرض وعلى وقتك.")
        if cheaper and urgent:
            lines.append("محتاجين نقفل بسرعة. لو تقدر تقرّب السعر شوية نأكد الطلب النهارده.")
        elif cheaper:
            lines.append(f"في عندنا عرض أقل. لو تقدر تنزل الخصم لحوالي {tgt}% زيادة يبقى ممتاز ونقفل الكمية معاك.")
        elif gap is not None:
            lines.append("السعر مناسب، نتمنى نضبط معاك الشروط بس.")
        else:
            lines.append("هل في خصم ممكن تعمله لنا على الكمية دي؟")
        lines.append(f"ونحتاج نعرف: {asks}.")
        if mq and not urgent: lines.append(f"وأقل كمية عندكم {int(mq)}، ممكن تتخفض شوية؟")
        lines.append("شاكرين ليك.")
    elif style == "حازم":
        lines.append("شكرًا على العرض.")
        if cheaper:
            lines.append(f"السعر ده أعلى من عرض تاني عندنا. محتاجين خصم إضافي حوالي {tgt}% عشان نكمل.")
        elif gap is not None:
            lines.append("السعر مقبول. هنركز على الشروط.")
        else:
            lines.append("محتاجين أفضل سعر عندكم للكمية دي، وخصم أعلى من ده.")
        lines.append(f"أكد لنا: {asks}.")
        if mq and not urgent: lines.append(f"محتاجين تخفضوا أقل كمية ({int(mq)}).")
        lines.append("في انتظار ردك النهارده.")
    elif style == "التزام":
        lines.append("شكرًا على العرض. مهتمين نشتغل معاكم بشكل منتظم.")
        lines.append("لو الطلبات اتكررت أو زودنا الكمية، إيه أفضل سعر وخصم تقدروا تقدموه؟")
        if cheaper:
            lines.append(f"محتاجين نقرّب السعر لحوالي {tgt}% أقل من ده.")
        lines.append(f"ونحتاج نعرف: {asks}.")
        if mq and not urgent: lines.append(f"وممكن نناقش أقل كمية ({int(mq)}) مع جدول توريد متكرر؟")
        lines.append("شكرًا.")
    else:  # سريع
        lines.append("شكرًا على العرض.")
        if cheaper:
            lines.append(f"لو وصلنا لخصم زيادة حوالي {tgt}% نقدر نقرر النهارده.")
        else:
            lines.append("لو وصلنا لأفضل سعر عندكم نقدر نقرر النهارده.")
        lines.append(f"ابعتلنا بسرعة: {asks}.")
        lines.append("شكرًا.")
    if confirm_price or confirm_discount:
        parts = []
        if confirm_price: parts.append(f"السعر {confirm_price:g} جنيه")
        if confirm_discount: parts.append(f"الخصم {confirm_discount:g}%")
        cl = "نأكد الاتفاق: " + " و".join(parts) + ". لو ده متفق عليه، من فضلك أكّد لنا كتابيًا قبل ما نجهّز أي طلب."
        reasons.append("أضفت طلب تأكيد بالسعر/الخصم اللي كتبتهم. ده مش التزام بالطلب.")
    else:
        cl = "قبل أي طلب، محتاجين تأكيد كتابي بالسعر والخصم النهائيين."
        reasons.append("أضفت طلب تأكيد السعر والخصم النهائيين قبل الطلب. ده مش التزام بالطلب.")
    lines.insert(len(lines) - 1, cl)
    reasons.append("المسودة بتتكلم بس عن اللي دخلته: العرض التاني مذكور من غير اسم، ومفيش وعد بكمية معينة. راجع قبل ما تبعت.")
    return "\n".join(l for l in lines if l), reasons


def fix_expiry_stock(stock):
    g = guess_columns(list(stock.columns), ["item", "expiry", "cost", "stock"])
    stock = stock.rename(columns={v: k for k, v in g.items()})
    for k in ["item", "stock", "expiry", "cost"]:
        if k not in stock.columns: raise ValueError("عمود ناقص في ملف الصلاحيات: " + k + " (مطلوب: صنف، كمية، تكلفة، صلاحية)")
    for k in ["stock", "cost"]:
        stock[k] = stock[k].map(num)
    return stock


def expiry_risk(stock, months=3, today=None):
    """Value at risk from expiry: items (rows/batches) expiring within `months`, value = qty * unit cost. Sorted."""
    today = today or dt.date.today()
    stock = fix_expiry_stock(stock)
    rows = []
    for _, r in stock.iterrows():
        item = str(r["item"]).strip()
        if not item or item == "nan": continue
        qty, cost = num(r["stock"]) or 0, num(r["cost"]) or 0
        e = parse_exp(r["expiry"])
        ml = round((e - today).days / 30.4, 1) if e else None
        val = round(qty * cost, 2)
        if ml is None:
            status = "بدون تاريخ صلاحية"
        elif ml < 0:
            status = "منتهي"
        elif ml <= 1:
            status = "عاجل: أقل من شهر"
        elif ml <= months:
            status = "قريب الانتهاء"
        else:
            continue
        rows.append({"الصنف": item, "الكمية": qty, "تكلفة الوحدة": cost,
            "الصلاحية": str(e) if e else "", "الأشهر المتبقية": ml,
            "القيمة المعرضة للخسارة": val if ml is not None else 0,
            "الحالة": status})
    df = pd.DataFrame(rows)
    if df.empty: return df
    rank = {"منتهي": 0, "عاجل: أقل من شهر": 1, "قريب الانتهاء": 2, "بدون تاريخ صلاحية": 3}
    return df.sort_values(["الحالة", "الأشهر المتبقية", "القيمة المعرضة للخسارة"],
        key=lambda s: s.map(rank) if s.name == "الحالة" else s,
        ascending=[True, True, False]).reset_index(drop=True)


def sample_expiry_stock():
    """Invented demo rows so the report can be tried without uploading anything."""
    t = dt.date.today()
    def plus(m): return (t + dt.timedelta(days=int(m * 30.4))).replace(day=1)
    return pd.DataFrame([
        {"item": "أوجمنتين 1جم 14قرص", "stock": 120, "cost": 185.0, "expiry": plus(-1)},
        {"item": "بنادول إكسترا 24قرص", "stock": 300, "cost": 42.5, "expiry": plus(1)},
        {"item": "فلاجيل 500مجم 20قرص", "stock": 200, "cost": 31.0, "expiry": plus(2)},
        {"item": "كونجستال 20قرص", "stock": 450, "cost": 27.0, "expiry": plus(3)},
        {"item": "زيروكسات 20مجم 30قرص", "stock": 60, "cost": 150.0, "expiry": plus(3)},
        {"item": "نيكسيوم 40مجم 14قرص", "stock": 90, "cost": 210.0, "expiry": plus(8)},
        {"item": "امبرال", "stock": 50, "cost": 18.0, "expiry": ""},
    ])


SAMPLE_CHAT = """12/8/2026, 10:15 ص - الحاج محمود: سرنجة 5مل - 110 جنيه خصم 3% أقل كمية 100
05/9/2026, 1:20 م - الحاج محمود: سرنجة 5مل - 112 جنيه خصم 5%
20/10/2026, 11:05 ص - الحاج محمود: بنادول إكسترا 24قرص - 44 جنيه خصم 2%
الصبح بكره التوريد لو حابب
15/11/2026, 9:40 م - الحاج محمود: سرنجة 5مل - 115 جنيه خصم 4%
15/11/2026, 9:41 م - الحاج محمود: بنادول إكسترا 24قرص - 43.5 جنيه خصم 3%
"""


def parse_whatsapp_dated(text, supplier):
    """parse_whatsapp plus the WhatsApp message date when the line starts with a timestamp."""
    rows = []
    for line in text.splitlines():
        d = None
        m = re.search(r"\[?\s*(\d{1,2})/(\d{1,2})/(\d{2,4})[,،]?\s+\d{1,2}:\d{2}", line[:40])
        if m:
            day, mo, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if yr < 100: yr += 2000
            if 1 <= mo <= 12 and 1 <= day <= 31: d = dt.date(yr, mo, day)
        for r in parse_whatsapp(line, supplier):
            r["date"] = d
            rows.append(r)
    return rows


def supplier_memory(rows):
    """Per supplier + item: offer count, last price/discount/date, best net price seen, and a note."""
    df = pd.DataFrame(rows)
    if df.empty: return df
    df["net"] = (df.price * (1 - df.discount / 100)).round(2)
    df["date"] = pd.to_datetime(df["date"])
    out = []
    for (sup, item), g in df.groupby(["supplier", "item"]):
        g2 = g.sort_values("date", na_position="first", kind="stable")
        last, best = g2.iloc[-1], g.loc[g.net.idxmin()]
        note = ""
        if best.net < last.net:
            note = f"آخر عرض أعلى من أفضل سعر شفناه بـ {(last.net / best.net - 1) * 100:.1f}%"
        elif last.net == best.net and len(g) > 1:
            note = "آخر عرض هو أفضل سعر شفناه"
        out.append({"المورد": sup, "الصنف": item, "عدد العروض": len(g),
            "آخر سعر": last.price, "آخر خصم %": last.discount, "آخر صافي": last.net,
            "آخر تاريخ": str(last["date"].date()) if pd.notna(last["date"]) else "",
            "أفضل صافي شفناه": best.net,
            "تاريخه": str(best["date"].date()) if pd.notna(best["date"]) else "",
            "ملاحظة": note})
    return pd.DataFrame(out).sort_values(["المورد", "الصنف"]).reset_index(drop=True)


HIST_COLS = ["التاريخ", "المورد", "الصنف", "السعر", "الخصم %", "الصافي"]


def rows_to_history(rows):
    out = []
    for r in rows:
        out.append({"التاريخ": str(r["date"]) if r.get("date") else "",
            "المورد": r["supplier"], "الصنف": r["item"],
            "السعر": r["price"], "الخصم %": r["discount"],
            "الصافي": round(r["price"] * (1 - r["discount"] / 100), 2)})
    return pd.DataFrame(out, columns=HIST_COLS)


def update_price_history(hist, rows):
    """Merge newly parsed offers into the history table; dedupe identical rows; sort by item then date."""
    new = rows_to_history(rows)
    if hist is not None and not hist.empty:
        missing = [c for c in HIST_COLS if c not in hist.columns]
        if missing:
            raise ValueError("عمود ناقص في ملف السجل: " + missing[0] + " (ارفع نفس ملف price_history.xlsx اللي حمّلته من التطبيق)")
        merged = pd.concat([hist[HIST_COLS].astype({"التاريخ": str}), new], ignore_index=True)
    else:
        merged = new
    merged["التاريخ"] = merged["التاريخ"].fillna("").astype(str).replace("nan", "")
    merged = merged.drop_duplicates(subset=HIST_COLS).reset_index(drop=True)
    merged["_d"] = pd.to_datetime(merged["التاريخ"], errors="coerce")
    return merged.sort_values(["الصنف", "_d"], na_position="last").drop(columns="_d").reset_index(drop=True)


def price_history_summary(hist):
    """Per supplier + item: last net, change vs previous offer, min/max seen."""
    h = hist.copy()
    h["_d"] = pd.to_datetime(h["التاريخ"], errors="coerce")
    out = []
    for (sup, item), g in h.groupby(["المورد", "الصنف"]):
        g = g.sort_values("_d", na_position="first", kind="stable")
        last = g.iloc[-1]
        prev = g.iloc[-2] if len(g) > 1 else None
        change = None
        if prev is not None and prev["الصافي"]:
            change = round((last["الصافي"] / prev["الصافي"] - 1) * 100, 1)
        trend = "" if change is None else ("↑ زاد" if change > 0 else ("↓ قل" if change < 0 else "ثابت"))
        out.append({"المورد": sup, "الصنف": item, "عدد العروض": len(g),
            "آخر صافي": last["الصافي"], "آخر تاريخ": last["التاريخ"],
            "التغير عن السابق %": change, "الاتجاه": trend,
            "أقل صافي": round(g["الصافي"].min(), 2), "أعلى صافي": round(g["الصافي"].max(), 2)})
    return pd.DataFrame(out).sort_values(["المورد", "الصنف"]).reset_index(drop=True)


COL_SYNS = {
    "item": ["صنف", "اسم", "منتج", "دواء", "وصف", "item", "name", "product", "description", "drug", "medicine"],
    "stock": ["مخزون", "رصيد", "كمية", "متاح", "stock", "qty", "quantity", "balance", "on hand", "amount", "units"],
    "monthly_sales": ["مبيعات", "شهري", "معدل", "monthly", "sales", "average", "avg"],
    "expiry": ["صلاحية", "انتهاء", "expiry", "expiration", "exp"],
    "cost": ["تكلفة", "سعر الشراء", "شراء", "cost", "سعر", "price"],
    "price": ["سعر", "تكلفة", "price", "cost"],
    "discount": ["خصم", "discount", "disc"],
    "min_qty": ["حد", "أقل كمية", "اقل كمية", "min", "moq"],
    "batch": ["تشغيلة", "باتش", "batch", "lot"],
    "qty": ["كمية", "العدد", "عدد", "qty", "quantity", "units"],
}


def guess_columns(columns, fields):
    """Map canonical field names to actual column labels via normalized substring synonyms.
    Synonyms are tried most-specific first; each column is used at most once."""
    mapping, used = {}, set()
    for f in fields:
        for w in COL_SYNS.get(f, [f]):
            hit = next((c for c in columns if c not in used and w in norm(str(c)).lower()), None)
            if hit is not None:
                mapping[f] = hit
                used.add(hit)
                break
    return mapping


OFFERS_AR = {"item": "الصنف", "supplier": "المورد", "price": "السعر", "discount": "الخصم %",
    "min_qty": "أقل كمية", "net": "الصافي", "expiry": "الصلاحية",
    "months_left": "الأشهر المتبقية", "batch": "التشغيلة"}


def offers_display(allo):
    """Arabic-titled offers table for display and Excel export."""
    df = allo.rename(columns=OFFERS_AR)
    df = df[[c for c in OFFERS_AR.values() if c in df.columns]]
    if "الصلاحية" in df.columns:
        df["الصلاحية"] = df["الصلاحية"].astype(str).replace("None", "")
    return df


def read_excel_smart(f, fields):
    """Read a messy real-world Excel: tries every sheet, sniffs the header row even with
    title rows above, drops blank and totals rows, forward-fills merged item cells.
    Returns (df, mapping, sheet_name, n_sheets): raw-labeled df + field->label guesses."""
    xls = pd.ExcelFile(f)
    best = None
    for sheet in xls.sheet_names:
        raw = pd.read_excel(xls, sheet_name=sheet, header=None).dropna(how="all")
        if raw.empty: continue
        hdr_i, hdr_map = None, {}
        for i in range(min(20, len(raw))):
            labels = [norm(str(x)) for x in raw.iloc[i].tolist()]
            m = guess_columns(labels, fields)
            if len(m) > len(hdr_map): hdr_i, hdr_map = i, m
            if len(m) == len(fields): break
        if hdr_i is None or not hdr_map: continue
        df = raw.iloc[hdr_i + 1:].copy()
        df.columns = [norm(str(x)) for x in raw.iloc[hdr_i].tolist()]
        df = df.dropna(how="all")
        icol = hdr_map.get("item", df.columns[0])
        df = df[~df[icol].astype(str).str.contains("إجمالي|اجمالي|مجموع|total", case=False, na=False)]
        df[icol] = df[icol].ffill()
        df = df.reset_index(drop=True)
        if df.empty: continue
        if best is None or len(hdr_map) > len(best[1]):
            best = (df, hdr_map, sheet)
        if len(hdr_map) == len(fields): break
    if best is None:
        raise ValueError("ما قدرتش ألاقي صف عناوين فيه الأعمدة المطلوبة في أي sheet من الملف. "
            "اتأكد إن الملف فيه صف عناوين واضح (صنف، كمية، ...) أو جرّب ملف تاني.")
    return best[0], best[1], best[2], len(xls.sheet_names)
