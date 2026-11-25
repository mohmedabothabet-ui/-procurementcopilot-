import re, io, difflib
import pandas as pd

AR = str.maketrans("٠١٢٣٤٥٦٧٨٩٫٬", "0123456789.,")
def norm(s): return str(s).translate(AR).strip()
def num(s):
    m = re.search(r"\d+(?:[.,]\d+)?", norm(s))
    return float(m.group().replace(",", ".")) if m else None

import datetime as dt
def parse_exp(s):
    """returns first-of-month-end date or None. Accepts MM/YYYY, YYYY-MM(-DD), DD/MM/YYYY, Excel dates."""
    if s is None or (isinstance(s, float) and pd.isna(s)): return None
    if isinstance(s, (pd.Timestamp, dt.datetime, dt.date)): return pd.Timestamp(s).date()
    t = norm(s)
    m = re.search(r"(\d{1,2})[/\-.](\d{4})\b", t)
    if m and 1 <= int(m.group(1)) <= 12: return dt.date(int(m.group(2)), int(m.group(1)), 28)
    m = re.search(r"(\d{4})[/\-.](\d{1,2})(?:[/\-.](\d{1,2}))?", t)
    if m and 1 <= int(m.group(2)) <= 12: return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3) or 28))
    m = re.search(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})", t)
    if m and 1 <= int(m.group(2)) <= 12: return dt.date(int(m.group(3)), int(m.group(2)), min(int(m.group(1)), 28))
    return None

def parse_excel(f, supplier):
    raw = pd.read_excel(f, header=None)
    hdr = next((i for i in range(min(15, len(raw))) if any(
        w in " ".join(map(str, raw.iloc[i].dropna())) for w in ["صنف", "سعر"])), 0)
    df = raw.iloc[hdr + 1:].copy(); df.columns = [str(c) for c in raw.iloc[hdr]]
    def col(*ws):
        return next((c for c in df.columns if any(w in c for w in ws)), None)
    ci, cp, cd, cm = col("صنف", "اسم"), col("سعر"), col("خصم"), col("حد", "كمية")
    ce, cb = col("صلاحية", "انتهاء", "expiry"), col("تشغيلة", "باتش", "batch")
    rows = []
    for _, r in df.iterrows():
        p = num(r[cp]) if cp else None
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
                def ix(*ws): return next((i for i, x in enumerate(h) if any(w in x for w in ws)), None)
                i_i, i_p, i_d, i_m = ix("صنف", "اسم"), ix("سعر"), ix("خصم"), ix("حد", "كمية")
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
        item = re.split(r"[-–:،]|\d", line)[0].strip()
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

def compare(offers, stock, cover_days=45, min_months=6, today=None):
    today = today or dt.date.today()
    stock = fix_stock(stock)
    st = {str(r["item"]).strip(): r for _, r in stock.iterrows()}
    out, unmatched = [], []
    for o in offers:
        k = difflib.get_close_matches(o["item"], list(st), n=1, cutoff=0.5)
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
    if style not in STYLES: style = "ودي"
    reasons.append(f"الأسلوب: {style}")
    tgt = None
    cheaper = gap is not None and gap > 1
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
