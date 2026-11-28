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
FORM_WORDS = set(_fold(w) for w in _FORM.split()) | {"سعر", "س", "ج"}

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
    # bare-number fallback: a number straight before a pack word is a pack count
    # (24 قرص, 6 امبول), not a strength - skip it so it never poisons the match key
    for m in re.finditer(r"\d+(?:[.,]\d+)?", t):
        after = t[m.end():].lstrip()
        before = t[:m.start()].rstrip()
        # sheet artifacts: (72) is a row code, and a number after سعر is a price
        if before.endswith("(") and after.startswith(")"):
            continue
        if before.endswith("سعر") or before.endswith("س."):
            continue
        if re.match(r"^(?:قرص|اقراص|أقراص|كبسول|كبسولة|كبسولات|اقماع|أقماع|قمع|برطمان|عبوة|علبة|شريط|كيس|اكياس|أكياس|زجاجة|فيال|لبوس|تحاميل)\b", after):
            continue
        return m.group().replace(",", ".")
    return ""

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
    g = guess_columns(list(df.columns), ["discount", "min_qty", "expiry", "batch", "bonus"])
    cd, cm, ce, cb = g.get("discount"), g.get("min_qty"), g.get("expiry"), g.get("batch")
    if cd is None:
        # Some supplier sheets label the discount column oddly (القائمة / شركات / المرجح /
        # جملة / مندوب). Fail-safe fallback: an unmapped column whose values are all a
        # plausible discount percent (0 < v <= 70) is treated as the discount column.
        _skip = ("كود", "رقم", "code", "id", "سعر", "price", "صنف", "name", "كمية", "qty", "barcode", "باركود")
        _used = {ci, cp, cm, ce, cb}
        for c in df.columns:
            if c in _used or any(x in norm(str(c)).lower() for x in _skip): continue
            vals = pd.to_numeric(df[c], errors="coerce").dropna()
            if len(vals) >= 10 and (vals > 0).mean() >= 0.8 and (vals <= 95).all() and vals.quantile(0.95) <= 70:
                cd = c
                break
    rows = []
    for _, r in df.iterrows():
        p = num(r[cp])
        if pd.isna(r[ci]) or p is None: continue
        rows.append(dict(item=str(r[ci]).strip(), supplier=supplier, price=p,
            discount=(num(r[cd]) or 0) if cd else 0, min_qty=(num(r[cm]) or 0) if cm else 0,
            expiry=parse_exp(r[ce]) if ce else None,
            batch=(str(r[cb]).strip() if cb and not pd.isna(r[cb]) else ""),
            bonus=(str(r[g["bonus"]]).strip() if g.get("bonus") and not pd.isna(r[g["bonus"]]) else "")))
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

_WA_TS_RE = re.compile(
    r"^\[?\s*"
    r"(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})"
    r"\s*[,،]?\s+"
    r"\d{1,2}:\d{2}(?::\d{2})?"
    r"(?:\s*(?:[APap][Mm]|صباحًا|صباحاً|مساءً|[صم]))?"
    r"\s*\]?\s*(?:[-–]\s*)?")
_SENDER_RE = re.compile(r"^([^:]{1,40}):\s+")


def _wa_date(m):
    day, mo, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if yr < 100: yr += 2000
    if 1 <= mo <= 12 and 1 <= day <= 31:
        return dt.date(yr, mo, day)
    return None


def split_whatsapp_messages(text):
    """Split a WhatsApp export (Android or iPhone) into (date, sender, body) messages.
    Covers both layouts ([d/m/y, h:mm:ss AM] vs d/m/y, h:mm -), 12/24h clocks, Arabic
    AM/PM markers (ص/م/صباحًا/مساءً) and Arabic-Indic digits. Lines without a timestamp
    join the message above them; when the text has no timestamps at all (a plain pasted
    price list) every line is its own message."""
    msgs = []
    seen_ts = False
    for raw in str(text).splitlines():
        line = norm(raw)
        if not line:
            continue
        m = _WA_TS_RE.match(line)
        if m:
            seen_ts = True
            rest = line[m.end():]
            sender = ""
            sm = _SENDER_RE.match(rest)
            if sm:
                sender, rest = sm.group(1).strip(), rest[sm.end():]
            msgs.append([_wa_date(m), sender, [rest] if rest else []])
        elif seen_ts and msgs:
            msgs[-1][2].append(line)
        else:
            msgs.append([None, "", [line]])
    return [(d, s, "\n".join(ls)) for d, s, ls in msgs if any(x.strip() for x in ls)]


def _price_row_from_line(line, supplier):
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:جنيه|ج\b|EGP)", line)
    if not m: return None
    item = line[:m.start()].strip(" -–:،")
    if not item: return None
    d = re.search(r"خصم\s*(\d+(?:[.,]\d+)?)", line)
    q = re.search(r"(?:أقل كمية|اقل كمية|الحد الأدنى|الحد الادنى)\s*(\d+)", line)
    e = re.search(r"(?:صلاحية|انتهاء|تاريخ الصلاحية)\s*:?\s*([\d/\-.]+)", line)
    b = re.search(r"(?:تشغيلة|باتش|batch)\s*:?\s*([A-Za-z0-9\-]+)", line, re.I)
    return dict(item=item, supplier=supplier, price=float(m.group(1).replace(",", ".")),
        expiry=parse_exp(e.group(1)) if e else None, batch=b.group(1) if b else "",
        discount=float(d.group(1).replace(",", ".")) if d else 0, min_qty=int(q.group(1)) if q else 0)


def parse_whatsapp(text, supplier):
    rows = []
    for _d, _s, body in split_whatsapp_messages(text):
        for line in body.splitlines():
            r = _price_row_from_line(norm(line), supplier)
            if r: rows.append(r)
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
        o = dict(o, item=k[0], orig_item=o["item"]); o["net"] = round(o["price"] * (1 - o["discount"] / 100), 2)
        _bn = parse_bonus(o.get("bonus"))
        if _bn != (0, 0, 0):
            o["net"] = round(o["net"] * _bonus_factor(_bn), 2)
            o["bonus_applied"] = str(o.get("bonus") or "")
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
            "البونص": getattr(best, "bonus_applied", "") or (best.get("bonus") if hasattr(best, "get") else ""), "الكمية المقترحة": need, "حد أدنى عند الأرخص": best.min_qty, "التكلفة": round(need * best.net, 2),
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
        for _, r in g.iterrows():
            item, qty, price = r["الصنف"], int(r["الكمية المقترحة"]), float(r["السعر بعد الخصم"])
            minq = r.get("حد أدنى عند الأرخص")
            lt = round(qty * price, 2)
            total += lt
            note = "  (أقل من حد الأدنى للمورد: " + str(int(minq)) + ")" if minq and qty < minq else ""
            lines.append(f"- {item}: {qty} × {price:,.2f} = {lt:,.2f} جنيه{note}")
        lines += ["", f"إجمالي الطلب: {total:,.2f} جنيه", "نرجو تأكيد الطلب وموعد التسليم.",
                  "شكرًا" + (" - " + buyer if buyer else "")]
        out.append({"supplier": sup, "message": "\n".join(lines), "total": round(total, 2), "items": len(g)})
    return out





_AR_DIG = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
def parse_bonus(text):
    """Parse a bonus cell in either Egyptian form: units «10+2» (10 paid + 2 free) or
    percent «5%» (extra discount). Returns (bonus_get, bonus_free, bonus_pct).
    Unknown text -> (0, 0, 0) so the net price is never silently changed."""
    if text is None: return (0, 0, 0)
    s = str(text).translate(_AR_DIG).strip()
    if not s or s.lower() in ("none", "nan", "-"): return (0, 0, 0)
    m = re.search(r"(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)", s)
    if m: return (float(m.group(1)), float(m.group(2)), 0.0)
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", s)
    if m: return (0, 0, float(m.group(1)))
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if m: return (0, 0, float(m.group(1)))
    return (0, 0, 0)

def _bonus_factor(bonus):
    bg, bf, bp = bonus
    f = bg / (bg + bf) if bg > 0 else 1.0
    return f * (1 - bp / 100)

def net_unit_cost(price, bonus_get=0, bonus_free=0, base_pct=0, cash_pct=0,
                  tax_egp=0, tax_pct=0, margin_egp=0, bonus_pct=0):
    """True net unit cost from the producer/distributor pricing structure:
    list price -> base discount (أساسي) -> cash discount (خصم نقدي) -> + item tax
    (fixed EGP and/or % of the discounted price) -> - per-unit margin/support
    (هامش ربح) -> bonus «10+2» spreads the paid cost over the received units.
    Every step is returned so the user can verify the arithmetic himself."""
    p = float(price or 0)
    after_base = p * (1 - float(base_pct or 0) / 100)
    after_cash = after_base * (1 - float(cash_pct or 0) / 100)
    tax = float(tax_egp or 0) + after_cash * float(tax_pct or 0) / 100
    after_tax = after_cash + tax
    after_margin = after_tax - float(margin_egp or 0)
    bg, bf = float(bonus_get or 0), float(bonus_free or 0)
    factor = bg / (bg + bf) if bg > 0 and bf >= 0 else 1.0
    factor = factor * (1 - float(bonus_pct or 0) / 100)
    final = after_margin * factor
    return {"السعر": round(p, 2), "بعد الأساسي": round(after_base, 2),
        "بعد الخصم النقدي": round(after_cash, 2), "الضريبة": round(tax, 2),
        "بعد الضريبة": round(after_tax, 2), "بعد هامش الربح": round(after_margin, 2),
        "معامل البونص": round(factor, 4), "صافي الوحدة": round(final, 2),
        "الخصم الفعلي الكلي %": round((1 - final / p) * 100, 1) if p else 0}

# ---------------- per-item producer discounts (خصومات الأصناف) ----------------

DISCOUNT_COLS = ["الصنف", "الشركة", "أساسي %", "هامش جنيه", "ملاحظة"]

def fix_discounts(df):
    """Normalize a خصومات الأصناف sheet: fixed columns, numeric base/margin, no empty
    rows. Never raises; unknown extra columns are dropped."""
    if df is None or df.empty:
        return pd.DataFrame(columns=DISCOUNT_COLS)
    d = df.copy()
    d.columns = [str(c).strip() for c in d.columns]
    for c in DISCOUNT_COLS:
        if c not in d.columns: d[c] = ""
    d = d[DISCOUNT_COLS]
    for c in ("الصنف", "الشركة", "ملاحظة"):
        d[c] = d[c].fillna("").astype(str).str.strip()
    for c in ("أساسي %", "هامش جنيه"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d[d["الصنف"] != ""].reset_index(drop=True)

def find_item_discount(item, discounts):
    """Per-item base discount + margin lookup in the خصومات الأصناف sheet. Matches by
    canonical name + strength: a strength-carrying row only fills the same strength,
    a strength-free row only fills a lone same-name item, never guesses between
    strengths or duplicates (fail-closed). Returns the row as dict or None."""
    if discounts is None or len(discounts) == 0 or not str(item or "").strip():
        return None
    c, st_ = canon(item), strength(item)
    if not c: return None
    exact, lone = [], []
    for _, r in discounts.iterrows():
        if canon(r["الصنف"]) != c: continue
        rs = strength(r["الصنف"])
        if st_ and rs == st_: exact.append(r)
        elif not rs: lone.append(r)
    if len(exact) == 1: return exact[0].to_dict()
    if not exact and len(lone) == 1: return lone[0].to_dict()
    return None

# Regulated distributor+pharmacist discount ceilings (EDA decision 480/2026), used as
# a sanity check on user-entered numbers only, never as pricing data.
def discount_ceiling(imported=False, pack_price=None):
    """Max regulated combined discount (distributor + pharmacist) % of retail price:
    local <500 EGP/pack 35.5%, >=500: 31%; imported 30% / 25.8%. Unknown origin or
    pack price uses the most lenient ceiling to avoid false alarms."""
    try: pp = float(pack_price or 0)
    except (TypeError, ValueError): pp = 0
    if imported: return 25.8 if pp >= 500 else 30.0
    return 31.0 if pp >= 500 else 35.5

def discount_ceiling_warning(base_pct, cash_pct, imported=False, pack_price=None):
    """Warns when أساسي + نقدي exceeds the regulated ceiling: likely a typo to review."""
    total = float(base_pct or 0) + float(cash_pct or 0)
    ceil_ = discount_ceiling(imported, pack_price)
    if total > ceil_ + 0.001:
        return (f"مجموع الأساسي + النقدي ({total:g}%) أعلى من الحد النظامي المعتاد ({ceil_:g}%). "
                "راجع الأرقام. الحد من قرار هيئة الدواء 480/2026 وبيختلف حسب سعر العبوة ومحلي/مستورد.")
    return None

def implied_discount(retail, net_price):
    """Implied total discount % off the official retail price, computed from the user's
    own numbers. An estimate, never a verified figure. Returns rounded pct or None."""
    try:
        r, n = float(retail), float(net_price)
    except (TypeError, ValueError):
        return None
    if r <= 0 or n < 0: return None
    return round((1 - n / r) * 100, 1)

def build_agreed_offers(allo, cmp_df, suppliers):
    """Offer dicts for the items the chosen suppliers won in the comparison, keyed by the
    supplier's own item name (orig_item) so a later invoice written in the supplier's
    wording matches exactly. Used to hand the agreed offers to check_invoice without a
    manual re-upload."""
    won = {}
    for _, r in cmp_df.iterrows():
        won.setdefault(r["أرخص مورد"], set()).add(r["الصنف"])
    out = []
    for _, r in allo.iterrows():
        sup = r["supplier"]
        if sup not in suppliers or r["item"] not in won.get(sup, set()):
            continue
        def _num(x):
            return x if x is not None and not (isinstance(x, float) and pd.isna(x)) else 0
        out.append(dict(item=r["orig_item"] if r.get("orig_item") else r["item"],
            supplier=sup, price=float(r["price"]), discount=float(_num(r.get("discount", 0)) or 0),
            min_qty=_num(r.get("min_qty", 0)) or 0,
            expiry=r["expiry"] if pd.notna(r.get("expiry")) else None,
            batch=str(r.get("batch") or "")))
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

_PACK_RE = re.compile(
    r"(\d+)\s*(?:tab|tabs|tablet|tablets|cap|caps|capsule|capsules|amp|amps|ampoule|ampoules"
    r"|sachet|sachets|قرص|اقراص|كبسوله|كبسولات|امبول|امبولات|كيس|اكياس)\b", re.I)

def pack_size(s):
    """Units per pack from a name (Panadol Extra 24 tab -> 24, كونكور 30 قرص -> 30).
    None when the name states no pack count."""
    if s is None: return None
    m = _PACK_RE.search(_fold(norm(str(s)).lower()))
    return int(m.group(1)) if m else None

def _no_pack(s):
    """Name text with the pack-count phrase removed, so strength() never reads a pack
    count as a strength (Panadol Extra 24 tab has strength '', not '24')."""
    return _PACK_RE.sub(" ", _fold(norm(str(s)).lower()))

def _is_strip(s):
    t = _fold(norm(str(s)).lower())
    return "شريط" in t or "strip" in t

def check_invoice(offers, invoice, invoice_vat=False, offer_vat=False, vat_rate=14.0):
    """Compare invoice lines to the agreed offer. Only exact dictionary matches get a
    price verdict. Fuzzy matches, strength conflicts, pack-size conflicts, strip-vs-box
    lines, multi-strength offers and multi-price lines are flagged for manual review
    (fail closed): they are never counted in the over-billing total and never drafted.
    invoice_vat / offer_vat: the side's prices include VAT, stripped at vat_rate before
    comparing so both sides stand on the same tax basis."""
    base = {}
    for o in offers:
        base.setdefault(canon(o["item"]), []).append(o)
    rows = []
    vat_div = 1 + vat_rate / 100

    def onet(o):
        return o["price"] * (1 - o.get("discount", 0) / 100) / (vat_div if offer_vat else 1)

    def out(line, status, o=None, net=None, pct=None, val=None, note="", inet=None):
        rows.append({"الصنف في الفاتورة": line["item"], "الصنف في العرض": (o or {}).get("item", ""),
            "المورد": (o or {}).get("supplier", ""), "سعر العرض بعد الخصم": net,
            "سعر الفاتورة": line["price"], "صافي الفاتورة قبل الضريبة": inet,
            "الفرق %": pct, "الكمية": line.get("qty"),
            "قيمة الفرق": val, "الحالة": status, "ملاحظة": note})

    for line in invoice:
        uprice = round(line["price"] / vat_div, 2) if invoice_vat else None
        cmp_price = uprice if invoice_vat else line["price"]
        c, s = canon(line["item"]), strength(_no_pack(line["item"]))
        cands = base.get(c)
        if not cands:
            kk = difflib.get_close_matches(c, list(base), n=1, cutoff=0.6)
            if kk:
                o0 = min(base[kk[0]], key=onet)
                out(line, "تحقق: المطابقة مش مؤكدة", o0, note="اتطابق تقريبي مع: " + o0["item"], inet=uprice)
            else:
                out(line, "صنف مش في العرض", inet=uprice)
            continue
        o_str = {id(o): strength(_no_pack(o["item"])) for o in cands}
        if s:
            same = [o for o in cands if o_str[id(o)] == s]
            nostr = [o for o in cands if not o_str[id(o)]]
            if same:
                cands = same
            elif nostr:
                cands = nostr
            else:
                strengths = sorted({o_str[id(o)] for o in cands})
                out(line, "تحقق: التركيز مختلف", cands[0], note="تركيز العرض: " + "، ".join(strengths), inet=uprice)
                continue
        else:
            nostr = [o for o in cands if not o_str[id(o)]]
            strengths = sorted({o_str[id(o)] for o in cands if o_str[id(o)]})
            if nostr:
                cands = nostr
            elif len(strengths) > 1:
                out(line, "تحقق: التركيز مش محدد في الفاتورة", cands[0],
                    note="تركيزات العرض: " + "، ".join(strengths), inet=uprice)
                continue
        ip = pack_size(line["item"])
        if ip is not None:
            same_p = [o for o in cands if pack_size(o["item"]) == ip]
            if same_p:
                cands = same_p
            else:
                opacks = sorted({pack_size(o["item"]) for o in cands if pack_size(o["item"])})
                if opacks:
                    out(line, "تحقق: حجم العبوة مختلفة", cands[0],
                        note="عبوة العرض: " + "، ".join(str(p) for p in opacks) + f" — عبوة الفاتورة: {ip}", inet=uprice)
                    continue
        elif _is_strip(line["item"]) and not any(_is_strip(o["item"]) for o in cands):
            out(line, "تحقق: الفاتورة بالشريط", cands[0],
                note="الفاتورة مسعّرة بالشريط والعرض بالعلبة أو الوحدة الكاملة", inet=uprice)
            continue
        nets = sorted({round(onet(o), 2) for o in cands})
        if len(nets) > 1:
            out(line, "غامض: أكتر من سعر في العروض", cands[0],
                note="الأسعار: " + "، ".join(f"{x:,.2f}" for x in nets), inet=uprice)
            continue
        net = nets[0]
        o = next(o for o in cands if round(onet(o), 2) == net)
        diff = round(cmp_price - net, 2)
        pct = round((cmp_price / net - 1) * 100, 1) if net else 0
        q = line.get("qty")
        if abs(pct) <= 0.5:
            status = "مطابق"
        elif pct > 0:
            status = f"أعلى من العرض بـ {pct}%"
        else:
            status = f"أقل من العرض بـ {abs(pct)}%"
        note = ""
        if invoice_vat: note += f"اتفكت ضريبة {vat_rate:g}% من سعر الفاتورة. "
        if offer_vat: note += f"سعر العرض بعد فك ضريبة {vat_rate:g}%. "
        out(line, status, o, net, pct, round(diff * q, 2) if q else diff, note.strip(), inet=uprice)
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
    """parse_whatsapp plus the WhatsApp message date from Android or iPhone exports.
    Every price line inside a dated message gets that message's date, including the
    extra lines of a multi-line message."""
    rows = []
    for d, _s, body in split_whatsapp_messages(text):
        for line in body.splitlines():
            r = _price_row_from_line(norm(line), supplier)
            if r:
                rows.append(dict(r, date=d))
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



def history_price_stats(hist, items):
    """Per stock item: last net price seen and lowest net price seen in the price
    history. Items match by canonical name + strength (كونكور 5 never mixes with
    كونكور 10); a history row with no strength only fills the lone same-name item or
    a strength-free one, never a guess between strengths. Dates compare as strings
    (YYYY-MM-DD sorts right; empty dates count as oldest)."""
    out = {}
    if hist is None or len(hist) == 0:
        return out
    items = [str(x) for x in items]
    bycanon = {}
    for it in items:
        bycanon.setdefault(canon(it), []).append(it)
    for _, r in hist.iterrows():
        nm = str(r["الصنف"])
        net = num(r["الصافي"])
        if net is None:
            continue
        c, s = canon(nm), strength(_no_pack(nm))
        cands = bycanon.get(c)
        if not cands:
            continue
        hits = [it for it in cands if strength(it) == s]
        if not hits and not s:
            nostr = [it for it in cands if not strength(it)]
            hits = nostr if nostr else (cands if len(cands) == 1 else [])
        d = str(r["التاريخ"] or "")
        for it in hits:
            st = out.setdefault(it, {"count": 0, "min": None, "min_date": "", "last": None, "last_date": ""})
            st["count"] += 1
            if st["min"] is None or net < st["min"]:
                st["min"], st["min_date"] = net, d
            if d >= st["last_date"]:
                st["last"], st["last_date"] = net, d
    return out

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
    "item": ["اسم الصنف", "إسم الصنف", "الصنف", "صنف", "اسم", "منتج", "دواء", "وصف", "item", "name", "product", "description", "drug", "medicine"],
    "stock": ["مخزون", "رصيد", "كمية", "متاح", "stock", "qty", "quantity", "balance", "on hand", "amount", "units"],
    "monthly_sales": ["مبيعات", "شهري", "معدل", "monthly", "sales", "average", "avg"],
    "expiry": ["صلاحية", "انتهاء", "expiry", "expiration", "exp"],
    "cost": ["تكلفة", "سعر الشراء", "شراء", "cost", "سعر", "price"],
    "price": ["سعر", "تكلفة", "price", "cost"],
    "discount": ["خصم", "discount", "disc"],
    "min_qty": ["حد", "أقل كمية", "اقل كمية", "min", "moq"],
    "batch": ["تشغيلة", "باتش", "batch", "lot"],
    "qty": ["كمية", "العدد", "عدد", "qty", "quantity", "units"],
    "bonus": ["بونص", "bonus"],
}


def guess_columns(columns, fields):
    """Map canonical field names to actual column labels via normalized substring synonyms.
    Synonyms are tried most-specific first; each column is used at most once."""
    mapping, used = {}, set()
    for f in fields:
        for w in COL_SYNS.get(f, [f]):
            hit = next((c for c in columns if c not in used and w in norm(str(c)).lower()
                        and not (f == "item" and any(x in norm(str(c)).lower() for x in ("رقم", "كود", "code", "id")))), None)
            if hit is not None:
                mapping[f] = hit
                used.add(hit)
                break
    return mapping


OFFERS_AR = {"item": "الصنف", "supplier": "المورد", "price": "السعر", "discount": "الخصم %",
    "min_qty": "أقل كمية", "net": "الصافي", "bonus": "البونص", "expiry": "الصلاحية",
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


# ---------------- unified user data file (بياناتي.xlsx) ----------------

MYDATA_SHEETS = {"links": "روابط", "history": "سجل الأسعار", "suppliers": "الموردين", "settings": "إعدادات", "discounts": "خصومات الأصناف", "public": "أسعار الجمهور", "public_src": "مصدر الأسعار", "item_disc": "أساسي الأصناف", "reference": "أسعار فارما أوفرسيز", "stock": "المخزون", "batches": "التشغيلات", "returns": "مرتجعات ونواقص", "cofix": "تصحيحات الشركات"}

STOCK_SHEET_COLS = ["الصنف", "الكمية", "باركود", "الكود", "الشركة", "الموقع", "المرجح %", "اخر خصم %", "الصنف في القاموس", "إجمالي التكلفة", "إجمالي الكمية", "رصيد الكوته", "الحد الأدنى", "مبيعات الشهر"]

BATCH_SHEET_COLS = ["الصنف", "الباتش", "تاريخ انتهاء الصلاحية", "الكمية"]

def fix_batch_sheet(df):
    """Normalize a التشغيلات (batch/expiry) sheet. Never raises; dates become
    YYYY-MM-DD strings, missing columns become empty, empty names dropped."""
    if df is None or df.empty:
        return pd.DataFrame(columns=BATCH_SHEET_COLS)
    d = df.copy()
    d.columns = [str(c).strip() for c in d.columns]
    for c in BATCH_SHEET_COLS:
        if c not in d.columns: d[c] = ""
    d = d[BATCH_SHEET_COLS]
    d["الصنف"] = d["الصنف"].fillna("").astype(str).str.strip()
    d["الباتش"] = d["الباتش"].fillna("").astype(str).str.strip()
    _dt = pd.to_datetime(d["تاريخ انتهاء الصلاحية"], errors="coerce", dayfirst=True)
    d["تاريخ انتهاء الصلاحية"] = _dt.dt.strftime("%Y-%m-%d").fillna(d["تاريخ انتهاء الصلاحية"].fillna("").astype(str).str.strip())
    d.loc[d["تاريخ انتهاء الصلاحية"].isin(["nan", "NaT", "None"]), "تاريخ انتهاء الصلاحية"] = ""
    d["الكمية"] = pd.to_numeric(d["الكمية"], errors="coerce")
    return d[d["الصنف"] != ""].reset_index(drop=True)

RETURNS_SHEET_COLS = ["التاريخ", "الصنف", "المورد", "الكمية", "النوع", "السبب", "الحالة"]

COFIX_COLS = ["الصنف", "الشركة المعتمدة", "ملاحظة"]

def price_trend_flags(history):
    """canon item -> "⬆ زاد" / "⬇ نزل" from the latest recorded change in his own
    offers history (price_history_summary). Latest change per item wins. Never raises."""
    out = {}
    try:
        if history is None or history.empty: return out
        ps = price_history_summary(history)
        if ps.empty or "التغير عن السابق %" not in ps.columns: return out
        if "آخر تاريخ" in ps.columns:
            ps = ps.sort_values("آخر تاريخ")
        for _, r in ps.iterrows():
            dv = r.get("التغير عن السابق %")
            if pd.isna(dv) or dv == 0: continue
            k = _canon_fast(r.get("الصنف", ""))
            if k: out[k] = "⬆ زاد" if dv > 0 else "⬇ نزل"
    except Exception:
        pass
    return out

def fix_cofix(df):
    """Normalize a تصحيحات الشركات sheet (his own approved per-item company decisions).
    Never raises; one row per item (last wins), empty names dropped."""
    if df is None or df.empty:
        return pd.DataFrame(columns=COFIX_COLS)
    d = df.copy()
    d.columns = [str(c).strip() for c in d.columns]
    for c in COFIX_COLS:
        if c not in d.columns: d[c] = ""
    d = d[COFIX_COLS]
    for c in COFIX_COLS:
        d[c] = d[c].fillna("").astype(str).str.strip()
    d = d[(d["الصنف"] != "") & (d["الشركة المعتمدة"] != "")]
    d = d.drop_duplicates(subset="الصنف", keep="last").reset_index(drop=True)
    return d

def cofix_map(cofix):
    """{canon item name -> approved company} from a تصحيحات الشركات sheet."""
    m = {}
    if cofix is None or cofix.empty: return m
    for _, r in cofix.iterrows():
        k = _canon_fast(r["الصنف"])
        if k: m[k] = str(r["الشركة المعتمدة"]).strip()
    return m

def cofix_upsert(cofix, item, company, note=""):
    """Add or replace one approved-company decision. Returns a fresh fixed sheet."""
    base = fix_cofix(cofix)
    k = _canon_fast(item)
    if len(base):
        base = base[base["الصنف"].map(lambda x: _canon_fast(x) != k)]
    base = pd.concat([base, pd.DataFrame([{"الصنف": str(item).strip(),
        "الشركة المعتمدة": str(company).strip(), "ملاحظة": note}])], ignore_index=True)
    return fix_cofix(base)

def fix_returns_sheet(df):
    """Normalize a مرتجعات ونواقص (returns/shortages log) sheet. Never raises; dates
    become YYYY-MM-DD strings, النوع is مرتجع or ناقص, الحالة defaults to مسودة."""
    if df is None or df.empty:
        return pd.DataFrame(columns=RETURNS_SHEET_COLS)
    d = df.copy()
    d.columns = [str(c).strip() for c in d.columns]
    for c in RETURNS_SHEET_COLS:
        if c not in d.columns: d[c] = ""
    d = d[RETURNS_SHEET_COLS]
    for c in ("الصنف", "المورد", "النوع", "السبب", "الحالة"):
        d[c] = d[c].fillna("").astype(str).str.strip()
    _dt = pd.to_datetime(d["التاريخ"], errors="coerce", dayfirst=True)
    d["التاريخ"] = _dt.dt.strftime("%Y-%m-%d").fillna(d["التاريخ"].fillna("").astype(str).str.strip())
    d.loc[d["التاريخ"].isin(["nan", "NaT", "None"]), "التاريخ"] = ""
    d["الكمية"] = pd.to_numeric(d["الكمية"], errors="coerce")
    d.loc[~d["النوع"].isin(["مرتجع", "ناقص"]), "النوع"] = "مرتجع"
    d.loc[d["الحالة"] == "", "الحالة"] = "مسودة"
    return d[d["الصنف"] != ""].reset_index(drop=True)

def stock_display_names(d):
    """Per-row match/display name for a fixed stock sheet: the pre-matched dictionary
    name (الصنف في القاموس) when present, else the raw الصنف. The raw export's names
    can carry mojibake from the source system; the matched column is the clean bridge."""
    alt = d["الصنف في القاموس"].fillna("").astype(str).str.strip()
    return alt.where(alt != "", d["الصنف"])

def suggested_order(stock, default_min=5):
    """Build the suggested-order table from the بياناتي stock sheet. An item enters
    when on-hand <= its الحد الأدنى (empty min = default_min). Suggested qty is
    max(min x 2 - on_hand, 1), an assumption until real sales data exists. Unit cost
    comes from إجمالي التكلفة / إجمالي الكمية when present. Never raises."""
    cols = ["الصنف", "الشركة", "الكمية الحالية", "الحد الأدنى", "الكمية المقترحة",
            "تكلفة الوحدة", "قيمة مقترحة", "رصيد الكوته"]
    if stock is None or stock.empty:
        return pd.DataFrame(columns=cols)
    d = fix_stock_sheet(stock)
    if d.empty:
        return pd.DataFrame(columns=cols)
    onhand = pd.to_numeric(d["الكمية"], errors="coerce").fillna(0)
    mn = pd.to_numeric(d["الحد الأدنى"], errors="coerce").fillna(default_min)
    mn = mn.where(mn > 0, default_min)
    sug = (mn * 2 - onhand).clip(lower=1)
    _tq = pd.to_numeric(d["إجمالي الكمية"], errors="coerce")
    cost = pd.to_numeric(d["إجمالي التكلفة"], errors="coerce") / _tq.where(_tq != 0)
    out = pd.DataFrame({
        "الصنف": stock_display_names(d), "الشركة": d["الشركة"],
        "الكمية الحالية": onhand, "الحد الأدنى": mn,
        "الكمية المقترحة": sug.round(0).astype(int),
        "تكلفة الوحدة": cost.round(2),
        "قيمة مقترحة": (sug * cost).round(2),
        "رصيد الكوته": pd.to_numeric(d["رصيد الكوته"], errors="coerce"),
    })
    _q = pd.to_numeric(d["رصيد الكوته"], errors="coerce")
    out["الكمية المقترحة"] = [min(s, int(q)) if pd.notna(q) and q > 0 else s
                              for s, q in zip(out["الكمية المقترحة"], _q)]
    out["قيمة مقترحة"] = (out["الكمية المقترحة"] * out["تكلفة الوحدة"]).round(2)
    out = out[out["الكمية الحالية"] <= out["الحد الأدنى"]]
    return out.sort_values("قيمة مقترحة", ascending=False, na_position="last").reset_index(drop=True)

def fix_stock_sheet(df):
    """Normalize a المخزون balances sheet inside بياناتي.xlsx. Never raises; missing
    columns become empty, unknown extra columns dropped, empty names dropped."""
    if df is None or df.empty:
        return pd.DataFrame(columns=STOCK_SHEET_COLS)
    d = df.copy()
    d.columns = [str(c).strip() for c in d.columns]
    for c in STOCK_SHEET_COLS:
        if c not in d.columns: d[c] = ""
    d = d[STOCK_SHEET_COLS]
    for c in ("الصنف", "باركود", "الكود", "الشركة", "الموقع", "الصنف في القاموس"):
        d[c] = d[c].fillna("").astype(str).str.strip()
    for c in ("الكمية", "المرجح %", "اخر خصم %", "إجمالي التكلفة", "إجمالي الكمية", "رصيد الكوته", "الحد الأدنى", "مبيعات الشهر"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d[d["الصنف"] != ""].reset_index(drop=True)

PUBLIC_COLS = ["الصنف", "الاسم الإنجليزي", "الشركة", "سعر الجمهور", "السعر السابق", "المادة الفعالة", "الباركود", "الوحدات", "الفئة", "سعر الصيدلي التقديري (متعلم)", "تخمين تقريبي (متوسط الشركة)"]

def fix_public(df):
    """Normalize a أسعار الجمهور sheet: fixed known columns, numeric prices, no empty
    names. Never raises; missing columns become empty, unknown extra columns dropped."""
    if df is None or df.empty:
        return pd.DataFrame(columns=PUBLIC_COLS)
    d = df.copy()
    d.columns = [str(c).strip() for c in d.columns]
    for c in PUBLIC_COLS:
        if c not in d.columns: d[c] = ""
    d = d[PUBLIC_COLS]
    for c in ("الصنف", "الاسم الإنجليزي", "الشركة", "المادة الفعالة", "الباركود", "الوحدات", "الفئة"):
        d[c] = d[c].fillna("").astype(str).str.strip()
    for c in ("سعر الجمهور", "السعر السابق", "سعر الصيدلي التقديري (متعلم)", "تخمين تقريبي (متوسط الشركة)"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d.loc[d["الصنف"] == "", "الصنف"] = d.loc[d["الصنف"] == "", "الاسم الإنجليزي"]
    return d[(d["الصنف"] != "") | (d["الاسم الإنجليزي"] != "")].reset_index(drop=True)

def _canon_fast(s):
    """Alias-resolved canonical key without the fuzzy pass; consistent for indexing
    and lookup of the public price list."""
    k = _key(s)
    return ALIAS_LOOKUP.get(k, k)

def public_price_index(public_df):
    """Build a lookup map {(canon, strength): (price, company)} from the أسعار الجمهور
    sheet, indexing both the Arabic and the English name of every row. Conflicting
    prices for the same key are dropped (fail-closed: value None)."""
    m = {}
    if public_df is None or public_df.empty: return m
    for _, r in public_df.iterrows():
        p = r["سعر الجمهور"]
        if p is None or (isinstance(p, float) and pd.isna(p)) or float(p) <= 0: continue
        co = str(r["الشركة"]).strip()
        for nm in (r["الصنف"], r["الاسم الإنجليزي"]):
            c = _canon_fast(nm)
            if not c: continue
            k = (c, strength(nm))
            if k in m:
                if m[k] is not None and m[k][0] != float(p): m[k] = None
            else:
                m[k] = (float(p), co, str(r["الصنف"]).strip())
    return m

def _pub_lookup(item, m):
    """Shared fail-closed lookup over the public price map -> (price, company) or None."""
    if not m or not str(item or "").strip(): return None
    c, st_ = _canon_fast(item), strength(item)
    if not c: return None
    if st_:
        return m.get((c, st_))
    hits = [v for (cc, s), v in m.items() if cc == c and v]
    prices = {p for p, _, _ in hits}
    if len(prices) != 1: return None
    cos = [co for _, co, _ in hits if co]
    disp = next((dn for _, _, dn in hits if dn), "")
    return prices.pop(), (max(set(cos), key=cos.count) if cos else ""), disp

def find_public_price(item, index):
    """Public retail price for an item from the index map, fail-closed: same canonical
    name required; a strength-carrying item only matches the same strength; an
    ambiguous or conflicting hit returns None."""
    hit = _pub_lookup(item, index)
    return hit[0] if hit else None

def find_public_row(item, index):
    """(public price, company, display name) for an item, fail-closed like
    find_public_price."""
    return _pub_lookup(item, index)

# ---------------- learned per-item base discounts (أساسي الأصناف, estimates) ----------------

ITEM_DISC_COLS = ["الصنف", "الشركة", "أساسي % (متعلم)", "عدد العينات", "آخر تحديث"]

def fix_item_learned(df):
    """Normalize an أساسي الأصناف sheet (per-item learned base discounts). Never raises."""
    if df is None or df.empty:
        return pd.DataFrame(columns=ITEM_DISC_COLS)
    d = df.copy()
    d.columns = [str(c).strip() for c in d.columns]
    for c in ITEM_DISC_COLS:
        if c not in d.columns: d[c] = ""
    d = d[ITEM_DISC_COLS]
    for c in ("الصنف", "الشركة", "آخر تحديث"):
        d[c] = d[c].fillna("").astype(str).str.strip()
    d["أساسي % (متعلم)"] = pd.to_numeric(d["أساسي % (متعلم)"], errors="coerce")
    d["عدد العينات"] = pd.to_numeric(d["عدد العينات"], errors="coerce").fillna(0).astype(int)
    return d[d["الصنف"] != ""].reset_index(drop=True)

def implied_base_samples(lines, index):
    """From loaded offer/invoice lines ({item, price} = price the pharmacy pays), learn
    the implied base discount % PER ITEM vs the official public price. Fail-closed item
    matching; implausible values (<=0% or >60%) are dropped. Returns
    {(canon, strength): {"name": display, "company": co, "bases": [..]}}."""
    out = {}
    if not index: return out
    for ln in lines or []:
        price = num(ln.get("price"))
        if price is None or price <= 0: continue
        c, st_ = _canon_fast(ln.get("item")), strength(ln.get("item"))
        hit = _pub_lookup(ln.get("item"), index)
        if not hit: continue
        pub, co, disp = hit
        if not pub or price >= pub: continue
        base = (1 - price / pub) * 100
        if not (0 < base <= 60): continue
        key = (c, st_) if st_ else (c, strength(disp))
        e = out.setdefault(key, {"name": disp or str(ln.get("item")).strip(), "company": co, "bases": []})
        e["bases"].append(round(base, 2))
    return out

def merge_item_bases(existing, samples, today=None):
    """Merge new per-item base samples into the أساسي الأصناف sheet. Each new batch
    contributes its median (outlier-safe), weighted with the stored base by sample
    count. Every value is an estimate learned from the user's own files, per item —
    never a company-wide assumption."""
    import datetime as _dt
    today = today or _dt.date.today()
    df = fix_item_learned(existing)
    rows = {(_canon_fast(r["الصنف"]), strength(r["الصنف"])): r for _, r in df.iterrows()}
    for key, e in (samples or {}).items():
        bases = sorted(e["bases"])
        if not bases: continue
        med = bases[len(bases) // 2] if len(bases) % 2 else (bases[len(bases) // 2 - 1] + bases[len(bases) // 2]) / 2
        if key in rows:
            r = rows[key]
            ob, on = r["أساسي % (متعلم)"], int(r["عدد العينات"])
            ob = float(ob) if pd.notna(ob) else med
            nn = on + len(bases)
            nb = round((ob * on + med * len(bases)) / nn, 2)
            rows[key] = pd.Series({"الصنف": r["الصنف"], "الشركة": r["الشركة"], "أساسي % (متعلم)": nb, "عدد العينات": nn, "آخر تحديث": str(today)})
        else:
            rows[key] = pd.Series({"الصنف": e["name"], "الشركة": e["company"], "أساسي % (متعلم)": round(med, 2), "عدد العينات": len(bases), "آخر تحديث": str(today)})
    out = pd.DataFrame(list(rows.values()), columns=ITEM_DISC_COLS)
    return out.sort_values("الصنف").reset_index(drop=True) if len(out) else fix_item_learned(None)

def item_base(item, idf):
    """Stored learned base % for this exact item (canonical name + strength), else None."""
    if idf is None or len(idf) == 0 or not str(item or "").strip(): return None
    c, st_ = _canon_fast(item), strength(item)
    for _, r in idf.iterrows():
        if _canon_fast(r["الصنف"]) != c: continue
        rs = strength(r["الصنف"])
        if st_ and rs == st_:
            v = r["أساسي % (متعلم)"]
            return float(v) if pd.notna(v) else None
    if not st_:
        vals = [r["أساسي % (متعلم)"] for _, r in idf.iterrows() if _canon_fast(r["الصنف"]) == c]
        vals = [float(v) for v in vals if pd.notna(v)]
        if len(vals) == 1: return vals[0]
    return None

def company_median_base(company, idf):
    """Rough guess only: the median of this company's LEARNED per-item bases. Never
    presented as the item's own base; callers must label it as a rough guess."""
    if idf is None or len(idf) == 0 or not str(company or "").strip(): return None
    k = str(company).strip().lower()
    vals = [float(r["أساسي % (متعلم)"]) for _, r in idf.iterrows()
            if str(r["الشركة"]).strip().lower() == k and pd.notna(r["أساسي % (متعلم)"])]
    if not vals: return None
    vals.sort()
    return round(vals[len(vals) // 2] if len(vals) % 2 else (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2, 2)

def est_pharmacy_price(public_price, base_pct):
    """Estimated pharmacy price = official public price x (1 - base%). Estimate only."""
    if public_price is None or base_pct is None: return None
    if pd.isna(public_price) or pd.isna(base_pct): return None
    return round(float(public_price) * (1 - float(base_pct) / 100), 2)
SUPPLIER_COLS = ["المورد", "مدة التوريد (يوم)"]
SETTINGS_COLS = ["الإعداد", "القيمة"]


def load_my_data(f):
    """Read the unified بياناتي.xlsx workbook. Returns dict with keys:
    links (offer->stock mapping), history (DataFrame or None), suppliers (DataFrame or
    None), settings (dict of str->value). Missing sheets or an unreadable file give
    empty parts; this never raises."""
    out = {"links": {}, "history": None, "suppliers": None, "settings": {}, "discounts": None, "public": None, "public_src": None, "item_disc": None, "reference": None, "stock": None, "batches": None, "returns": None, "cofix": None}
    if isinstance(f, (bytes, bytearray)):
        f = io.BytesIO(f)
    try:
        xl = pd.ExcelFile(f)
    except Exception:
        return out
    names = set(xl.sheet_names)
    try:
        if MYDATA_SHEETS["links"] in names:
            out["links"] = df_to_links(pd.read_excel(xl, MYDATA_SHEETS["links"]))
        if MYDATA_SHEETS["history"] in names:
            h = pd.read_excel(xl, MYDATA_SHEETS["history"])
            if not h.empty and all(c in h.columns for c in HIST_COLS):
                out["history"] = h[HIST_COLS]
        if MYDATA_SHEETS["discounts"] in names:
            dd = pd.read_excel(xl, MYDATA_SHEETS["discounts"])
            dd = fix_discounts(dd)
            if not dd.empty:
                out["discounts"] = dd
        if MYDATA_SHEETS["public"] in names:
            pp = fix_public(pd.read_excel(xl, MYDATA_SHEETS["public"]))
            if not pp.empty:
                out["public"] = pp
        if MYDATA_SHEETS["public_src"] in names:
            ps = pd.read_excel(xl, MYDATA_SHEETS["public_src"])
            if not ps.empty:
                out["public_src"] = ps
        if MYDATA_SHEETS["item_disc"] in names:
            idf = fix_item_learned(pd.read_excel(xl, MYDATA_SHEETS["item_disc"]))
            if not idf.empty:
                out["item_disc"] = idf
        if MYDATA_SHEETS["stock"] in names:
            out["stock"] = fix_stock_sheet(pd.read_excel(xl, MYDATA_SHEETS["stock"]))
        if MYDATA_SHEETS["batches"] in names:
            out["batches"] = fix_batch_sheet(pd.read_excel(xl, MYDATA_SHEETS["batches"]))
        if MYDATA_SHEETS["returns"] in names:
            out["returns"] = fix_returns_sheet(pd.read_excel(xl, MYDATA_SHEETS["returns"]))
        if MYDATA_SHEETS["cofix"] in names:
            cf = fix_cofix(pd.read_excel(xl, MYDATA_SHEETS["cofix"]))
            if not cf.empty:
                out["cofix"] = cf
        if MYDATA_SHEETS["reference"] in names:
            rf = fix_reference(pd.read_excel(xl, MYDATA_SHEETS["reference"]))
            if not rf.empty:
                out["reference"] = rf
        if MYDATA_SHEETS["suppliers"] in names:
            s = pd.read_excel(xl, MYDATA_SHEETS["suppliers"])
            if not s.empty and len(s.columns) >= 2:
                s = s.iloc[:, :2]
                s.columns = SUPPLIER_COLS
                out["suppliers"] = s.dropna(how="all").reset_index(drop=True)
        if MYDATA_SHEETS["settings"] in names:
            st_df = pd.read_excel(xl, MYDATA_SHEETS["settings"])
            if len(st_df.columns) >= 2:
                out["settings"] = {str(k).strip(): v for k, v in zip(st_df.iloc[:, 0], st_df.iloc[:, 1])
                                   if pd.notna(k) and str(k).strip()}
    except Exception:
        pass
    return out


def build_my_data(links=None, history=None, suppliers=None, settings=None, discounts=None, public=None, public_src=None, item_disc=None, reference=None, stock=None, batches=None, returns=None, cofix=None):
    """Serialize the unified workbook to xlsx bytes. Empty parts become header-only
    sheets so the file always has the same five sheets."""
    links_df = links_to_df(links or {})
    hist_df = history if history is not None and not history.empty else pd.DataFrame(columns=HIST_COLS)
    sup_df = suppliers if suppliers is not None and not suppliers.empty else pd.DataFrame(columns=SUPPLIER_COLS)
    set_df = pd.DataFrame([{SETTINGS_COLS[0]: k, SETTINGS_COLS[1]: v} for k, v in (settings or {}).items()],
                          columns=SETTINGS_COLS)
    disc_df = fix_discounts(discounts)
    b = io.BytesIO()
    with pd.ExcelWriter(b, engine="openpyxl") as w:
        links_df.to_excel(w, sheet_name=MYDATA_SHEETS["links"], index=False)
        hist_df.to_excel(w, sheet_name=MYDATA_SHEETS["history"], index=False)
        sup_df.to_excel(w, sheet_name=MYDATA_SHEETS["suppliers"], index=False)
        set_df.to_excel(w, sheet_name=MYDATA_SHEETS["settings"], index=False)
        disc_df.to_excel(w, sheet_name=MYDATA_SHEETS["discounts"], index=False)
        if public is not None and not public.empty:
            fix_public(public).to_excel(w, sheet_name=MYDATA_SHEETS["public"], index=False)
            if public_src is not None and not public_src.empty:
                public_src.to_excel(w, sheet_name=MYDATA_SHEETS["public_src"], index=False)
        fix_item_learned(item_disc).to_excel(w, sheet_name=MYDATA_SHEETS["item_disc"], index=False)
        if reference is not None and not reference.empty:
            fix_reference(reference).to_excel(w, sheet_name=MYDATA_SHEETS["reference"], index=False)
        if stock is not None and not stock.empty:
            fix_stock_sheet(stock).to_excel(w, sheet_name=MYDATA_SHEETS["stock"], index=False)
        if batches is not None and not batches.empty:
            fix_batch_sheet(batches).to_excel(w, sheet_name=MYDATA_SHEETS["batches"], index=False)
        if returns is not None and not returns.empty:
            fix_returns_sheet(returns).to_excel(w, sheet_name=MYDATA_SHEETS["returns"], index=False)
        if cofix is not None and not cofix.empty:
            fix_cofix(cofix).to_excel(w, sheet_name=MYDATA_SHEETS["cofix"], index=False)
    return b.getvalue()


# ---------------- Farma Overseas reference sheet (أسعار فارما أوفرسيز) ----------------

REF_COLS = ["الصنف", "الكود", "الفئة", "الشركة/المورد", "محلي/مستورد (تقديري)",
            "سعر الجمهور", "سعر الصيدلي", "الهامش الكلي جنيه", "الخصم الضمني %",
            "الأساسي %", "ثقة الأساسي", "بديل الأساسي", "الهامش جنيه (بعد الأساسي)",
            "الضريبة (تقديري)", "الأساسي المؤكد (اكتبه هنا)", "الضريبة المؤكدة (اكتبها هنا)",
            "المادة الفعالة", "الاستخدام (معلومة عامة - مش نصيحة طبية)", "باركود"]
REF_NUM = ["سعر الجمهور", "سعر الصيدلي", "الهامش الكلي جنيه", "الخصم الضمني %",
           "الأساسي %", "بديل الأساسي", "الهامش جنيه (بعد الأساسي)",
           "الأساسي المؤكد (اكتبه هنا)", "الضريبة المؤكدة (اكتبها هنا)"]

def fix_reference(df):
    """Normalize an أسعار فارما أوفرسيز reference sheet. Never raises; missing columns
    become empty, unknown extra columns dropped, empty names dropped."""
    if df is None or df.empty:
        return pd.DataFrame(columns=REF_COLS)
    d = df.copy()
    d.columns = [str(c).strip() for c in d.columns]
    for c in REF_COLS:
        if c not in d.columns: d[c] = ""
    d = d[REF_COLS]
    for c in REF_COLS:
        if c not in REF_NUM:
            d[c] = d[c].fillna("").astype(str).str.strip()
    for c in REF_NUM:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["الكود"] = d["الكود"].astype(str).str.strip()
    d["باركود"] = d["باركود"].astype(str).str.strip()
    return d[(d["الصنف"] != "") | (d["الكود"] != "")].reset_index(drop=True)

def reference_index(ref_df):
    """Build {(canon, strength): row-dict} from the reference sheet. Conflicting rows
    for the same key are dropped (fail-closed: value None)."""
    m = {}
    if ref_df is None or ref_df.empty: return m
    for _, r in ref_df.iterrows():
        nm = r["الصنف"]
        c = _canon_fast(nm)
        if not c: continue
        k = (c, strength(nm))
        row = {col: (None if (col in REF_NUM and pd.isna(r[col])) else r[col]) for col in REF_COLS}
        if k in m:
            if m[k] is not None and m[k]["الكود"] != row["الكود"]: m[k] = None
        else:
            m[k] = row
    return m

def find_reference(item, index):
    """Reference row for an item, fail-closed like find_public_price."""
    if not index: return None
    c, st_ = _canon_fast(item), strength(item)
    hit = index.get((c, st_))
    if hit is None and (c, "") in index: hit = index.get((c, ""))
    return hit

def reference_barcode_index(ref_df):
    """Map barcode -> reference row for exact barcode search."""
    m = {}
    if ref_df is None or ref_df.empty: return m
    for _, r in ref_df.iterrows():
        b = str(r["باركود"]).strip()
        if b and b not in m:
            m[b] = {col: (None if (col in REF_NUM and pd.isna(r[col])) else r[col]) for col in REF_COLS}
    return m

def ref_base_confirmed(row):
    """The أساسي to trust for a reference row: his confirmed value if he wrote one,
    else the fitted/site value (always labeled by ثقة الأساسي upstream)."""
    if not row: return None
    v = row.get("الأساسي المؤكد (اكتبه هنا)")
    if v is not None and not (isinstance(v, float) and pd.isna(v)):
        try: return float(v)
        except Exception: pass
    v = row.get("الأساسي %")
    if v is None or (isinstance(v, float) and pd.isna(v)): return None
    return float(v)

def ref_tax_confirmed(row):
    """His confirmed tax % if written, else None (the estimate text stays in its column)."""
    if not row: return None
    v = row.get("الضريبة المؤكدة (اكتبها هنا)")
    if v is None or (isinstance(v, float) and pd.isna(v)): return None
    try: return float(v)
    except Exception: return None

# ---------------- equivalents dictionary (dict_full.csv, public eg-drugs data) ----------------

def _norm_active(a):
    """Normalize an active-ingredient string for grouping: lowercase, split combos,
    sorted, joined. Returns '' when unknown."""
    a = str(a or "").strip().lower()
    if not a or a in ("unknown", "none", "-"): return ""
    parts = re.split(r"[+,/;]|\band\b", a)
    parts = [re.sub(r"\s+", " ", p).strip() for p in parts if p.strip()]
    return "|".join(sorted(set(parts)))

def active_ingredient_index(dict_df):
    """Map normalized active -> list of dict row indices, for the equivalents feature."""
    m = {}
    if dict_df is None or dict_df.empty: return m
    for i, a in enumerate(dict_df["active"]):
        k = _norm_active(a)
        if k: m.setdefault(k, []).append(i)
    return m

def dict_lookup(query, dict_df):
    """Find a dict row for a free-text query: exact canon match first, then a unique
    prefix/contains match, then barcode. Fail-closed: None when ambiguous."""
    if dict_df is None or dict_df.empty: return None
    q = str(query or "").strip()
    if not q: return None
    if q.isdigit() and len(q) >= 8 and "barcode" in dict_df.columns:
        hits = [i for i, b in enumerate(dict_df["barcode"])
                if re.sub(r"\.0$", "", str(b).strip()) == q]
        if hits: return hits[0]
    qc = _canon_fast(q)
    if not qc: return None
    names = dict_df["name"].astype(str)
    qs = strength(q)
    def pick(cands):
        if not cands: return None
        if len(cands) == 1: return cands[0]
        if qs:
            sm = [i for i in cands if strength(names.iloc[i]) == qs]
            if sm: return sm[0]
        return cands[0]
    exact = [i for i, n in enumerate(names) if _canon_fast(n) == qc]
    if exact: return pick(exact)
    ar = dict_df["arabic"].astype(str) if "arabic" in dict_df.columns else None
    if ar is not None:
        fq = " ".join(_fold(q).split())
        def _far(n): return " ".join(_fold(str(n)).split())
        exact_ar = [i for i, n in enumerate(ar) if _far(n).strip() == fq]
        if exact_ar: return pick(exact_ar)
        cont_ar = [i for i, n in enumerate(ar) if fq and fq in _far(n)]
        if cont_ar: return pick(cont_ar)
        # Egyptian spelling varies (كونجيستال/كونجستال): retry with ي/ى squashed
        sq = fq.replace("\u064a", "")
        if sq and sq != fq:
            cont_sq = [i for i, n in enumerate(ar) if sq in _far(n).replace("\u064a", "")]
            if cont_sq: return pick(cont_sq)
        import difflib as _dl
        folded = [_fold(str(n)) for n in ar]
        close = _dl.get_close_matches(fq, [f for f in folded if f], n=6, cutoff=0.72)
        if close:
            cands = [folded.index(c) for c in close]
            return pick(cands)
    pref = [i for i, n in enumerate(names) if _canon_fast(n).startswith(qc)]
    if pref: return pick(pref)
    cont = [i for i, n in enumerate(names) if qc in _canon_fast(n)]
    return pick(cont)

def equivalents_for(dict_row_i, dict_df, aindex, limit=30):
    """Rows (list of dicts) sharing the same normalized active ingredient as dict row i."""
    if dict_row_i is None: return []
    a = _norm_active(dict_df.iloc[dict_row_i]["active"])
    if not a: return []
    out = []
    for i in aindex.get(a, [])[:limit]:
        r = dict_df.iloc[i]
        out.append({"name": str(r["name"]), "arabic": str(r.get("arabic", "")),
                    "company": str(r.get("company", "")), "barcode": str(r.get("barcode", "")),
                    "uses": str(r.get("uses", "")), "same_item": i == dict_row_i})
    return out

def find_reference_loose(query, ref_df, rindex=None):
    """Display-oriented reference search: exact canon+strength via the index first,
    then a case-insensitive substring scan of الصنف preferring a strength match.
    Returns a row dict or None. Never invents data; ambiguity just picks the closest
    display candidate after exact matching fails."""
    if ref_df is None or ref_df.empty: return None
    if rindex:
        hit = find_reference(query, rindex)
        if hit: return hit
    q = str(query or "").strip().lower()
    if not q: return None
    qs = strength(query)
    best = None
    for _, r in ref_df.iterrows():
        nm = str(r["الصنف"]).lower()
        if q in nm or _canon_fast(query) and _canon_fast(query) in _canon_fast(nm):
            row = {col: (None if (col in REF_NUM and pd.isna(r[col])) else r[col]) for col in REF_COLS}
            if qs:
                if strength(r["الصنف"]) == qs: return row
            elif best is None:
                best = row
    return None if qs else best

def reference_search_cache(ref_df):
    """One-time precomputed lists for fast reference search (built per upload)."""
    rows, names, canons, strs = [], [], [], []
    if ref_df is None or ref_df.empty: return ([], [], [], [])
    for _, r in ref_df.iterrows():
        row = {col: (None if (col in REF_NUM and pd.isna(r[col])) else r[col]) for col in REF_COLS}
        nm = str(r["الصنف"])
        rows.append(row); names.append(nm.lower()); canons.append(_canon_fast(nm)); strs.append(strength(nm))
    return (rows, names, canons, strs)

def find_reference_fast(query, cache):
    """find_reference_loose over a prebuilt reference_search_cache: ms per lookup.
    Fail-closed on strength mismatch (never shows another strength's price)."""
    rows, names, canons, strs = cache
    q = str(query or "").strip().lower()
    if not q or not rows: return None
    qc = _canon_fast(query); qs = strength(query)
    best = None
    for i, nm in enumerate(names):
        if q in nm or (qc and qc in canons[i]):
            if qs:
                if strs[i] == qs: return rows[i]
            elif best is None:
                best = rows[i]
    return None if qs else best

def dict_search_cache(dict_df):
    """One-time precomputed lists for fast dictionary search."""
    if dict_df is None or dict_df.empty: return None
    names = dict_df["name"].astype(str).tolist()
    ar = dict_df["arabic"].astype(str).tolist() if "arabic" in dict_df.columns else [""] * len(names)
    canons = [_canon_fast(n) for n in names]
    strs = [strength(n) for n in names]
    far = [" ".join(_fold(n).split()) for n in ar]
    far_sq = [f.replace("ي", "") for f in far]
    barcs = [re.sub(r"\.0$", "", str(b).strip()) for b in (dict_df["barcode"].tolist() if "barcode" in dict_df.columns else [""] * len(names))]
    return {"names": names, "canons": canons, "strs": strs, "far": far, "far_sq": far_sq, "barcs": barcs}

def dict_lookup_fast(query, dict_df, cache):
    """dict_lookup over a prebuilt dict_search_cache. Same matching order:
    barcode, exact canon, exact Arabic, Arabic contains (then ي-squashed), English
    prefix, English contains; strength-preferred within ties. Arabic names in the
    dataset carry the strength, so Arabic candidates match on the Arabic strength."""
    if dict_df is None or dict_df.empty or not cache: return None
    q = str(query or "").strip()
    if not q: return None
    names = cache["names"]
    def pick(cands, qs):
        if not cands: return None
        if len(cands) == 1: return cands[0]
        if qs:
            sm = [i for i in cands if cache["strs"][i] == qs or qs in str(dict_df["arabic"].iloc[i])]
            if sm: return sm[0]
        return cands[0]
    qs = strength(q)
    if q.isdigit() and len(q) >= 8:
        hits = [i for i, b in enumerate(cache["barcs"]) if b == q]
        if hits: return hits[0]
    qc = _canon_fast(q)
    if qc:
        exact = [i for i, c in enumerate(cache["canons"]) if c == qc]
        if exact: return pick(exact, qs)
    fq = " ".join(_fold(q).split())
    if fq and any("\u0600" <= ch <= "\u06ff" for ch in fq):
        ex = [i for i, f in enumerate(cache["far"]) if f == fq]
        if ex: return pick(ex, qs)
        ct = [i for i, f in enumerate(cache["far"]) if fq in f]
        if ct: return pick(ct, qs)
        sq = fq.replace("ي", "")
        if sq and sq != fq:
            ct = [i for i, f in enumerate(cache["far_sq"]) if sq in f]
            if ct: return pick(ct, qs)
    if qc:
        pref = [i for i, c in enumerate(cache["canons"]) if c.startswith(qc)]
        if pref: return pick(pref, qs)
        cont = [i for i, c in enumerate(cache["canons"]) if qc in c]
        return pick(cont, qs)
    return None


OPP_COLS = ["الصنف", "المورد", "الصافي", "أساسيك المسجل %", "أساسي العرض %", "الفرق %"]

def weekly_opportunities(allo, idf, pidx, min_gain=1.0):
    """Per-item buying opportunities in the uploaded offers: rows whose implied base
    discount (vs the official public price) beats the user's recorded per-item أساسي
    by at least min_gain percentage points. Strictly per item, never company-wide.
    Items without a recorded أساسي are skipped (not judged)."""
    out = pd.DataFrame(columns=OPP_COLS)
    if allo is None or len(allo) == 0 or not pidx:
        return out
    rows = []
    for _, r in allo.iterrows():
        net = num(r.get("net"))
        if net is None or net <= 0:
            net = num(r.get("price"))
        if net is None or net <= 0:
            continue
        hit = find_public_row(r.get("item"), pidx)
        if not hit:
            continue
        pub, co, disp = hit[0], hit[1], hit[2]
        if not pub or net >= pub:
            continue
        implied = (1 - net / pub) * 100
        if not (0 < implied <= 60):
            continue
        recorded = item_base(disp or r.get("item"), idf)
        if recorded is None:
            continue
        if implied - recorded >= min_gain:
            rows.append({"الصنف": disp or str(r.get("item")).strip(),
                         "المورد": r.get("supplier", ""),
                         "الصافي": round(net, 2),
                         "أساسيك المسجل %": round(recorded, 1),
                         "أساسي العرض %": round(implied, 1),
                         "الفرق %": round(implied - recorded, 1)})
    if rows:
        out = pd.DataFrame(rows, columns=OPP_COLS).sort_values("الفرق %", ascending=False).reset_index(drop=True)
    return out


def supplier_weekly_draft(supplier, order_items, opp_items):
    """WhatsApp-ready DRAFT text for one supplier: suggested-order quantities first,
    then this week's opportunity lines from their own offer. The user reviews and
    sends it himself - never sent automatically."""
    lines = ["السلام عليكم", "معايا طلب لو ينفع:"]
    n = 0
    if order_items is None:
        order_items = pd.DataFrame()
    for _, r in order_items.iterrows():
        n += 1
        qty = r.get("الكمية المقترحة", "")
        lines.append(f"{n}) {r.get('الصنف', '')} - {qty}")
    if opp_items is not None and len(opp_items):
        lines.append("ومهتم بالأصناف دي من عرضك:")
        for _, r in opp_items.iterrows():
            lines.append(f"- {r['الصنف']} (أساسي العرض {r['أساسي العرض %']}%)")
    lines.append("تأكيدك بالأسعار النهائية قبل التوريد لو سمحت.")
    return "\n".join(lines)


MARGIN_COLS = ["الصنف", "الشركة", "الشركة (القاموس)", "ملاحظة الشركة", "سعر الجمهور", "تكلفتك الحقيقية", "هامشك (جنيه)", "هامشك %", "أساسيك الفعلي %", "الحكم"]

def margin_hunter(stock, pidx, thin_pct=20.0, cofix=None):
    """Per-item real margin from the بياناتي stock sheet: selling happens at the
    official public price, so margin = سعر الجمهور - real unit cost (إجمالي التكلفة /
    إجمالي الكمية). أساسيك الفعلي is the base discount his cost implies vs the public
    price. Items without a public price or a cost are skipped, never guessed.
    Worst margins first. Never raises."""
    if stock is None or stock.empty or not pidx:
        return pd.DataFrame(columns=MARGIN_COLS)
    try:
        d = fix_stock_sheet(stock)
        if d.empty:
            return pd.DataFrame(columns=MARGIN_COLS)
        _cfx = cofix_map(cofix)
        _tq = pd.to_numeric(d["إجمالي الكمية"], errors="coerce")
        cost = pd.to_numeric(d["إجمالي التكلفة"], errors="coerce") / _tq.where(_tq != 0)
        rows = []
        _names = stock_display_names(d)
        for i in range(len(d)):
            c = cost.iloc[i]
            if pd.isna(c) or c <= 0:
                continue
            hit = find_public_row(_names.iloc[i], pidx)
            if not hit or not hit[0]:
                continue
            pub = float(hit[0])
            margin = pub - c
            pct = margin / pub * 100
            implied = (1 - c / pub) * 100
            if margin < 0:
                verdict = "خسارة (تكلفتك فوق سعر الجمهور) - تأكد من سعر القايمة الأول"
            elif pct < thin_pct:
                verdict = "هامش ضعيف"
            else:
                verdict = "كويس"
            _co_note = ""
            _appr = _cfx.get(_canon_fast(d["الصنف"].iloc[i])) or _cfx.get(_canon_fast(_names.iloc[i])) or _cfx.get(_canon_fast(hit[2] or ""))
            if _appr:
                _co_note = f"✅ الشركة مؤكدة منك: {_appr}"
            elif hit[1] and company_conflict(d["الشركة"].iloc[i], hit[1]):
                _co_note = f"⚠ الشركة في شيتك تختلف عن القاموس: {company_ar(hit[1])}"
            rows.append({"الصنف": hit[2] or str(d["الصنف"].iloc[i]).strip(),
                         "الشركة": d["الشركة"].iloc[i],
                         "الشركة (القاموس)": company_ar(hit[1]),
                         "ملاحظة الشركة": _co_note,
                         "سعر الجمهور": round(pub, 2),
                         "تكلفتك الحقيقية": round(c, 2),
                         "هامشك (جنيه)": round(margin, 2),
                         "هامشك %": round(pct, 1),
                         "أساسيك الفعلي %": round(implied, 1),
                         "الحكم": verdict})
        out = pd.DataFrame(rows, columns=MARGIN_COLS)
        if len(out):
            out = out.sort_values("هامشك %", ascending=True).reset_index(drop=True)
        return out
    except Exception:
        return pd.DataFrame(columns=MARGIN_COLS)


_INVOICE_SKIP_RE = re.compile(
    r"إجمالي|اجمالى|اجمالي|صافي|الخصم|الضريبة|ض\.ق\.م|ضريبة|المدفوع|النقدي|آجل|اجل|توقيع|العميل|"
    r"فاتورة|تاريخ|رقم الحساب|رصيد|مبلغ|الشحن|خدمة|total|vat|invoice|cash", re.I)
_NUM_TOKEN_RE = re.compile(r"\d[\d.,]*")


_UNIT_AFTER_RE = re.compile(
    r"^\s*(?:قرص|اقراص|أقراص|قرصين|اقماع|أقماع|قمع|كبسول|كبسولة|كبسولات|شراب|نقط|مل|مجم|جم|"
    r"وحدة|علبة|زجاجة|امبول|أمبول|امبولات|فيال|كيس|اكياس|أكياس|لبوس|كريم|مرهم|جل|"
    r"tab|tabs|cap|caps|ml|mg|amp|amps|vial)\b", re.I)


def parse_invoice_text(text):
    """Invoice lines from OCR/plain text: [{item, price, qty}]. Egyptian invoice rows are
    usually: name ... qty unit total (or name ... qty unit, or name ... price). The unit
    price is picked, never the line total: when the last three numbers satisfy
    qty*unit ~= total the middle one is the price; with two numbers the last is the price
    (the first is qty when it is a plausible integer count); one number is the price.
    Numbers followed by a unit word (24 قرص, 50 مجم) belong to the item name, not the
    columns. Header/footer/total lines and rows with no readable name are skipped - a
    skipped line is safer than a guessed price."""
    rows = []
    for raw in str(text).splitlines():
        line = norm(raw)
        if len(line) < 4 or _INVOICE_SKIP_RE.search(line):
            continue
        toks = [(m.start(), m.end(), num(m.group()))
                for m in _NUM_TOKEN_RE.finditer(line)]
        toks = [x for x in toks if x[2] is not None]
        if not toks:
            continue
        # trailing column cluster: walk left while only spaces/punct separate the
        # numbers and the previous number is not a name number (24 قرص, 50 مجم)
        k = len(toks) - 1
        while k > 0:
            prev_end, cur_start = toks[k - 1][1], toks[k][0]
            if re.search(r"[ء-يA-Za-z]", line[prev_end:cur_start]):
                break
            if _UNIT_AFTER_RE.match(line[prev_end:]):
                break
            k -= 1
        cluster = toks[k:]
        vals = [v for _, _, v in cluster]
        qty, name_end = None, None
        if len(vals) >= 3 and abs(vals[-3] * vals[-2] - vals[-1]) <= max(1.0, vals[-1] * 0.02):
            qty, price, name_end = vals[-3], vals[-2], cluster[-3][0]
        elif len(vals) >= 2:
            price, name_end = vals[-1], cluster[-2][0]
            q = vals[-2]
            if q == int(q) and 0 < q <= 10000:
                qty = q
        else:
            price, name_end = vals[0], cluster[0][0]
        item = line[:name_end].strip(" -–:،.*\u200e\u200f\u061c").strip()
        # leading row index (a bare number followed by Arabic letters) is not the name
        m_idx = re.match(r"^(\d{1,3})\s+(?=\D)", item)
        if m_idx:
            item = item[m_idx.end():]
        if len(item) < 2 or not re.search(r"[ء-يA-Za-z]", item):
            continue
        if not price or price <= 0:
            continue
        rows.append(dict(item=item, price=float(price),
                         qty=float(qty) if qty else None))
    return rows


def ocr_invoice_image(image_bytes, lang="ara+eng"):
    """OCR a supplier-invoice photo to text lines. Returns (rows, raw_text): rows as
    parse_invoice_text dicts and the raw OCR text so the user can eyeball the read.
    Needs pytesseract + a tesseract binary with the ara language (Streamlit: packages.txt)."""
    import io, os as _os
    import pytesseract
    from PIL import Image, ImageOps
    _texe = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "tesseract", "tesseract.exe")
    if _os.path.exists(_texe):
        pytesseract.pytesseract.tesseract_cmd = _texe
        _os.environ.setdefault("TESSDATA_PREFIX", _os.path.join(_os.path.dirname(_texe), "tessdata"))
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.grayscale(img)
    if img.width < 1400:
        img = img.resize((1400, int(img.height * 1400 / img.width)))
    cfg = "--psm 6"
    try:
        text = pytesseract.image_to_string(img, lang=lang, config=cfg)
    except Exception:
        text = pytesseract.image_to_string(img, config=cfg)
    return parse_invoice_text(text), text


# ---------- Company names: canonical Arabic display + conflict detection ----------
# Rule (user directive 27367853): a company name must never be wrong or guessed.
# We only ever DISPLAY a company that came from a real source (dictionary/public list
# = manufacturer of record; stock sheet = his own system) and we LABEL the source.
# The dictionary stores some companies as "manufacturer > originator/importer" chains;
# the first element is the actual manufacturer, the rest is never shown as the company.

_CO_CANON = {
    "eipico": "ايبيكو", "ايبيكو": "ايبيكو", "ابيكو": "ايبيكو",
    "eva pharma": "ايفا فارما", "ايفا": "ايفا فارما", "افا": "ايفا فارما",
    "amoun": "امون", "امون": "امون",
    "global napi pharmaceuticals": "جلوبال نابي", "global napi": "جلوبال نابي", "جلوبال": "جلوبال نابي",
    "marcyrl co.": "ماركيرل", "marcyrl": "ماركيرل", "ماركيرل": "ماركيرل",
    "multi-apex": "مالتي ابيكس", "مالتي ابيكس": "مالتي ابيكس",
    "mash premiere": "ماش بريميير", "ماش": "ماش بريميير",
    "mup": "ميديكال يونيون (mup)", "medical union pharmaceuticals": "ميديكال يونيون (mup)",
    "macro group pharmaceuticals": "ماكرو جروب", "macro group": "ماكرو جروب", "ماكروانترناشونال": "ماكرو جروب", "ماكرو": "ماكرو جروب",
    "chemipharm": "كيما فارم", "كيما فارم": "كيما فارم",
    "delta pharma": "الدلتا فارما", "الدلتا فارم": "الدلتا فارما", "الدلتا": "الدلتا فارما",
    "pharco": "فاركو", "فاركو": "فاركو",
    "pharopharma": "الفرعونية فارما", "الفرعونيه": "الفرعونية فارما",
    "october pharma": "اكتوبر فارما", "اكتوبر فارم": "اكتوبر فارما", "اكتوبر": "اكتوبر فارما",
    "mina pharm": "مينا فارم", "مينا فارم": "مينا فارم",
    "andalous pharma": "الاندلس فارما", "الاندلس": "الاندلس فارما",
    "orchidia pharmaceutical industries": "اوركيديا", "orchidia": "اوركيديا", "اوركدي": "اوركيديا",
    "novartis": "نوفارتس", "نوفارتيس": "نوفارتس",
    "mepaco": "ميباكو", "ميباكو": "ميباكو",
    "hikma pharma": "الحكمة فارما", "hikma": "الحكمة فارما", "الحكمه فارم": "الحكمة فارما", "الحكمه": "الحكمة فارما",
    "kahira": "القاهرة للادوية", "القاهره": "القاهرة للادوية",
    "adwia": "ادويا", "ادوي": "ادويا",
    "al esraa pharmaceutical optima": "الاسراء", "الاسرا": "الاسراء",
    "rameda": "راميدا", "راميدا": "راميدا",
    "sanofi": "سانوفي (افنتيس سابقا)", "سانوفي": "سانوفي (افنتيس سابقا)", "افنتيس": "سانوفي (افنتيس سابقا)", "aventis": "سانوفي (افنتيس سابقا)",
    "egpi": "المجموعة المصرية", "المجموعه المصريه": "المجموعة المصرية",
    "sigma": "سيجما", "سيجما": "سيجما",
    "sedico": "سيديكو", "سيديكو": "سيديكو",
    "alexandria": "الاسكندرية للادوية", "الاسكندريه": "الاسكندرية للادوية",
    "amriya": "العامرية للادوية", "العامريه": "العامرية للادوية",
    "cid": "سيد (cid)", "سيد": "سيد (cid)",
    "borg": "بورج", "بورج": "بورج",
    "unipharma co.": "يوني فارما", "unipharma": "يوني فارما", "يوني فارما": "يوني فارما",
    "zeta pharm": "زيتا فارم", "زيتا فارم": "زيتا فارم",
    "future pharmaceutical industries (fpi)": "اف بي اي (المستقبل)", "fpi": "اف بي اي (المستقبل)", "اف بي اي": "اف بي اي (المستقبل)",
    "medizen": "ميدزين", "medizen pharmaceutical industries": "ميدزين", "ميدزين": "ميدزين",
    "organopharma": "اورجانو فارما", "اورجانو فارم": "اورجانو فارما",
    "arab drug company (adco)": "العربية للادوية (adco)", "adco": "العربية للادوية (adco)", "العربيه": "العربية للادوية (adco)",
    "park view": "بارك فيو", "بارك في": "بارك فيو",
    "globe international pharmaceuticals": "جلوب انترناشيونال", "جلوب انترناشيونال": "جلوب انترناشيونال",
    "sanofi winthrop": "سانوفي (افنتيس سابقا)", "sanofi aventis": "سانوفي (افنتيس سابقا)",
    "apex pharma": "ابيكس فارما", "ابيكس": "ابيكس فارما",
    "global nabi pharmaceuticals": "جلوبال نابي",
    "gsk": "جلاكسو", "glaxosmithkline": "جلاكسو", "glaxo": "جلاكسو", "جلاكسو": "جلاكسو",
    "memphis": "ممفيس", "ممفيس": "ممفيس",
    "acdima": "اكديما", "acdima international trading": "اكديما", "اكديما": "اكديما", "اكديما انترناشيونال": "اكديما",
    "biomed": "بيوميد", "بيوميد": "بيوميد",
    "nile": "النيل فارما", "nile pharma": "النيل فارما", "النيل": "النيل فارما",
    "abbott": "ابوت", "abbott laboratories": "ابوت",
    "western": "ويسترن", "ويسترن": "ويسترن",
}
_CO_JUNK = {"", "company", "nan", "none", "-"}

def _co_norm(s):
    import re as _re, unicodedata as _ud
    s = ''.join(c for c in _ud.normalize('NFKD', str(s)) if not _ud.combining(c))
    s = _re.sub(r'[^\w\s؀-ۿ]', ' ', s)
    s = _re.sub(r'\s+', ' ', s).strip().lower()
    for a, b in [('أ','ا'),('إ','ا'),('آ','ا'),('ة','ه'),('ى','ي')]:
        s = s.replace(a, b)
    for _pre in ("شركه ", "شركة ", "مصنع ", "معامل "):
        if s.startswith(_pre):
            s = s[len(_pre):]
            break
    return s

def _co_lookup(s):
    n = _co_norm(s)
    if n in _CO_JUNK:
        return None
    if n in _CO_CANON:
        return _CO_CANON[n]
    # try progressive trimming for mojibake-truncated Arabic (e.g. "العامري�" loses its tail)
    words = n.split()
    while words:
        cand = ' '.join(words)
        if cand in _CO_CANON:
            return _CO_CANON[cand]
        # prefix match against alias keys (both directions, min 4 chars)
        hits = [v for k, v in _CO_CANON.items() if len(cand) >= 5 and (k.startswith(cand) or cand.startswith(k))]
        if len(set(hits)) == 1:
            return hits[0]
        words = words[:-1]
    return None

def _co_sides(raw):
    """A dict company field can be a 'a > b' chain (direction not guaranteed: sometimes
    manufacturer > originator, sometimes marketer > manufacturer). Returns all usable
    sides; we never pick one side and claim it is the manufacturer."""
    s = str(raw or "").strip()
    if _co_norm(s) in _CO_JUNK:
        return []
    return [p.strip() for p in s.split(">") if _co_norm(p) not in _CO_JUNK]

def company_manufacturer(raw):
    """Single-name company fields only: the name. Chained fields return '' because
    which side manufactures is not reliably encoded."""
    sides = _co_sides(raw)
    return sides[0] if len(sides) == 1 else ""

def company_ar(raw):
    """Canonical Arabic display for a company string from any source, or the cleaned
    raw string when we have no verified alias, or '' when the source has nothing usable.
    Chains display every side (' / ' joined) without claiming which one manufactures.
    Never invents a value."""
    sides = _co_sides(raw)
    if not sides:
        return ""
    return " / ".join(_co_lookup(s) or s for s in sides)

def company_conflict(co_a, co_b):
    """True only when BOTH sides resolve to canonical aliases and share NONE.
    Unknown on either side, or a match on any chain side = no conflict (fail-closed)."""
    sa = {_co_lookup(x) for x in _co_sides(co_a)} - {None}
    sb = {_co_lookup(x) for x in _co_sides(co_b)} - {None}
    return bool(sa and sb and sa.isdisjoint(sb))


def offer_cycle_notes(history):
    """canon item -> short honest note about its recorded price behavior in his own
    offers history: consecutive-offer changes per item (any supplier), counted as
    rises/falls. A description of what already happened, never a forecast. Never raises."""
    out = {}
    try:
        if history is None or history.empty:
            return out
        need = {"الصنف", "الصافي", "التاريخ"}
        if not need.issubset(set(history.columns)):
            return out
        h = history.copy()
        h["_d"] = pd.to_datetime(h["التاريخ"], errors="coerce")
        h["_v"] = pd.to_numeric(h["الصافي"], errors="coerce")
        for name, g in h.groupby("الصنف"):
            g = g.sort_values("_d", na_position="first", kind="stable")["_v"].dropna()
            if len(g) < 2:
                continue
            dv = g.pct_change().dropna() * 100
            dv = dv[dv != 0]
            if dv.empty:
                continue
            up, dn = int((dv > 0).sum()), int((dv < 0).sum())
            k = _canon_fast(name)
            if not k:
                continue
            if up and dn:
                out[k] = "🔁 سعره بيتحرك (صعود ونزول في سجلك)"
            elif up >= 2:
                out[k] = f"⬆ زاد {up} مرات في سجلك"
            elif up == 1:
                out[k] = "⬆ زاد مرة في سجلك"
            elif dn >= 2:
                out[k] = f"⬇ نزل {dn} مرات في سجلك"
            else:
                out[k] = "⬇ نزل مرة في سجلك"
    except Exception:
        pass
    return out


def expiry_days_map(batches):
    """canon item -> min days to expiry from a تشغيلات/باتشات sheet. Never raises."""
    out = {}
    try:
        if batches is None or batches.empty or "الصنف" not in batches.columns:
            return out
        if "تاريخ انتهاء الصلاحية" not in batches.columns:
            return out
        d = pd.to_datetime(batches["تاريخ انتهاء الصلاحية"], errors="coerce")
        days = (d - pd.Timestamp.now()).dt.days
        for name, dy in zip(batches["الصنف"], days):
            if pd.isna(dy):
                continue
            k = _canon_fast(name)
            if k:
                out[k] = min(out.get(k, 10 ** 9), int(dy))
    except Exception:
        pass
    return out


def smart_priority(so, days_left=None, trend=None, exp_days=None):
    """Add 🎯 أولوية (0-100) + 🧠 ليه الأولوية to a suggested-order df, sorted by the
    score. Combines only signals already computed from his own data: days of stock
    left, recorded price direction, nearest expiry, quota cap. Reasons stay
    descriptive (what the numbers say), never stockpiling advice. Never raises."""
    if so is None or so.empty:
        return so
    d = so.copy()
    days_left, trend, exp_days = days_left or {}, trend or {}, exp_days or {}
    scores, whys = [], []
    for _, r in d.iterrows():
        k = _canon_fast(r.get("الصنف", ""))
        s, why = 30, []
        left = days_left.get(k)
        try:
            if left is not None and left == left:
                if left <= 7:
                    s += 35; why.append(f"المخزون يكفي {int(left)} يوم بس")
                elif left <= 14:
                    s += 25; why.append(f"المخزون يكفي حوالي {int(left)} يوم")
                elif left <= 30:
                    s += 10
        except Exception:
            pass
        t = trend.get(k, "")
        if t == "⬆ زاد":
            s += 20; why.append("سعره زاد في آخر عروضك")
        elif t == "⬇ نزل":
            s -= 5; why.append("سعره نزل في آخر عروضك")
        ed = exp_days.get(k)
        try:
            if ed is not None and ed == ed and ed <= 90:
                s -= 20; why.append(f"صلاحيته قريبة ({int(ed)} يوم)")
        except Exception:
            pass
        try:
            q = pd.to_numeric(r.get("رصيد الكوته"), errors="coerce")
            sq = pd.to_numeric(r.get("الكمية المقترحة"), errors="coerce")
            if pd.notna(q) and q > 0 and pd.notna(sq) and sq >= q:
                s += 10; why.append("الكوته محدودة - الطلب مقفول على رصيدها")
        except Exception:
            pass
        scores.append(max(0, min(100, int(s))))
        whys.append("، ".join(why) if why else "تحت حده الأدنى")
    d["🎯 أولوية"] = scores
    d["🧠 ليه الأولوية"] = whys
    return d.sort_values("🎯 أولوية", ascending=False).reset_index(drop=True)
