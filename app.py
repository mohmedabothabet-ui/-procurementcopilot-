import streamlit as st, pandas as pd, io
from core import *
st.set_page_config(page_title="مساعد المشتريات", layout="wide")
st.markdown("<style>body,.stApp{direction:rtl;text-align:right}</style>", unsafe_allow_html=True)
st.title("مساعد المشتريات - نموذج تجريبي")
st.caption("الملفات بتتعالج في الذاكرة بس ومبتتخزنش. استخدم بيانات تجريبية لحد ما تتأكد.")
files = st.file_uploader("عروض الموردين (إكسيل / PDF / نص واتس)", accept_multiple_files=True, type=["xlsx", "pdf", "txt"])
stockf = st.file_uploader("المخزون (أعمدة: صنف ومخزون ومبيعات شهرية، بأي اسم أو ترتيب)", type=["xlsx"])
days = st.number_input("أيام التغطية", 15, 120, 45)
months = st.number_input("أقل مدة صلاحية متبقية مقبولة (شهر)", 0, 36, 6)

FIELDS_AR = {"item": "الصنف", "stock": "المخزون / الكمية", "monthly_sales": "مبيعات الشهر",
             "expiry": "تاريخ الصلاحية", "cost": "تكلفة الوحدة"}


def map_excel_ui(df, fields, keyp, pre=None):
    """Auto-recognize columns; if any required field is unrecognized, show Arabic
    selectboxes so the user maps them by hand. Returns the renamed df or None."""
    g = pre if pre is not None else guess_columns(list(df.columns), fields)
    missing = [f for f in fields if f not in g]
    if not missing:
        return df.rename(columns={v: k for k, v in g.items()})
    st.warning("مش قادر أتعرف تلقائيًا على: " + "، ".join(FIELDS_AR[f] for f in missing) +
        ". اختار الأعمدة بنفسك من القوائم دي:")
    if any(str(c).startswith("Unnamed") for c in df.columns):
        st.info("الأعمدة ظاهرة بأسماء زي Unnamed: غالبًا الملف مفيهوش صف عناوين في أول سطر، أو العناوين مش في السطر الأول.")
    mapping = {}
    cols = list(df.columns)
    for f in fields:
        opts = ["—"] + cols
        idx = cols.index(g[f]) + 1 if f in g else 0
        ch = st.selectbox("أي عمود فيه: " + FIELDS_AR[f], opts, index=idx, key=f"{keyp}_{f}")
        if ch != "—": mapping[f] = ch
    if len(mapping) < len(fields):
        return None
    return df.rename(columns={v: k for k, v in mapping.items()})

stock_df = None
if stockf:
    try:
        raw_df, pre_map, sheet, nsheets = read_excel_smart(stockf, ["item", "stock", "monthly_sales"])
        if nsheets > 1: st.caption(f"الملف فيه {nsheets} sheets، اشتغلت على: {sheet}")
        stock_df = map_excel_ui(raw_df, ["item", "stock", "monthly_sales"], "map_stock", pre_map)
    except Exception as e:
        st.error(str(e))
if stock_df is not None:
    try:
        st.subheader("تنبيه إعادة الطلب")
        c1, c2 = st.columns(2)
        lead = c1.number_input("مدة توريد المورد (يوم)", 1, 60, 7)
        safety = c2.number_input("هامش أمان (يوم)", 0, 30, 7)
        ra = reorder_alert(stock_df, lead, safety, days)
        st.dataframe(ra, use_container_width=True)
        n = int(ra["الحالة"].str.startswith("عاجل").sum())
        if n: st.error(f"{n} صنف لازم يتطلب النهارده")
        with st.expander("رسالة طلب سعر جاهزة"):
            sup = st.text_input("اسم المورد (اختياري)")
            buyer = st.text_input("اسمك / شركتك (اختياري)")
            rb = st.text_input("الرد قبل (اختياري، مثلا: الخميس)")
            msg = build_request_message(ra, sup, buyer, rb, True, months)
            if msg:
                st.text_area("انسخ الرسالة وابعتها للموردين", msg, height=260)
                import urllib.parse
                st.link_button("افتح واتساب بالرسالة", "https://wa.me/?text=" + urllib.parse.quote(msg))
            else:
                st.info("مفيش أصناف محتاجة طلب دلوقتي.")
    except Exception as e:
        st.error(str(e))
if files and stock_df is not None:
    offers = []
    for f in files:
        base = f.name.rsplit(".", 1)[0]
        guess = guess_supplier_name(f, base) if f.name.endswith("xlsx") else base
        sup = st.text_input(f"اسم المورد (ملف: {f.name})", value=guess, key=f"sup_{f.name}")
        sup = sup.strip() or base
        if f.name.endswith("xlsx"): offers += parse_excel(f, sup)
        elif f.name.endswith("pdf"): offers += parse_pdf(f, sup)
        else: offers += parse_whatsapp(f.read().decode("utf-8", "ignore"), sup)
    st.write(f"تم قراءة {len(offers)} عرض")
    if not offers:
        st.error("ما قدرتش أقرا أي عروض من الملفات. اتأكد إن فيها أعمدة صنف وسعر.")
        st.stop()
    linkf = st.file_uploader("ملف الربط من المرة اللي فاتت (روابط.xlsx، سيبه فاضي أول مرة)", type=["xlsx"], key="linkf")
    if linkf is not None and st.session_state.get("links_loaded") != (linkf.name, linkf.size):
        try:
            loaded = df_to_links(pd.read_excel(linkf))
            st.session_state["manual_map"] = {**loaded, **st.session_state.get("manual_map", {})}
            st.session_state["links_loaded"] = (linkf.name, linkf.size)
            if loaded: st.success(f"اتحمّل {len(loaded)} ربط من الملف.")
        except Exception as e:
            st.error("ملف الربط مش مفهوم: " + str(e))
    try:
        allo, cmp_, un = compare(offers, stock_df, days, months, manual=st.session_state.get("manual_map"))
    except Exception as e:
        st.error(str(e)); st.stop()
    if len(un):
        st.warning("أصناف مش متطابقة مع المخزون — غالبًا الاسم مكتوب بشكل مختلف (عربي/إنجليزي). اربطها بنفسك من تحت أو سيبها.")
        st.dataframe(pd.DataFrame(un))
        fx = fix_stock(stock_df)
        stock_names = [str(x).strip() for x in fx["item"]]
        with st.expander("ربط أصناف العرض بالمخزون", expanded=True):
            st.caption("اختار لكل صنف في العرض اسمه في ملف المخزون، وبعدين دوس «طبّق الربط». حمّل ملف الربط تحت عشان يشتغل لوحده المرة الجاية.")
            new_map = {}
            for _, r in pd.DataFrame(un).iterrows():
                opts = ["من غير ربط"] + stock_names
                sug = suggest_match(r["item"], stock_names)
                idx = stock_names.index(sug) + 1 if sug in stock_names else 0
                ch = st.selectbox(f"«{r['item']}» (عرض {r['supplier']})", opts, index=idx, key=f"lnk_{r['item']}_{r['supplier']}")
                if ch != "من غير ربط": new_map[r["item"]] = ch
            if st.button("طبّق الربط"):
                st.session_state["manual_map"] = {**st.session_state.get("manual_map", {}), **new_map}
                st.rerun()
    if cmp_.empty:
        st.error("مفيش صنف من العروض اتطابق مع ملف المخزون. اتأكد إن أسماء الأصناف متشابهة، أو اربطها يدوي من القايمة اللي فوق.")
        st.stop()
    st.subheader("المقارنة"); st.dataframe(cmp_, use_container_width=True)
    st.caption("الجدول أوسع من الشاشة: اسحبه يمين وشمال عشان تشوف باقي الأعمدة.")
    allo_ar = offers_display(allo)
    st.subheader("كل العروض"); st.dataframe(allo_ar, use_container_width=True)
    st.caption("الجدول أوسع من الشاشة: اسحبه يمين وشمال عشان تشوف باقي الأعمدة.")
    b = io.BytesIO()
    with pd.ExcelWriter(b, engine="openpyxl") as w:
        cmp_.to_excel(w, sheet_name="comparison", index=False)
        allo_ar.to_excel(w, sheet_name="offers", index=False)
    st.download_button("حمّل النتيجة إكسيل", b.getvalue(), "comparison.xlsx")
    mm = st.session_state.get("manual_map") or {}
    if mm:
        lb = io.BytesIO()
        with pd.ExcelWriter(lb, engine="openpyxl") as w:
            links_to_df(mm).to_excel(w, sheet_name="links", index=False)
        st.download_button(f"حمّل ملف الربط ({len(mm)} صنف) وارفعه المرة الجاية", lb.getvalue(), "روابط.xlsx")
    orders = build_order_messages(cmp_)
    if orders:
        with st.expander("رسائل الطلب النهائية لكل مورد (مسودة، راجعها وابعتها بنفسك)", expanded=True):
            obuyer = st.text_input("اسمك / اسم الصيدلية (بيظهر في التوقيع، اختياري)", key="obuyer")
            for od in build_order_messages(cmp_, obuyer.strip()):
                st.markdown(f"**طلب لـ {od['supplier']}** — {od['items']} صنف، إجمالي {od['total']:,.2f} جنيه")
                st.text_area("المسودة", od["message"], height=200, key=f"ord_{od['supplier']}")
                import urllib.parse
                st.link_button(f"افتح واتساب بطلب {od['supplier']}", "https://wa.me/?text=" + urllib.parse.quote(od["message"]))


st.divider()
st.subheader("مساعد التفاوض (مسودة بس، مش بيبعت حاجة)")
rep = st.text_area("الصق رد المورد", placeholder="سرنجة 5مل - 110 جنيه خصم 3% أقل كمية 100", key="rep")
c1, c2, c3 = st.columns(3)
comp = c1.number_input("أقل سعر عرض تاني بعد الخصم (0 = مفيش)", 0.0, 1000000.0, 0.0)
dl = c2.number_input("أيام المخزون المتبقية (0 = مش معروف)", 0.0, 365.0, 0.0)
ld = c3.number_input("مدة التوريد (يوم)", 1, 60, 7, key="ld2")
sty = st.selectbox("الأسلوب", ["تلقائي", "ودي", "حازم", "التزام", "سريع"], format_func=lambda x: {"تلقائي":"تلقائي (حسب الموقف)","ودي":"ودي (علاقة)","حازم":"حازم ومباشر","التزام":"التزام بالكمية/تكرار","سريع":"قرار سريع"}[x])
c4, c5 = st.columns(2)
cp = c4.number_input("السعر المتفق عليه لإعادة التأكيد (اختياري، 0 = مفيش)", 0.0, 1000000.0, 0.0)
cd = c5.number_input("الخصم المتفق عليه % (اختياري، 0 = مفيش)", 0.0, 99.0, 0.0)
if st.button("جهّز المسودة") and rep.strip():
    d, why = draft_counter(rep, comp or None, dl or None, ld, style=sty, confirm_price=cp or None, confirm_discount=cd or None)
    if d:
        st.text_area("المسودة (راجعها وابعتها بنفسك)", d, height=200)
    st.caption(" | ".join(why))


st.divider()
st.subheader("تقرير قيمة الأصناف قريبة الانتهاء")
expf = st.file_uploader("ملف الصلاحيات (أعمدة: صنف، كمية، تكلفة، صلاحية)", type=["xlsx"], key="expf")
use_sample = st.checkbox("جرّب ببيانات تجريبية (من غير ملف)", key="use_sample")
em = st.number_input("أظهر اللي صلاحيته تنتهي خلال (شهر)", 1, 24, 3, key="em")
if expf or use_sample:
    try:
        df = sample_expiry_stock()
        if expf:
            raw_df, pre_map, sheet, nsheets = read_excel_smart(expf, ["item", "stock", "cost", "expiry"])
            if nsheets > 1: st.caption(f"الملف فيه {nsheets} sheets، اشتغلت على: {sheet}")
            df = map_excel_ui(raw_df, ["item", "stock", "cost", "expiry"], "map_exp", pre_map)
        if df is None:
            st.stop()
        er = expiry_risk(df, em)
        if er.empty:
            st.success("مفيش أصناف قريبة الانتهاء خلال المدة دي.")
        else:
            risk = er[er["القيمة المعرضة للخسارة"] > 0]
            total = float(risk["القيمة المعرضة للخسارة"].sum())
            c1, c2, c3 = st.columns(3)
            c1.metric("إجمالي القيمة المعرضة للخسارة", f"{total:,.0f} جنيه")
            c2.metric("عدد الأصناف المتأثرة", len(risk))
            soon = risk["الأشهر المتبقية"].min()
            c3.metric("أقرب انتهاء", ("في صنف منتهي" if soon < 0 else f"{soon:.1f} شهر") if soon == soon and soon is not None else "-")
            expired = int((er["الحالة"] == "منتهي").sum())
            if expired: st.error(f"{expired} صنف منتهي فعلًا: اعزله فورًا من المخزون.")
            st.dataframe(er, use_container_width=True)
            st.caption("القيمة = الكمية × تكلفة الوحدة. بيانات تجريبية لحد ما تتأكد من شغل الملفات الحقيقية.")
    except Exception as e:
        st.error(str(e))


st.divider()
st.subheader("ذاكرة المورد من شات واتس")
st.caption("الصق الشات والتطبيق يطلّع لكل صنف: آخر سعر وخصم، وأفضل سعر شفناه قبل كده. مفيش حاجة بتتخزن.")
supn = st.text_input("اسم المورد", key="sup_mem")
chat = st.text_area("الصق شات واتس مع المورد", key="chat_mem", height=160,
    placeholder="12/8/2026, 10:15 ص - الحاج محمود: سرنجة 5مل - 110 جنيه خصم 3%")
use_chat_sample = st.checkbox("جرّب بشات تجريبي (من غير لصق)", key="use_chat_sample")
if st.button("لخّص الشات", key="btn_mem"):
    text = chat.strip() or (SAMPLE_CHAT if use_chat_sample else "")
    if not text:
        st.info("الصق الشات الأول، أو فعّل الشات التجريبي.")
    else:
        rows = parse_whatsapp_dated(text, supn.strip() or "المورد")
        if not rows:
            st.error("ما قدرتش أقرا أي أسعار من الشات. لازم كل سطر فيه سعر يكون معاه كلمة جنيه.")
        else:
            mem = supplier_memory(rows)
            st.write(f"اتقرأ {len(rows)} عرض سعر من الشات.")
            st.dataframe(mem, use_container_width=True)
            st.caption("لو آخر عرض أعلى من أفضل سعر شفناه، ده معناه إن عندك نقطة تفاوض قوية.")
            mb = io.BytesIO()
            with pd.ExcelWriter(mb, engine="openpyxl") as w:
                mem.to_excel(w, sheet_name="memory", index=False)
            st.download_button("حمّل الذاكرة إكسيل", mb.getvalue(), "supplier_memory.xlsx")


st.divider()
st.subheader("سجل الأسعار التاريخي")
st.caption("السجل ملف بيتحفظ عندك إنت، مش في التطبيق: حمّله وخزّنه، وارفعه كل مرة ترجع تضيف شات جديد.")
histf = st.file_uploader("ملف السجل من المرة اللي فاتت (price_history.xlsx، سيبه فاضي أول مرة)", type=["xlsx"], key="histf")
suph = st.text_input("اسم المورد", key="sup_hist")
chath = st.text_area("الصق شات واتس جديد للمورد", key="chat_hist", height=140,
    placeholder="26/11/2026, 10:00 ص - الحاج محمود: سرنجة 5مل - 113 جنيه خصم 6%")
use_hist_sample = st.checkbox("جرّب بشات تجريبي (من غير لصق)", key="use_hist_sample")
if st.button("حدّث السجل", key="btn_hist"):
    text = chath.strip() or (SAMPLE_CHAT if use_hist_sample else "")
    if not text and not histf:
        st.info("الصق شات جديد، أو فعّل الشات التجريبي، أو ارفع ملف السجل.")
    else:
        try:
            hist = pd.read_excel(histf) if histf else None
            rows = parse_whatsapp_dated(text, suph.strip() or "المورد") if text else []
            if text and not rows:
                st.error("ما قدرتش أقرا أي أسعار من الشات. لازم كل سطر فيه سعر يكون معاه كلمة جنيه.")
            else:
                before = len(hist) if hist is not None else 0
                merged = update_price_history(hist, rows)
                added = len(merged) - before
                st.success(f"السجل فيه دلوقتي {len(merged)} عرض" + (f" (اتضاف {added} جديد)." if added else " (مفيش عروض جديدة، كلها موجودة قبل كده)."))
                st.markdown("**ملخص لكل صنف**")
                st.dataframe(price_history_summary(merged), use_container_width=True)
                st.markdown("**كل العروض**")
                st.dataframe(merged, use_container_width=True)
                hb = io.BytesIO()
                with pd.ExcelWriter(hb, engine="openpyxl") as w:
                    merged.to_excel(w, index=False)
                st.download_button("حمّل السجل المحدّث (خزّنه وارفعه المرة الجاية)", hb.getvalue(), "price_history.xlsx")
        except Exception as e:
            st.error(str(e))
