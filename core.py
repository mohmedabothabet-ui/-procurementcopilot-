import re, io, difflib
import pandas as pd

AR = str.maketrans("٠١٢٣٤٥٦٧٨٩٫٬", "0123456789.,")
def norm(s): return str(s).translate(AR).strip()
def num(s):
    m = re.search(r"\d+(?:[.,]\d+)?", norm(s))
    return float(m.group().replace(",", ".")) if m else None

def parse_excel(f, supplier):
    raw = pd.read_excel(f, header=None)
    hdr = next((i for i in range(min(15, len(raw))) if any(
        w in " ".join(map(str, raw.iloc[i].dropna())) for w in ["صنف", "سعر"])), 0)
    df = raw.iloc[hdr + 1:].copy(); df.columns = [str(c) for c in raw.iloc[hdr]]
    def col(*ws):
        return next((c for c in df.columns if any(w in c for w in ws)), None)
    ci, cp, cd, cm = col("صنف", "اسم"), col("سعر"), col("خصم"), col("حد", "كمية")
    rows = []
    for _, r in df.iterrows():
        p = num(r[cp]) if cp else None
        if pd.isna(r[ci]) or p is None: continue
        rows.append(dict(item=str(r[ci]).strip(), supplier=supplier, price=p,
            discount=(num(r[cd]) or 0) if cd else 0, min_qty=(num(r[cm]) or 0) if cm else 0))
    return rows

def parse_pdf(f, supplier):
    import pdfplumber
    rows = []
    with pdfplumber.open(f) as pdf:
        for pg in pdf.pages:
            for t in pg.extract_tables():
                if not t: continue
                h = [str(x or "") for x in t[0]]
                def ix(*ws): return next((i for i, x in enumerate(h) if any(w in x for w in ws)), None)
                i_i, i_p, i_d, i_m = ix("صنف", "اسم"), ix("سعر"), ix("خصم"), ix("حد", "كمية")
                for r in t[1:]:
                    if i_i is None or i_p is None: continue
                    p = num(r[i_p] or "")
                    if p is None: continue
                    rows.append(dict(item=str(r[i_i]).strip(), supplier=supplier, price=p,
                        discount=(num(r[i_d] or "") or 0) if i_d is not None else 0,
                        min_qty=(num(r[i_m] or "") or 0) if i_m is not None else 0))
    return rows

def parse_whatsapp(text, supplier):
    rows = []
    for line in text.splitlines():
        line = norm(line)
        line = re.sub(r"^\[?[\d/,: \-APM]+\]?\s*[^:]{0,30}:\s", "", line) if re.match(r"^\[?\d", line) else line
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:جنيه|ج\b|EGP)", line)
        if not m: continue
        item = re.split(r"[-–:،]|\d", line)[0].strip()
        if not item: continue
        d = re.search(r"خصم\s*(\d+(?:[.,]\d+)?)", line)
        q = re.search(r"(?:أقل كمية|اقل كمية|الحد الأدنى|الحد الادنى)\s*(\d+)", line)
        rows.append(dict(item=item, supplier=supplier, price=float(m.group(1).replace(",", ".")),
            discount=float(d.group(1).replace(",", ".")) if d else 0, min_qty=int(q.group(1)) if q else 0))
    return rows

def fix_stock(stock):
    m = {}
    for c in stock.columns:
        s = str(c).lower()
        if any(w in s for w in ["item", "صنف", "اسم", "name"]): m.setdefault("item", c)
        elif any(w in s for w in ["monthly", "sales", "مبيعات", "شهري"]): m.setdefault("monthly_sales", c)
        elif any(w in s for w in ["stock", "مخزون", "رصيد", "كمية"]): m.setdefault("stock", c)
    stock = stock.rename(columns={v: k for k, v in m.items()})
    for k in ["item", "stock", "monthly_sales"]:
        if k not in stock.columns: raise ValueError("عمود ناقص في ملف المخزون: " + k)
    return stock

def compare(offers, stock, cover_days=45):
    stock = fix_stock(stock)
    st = {str(r["item"]).strip(): r for _, r in stock.iterrows()}
    out, unmatched = [], []
    for o in offers:
        k = difflib.get_close_matches(o["item"], list(st), n=1, cutoff=0.5)
        if not k: unmatched.append(o); continue
        o = dict(o, item=k[0]); o["net"] = round(o["price"] * (1 - o["discount"] / 100), 2); out.append(o)
    df = pd.DataFrame(out)
    if df.empty: return df, pd.DataFrame(), pd.DataFrame(unmatched)
    rows = []
    for item, g in df.groupby("item"):
        g = g.sort_values("net"); best = g.iloc[0]; worst = g.iloc[-1]
        s = st[item]; need = max(0, round(s["monthly_sales"] * cover_days / 30 - s["stock"]))
        rows.append({"الصنف": item, "أرخص مورد": best.supplier, "السعر بعد الخصم": best.net,
            "أغلى سعر": worst.net, "التوفير %": round((1 - best.net / worst.net) * 100, 1) if worst.net else 0,
            "الكمية المقترحة": need, "حد أدنى عند الأرخص": best.min_qty, "التكلفة": round(need * best.net, 2),
            "تنبيه": "الكمية أقل من الحد الأدنى" if 0 < need < best.min_qty else ""})
    return df, pd.DataFrame(rows), pd.DataFrame(unmatched)
