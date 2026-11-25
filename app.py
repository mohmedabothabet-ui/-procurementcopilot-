import streamlit as st, pandas as pd, io
from core import *
st.set_page_config(page_title="مساعد المشتريات", layout="wide")
st.markdown("<style>body,.stApp{direction:rtl;text-align:right}</style>", unsafe_allow_html=True)
st.title("مساعد المشتريات - نموذج تجريبي")
st.caption("الملفات بتتعالج في الذاكرة بس ومبتتخزنش. استخدم بيانات تجريبية لحد ما تتأكد.")
files = st.file_uploader("عروض الموردين (إكسيل / PDF / نص واتس)", accept_multiple_files=True, type=["xlsx", "pdf", "txt"])
stockf = st.file_uploader("المخزون (أعمدة: item, stock, monthly_sales)", type=["xlsx"])
days = st.number_input("أيام التغطية", 15, 120, 45)
months = st.number_input("أقل مدة صلاحية متبقية مقبولة (شهر)", 0, 36, 6)
if stockf:
    try:
        st.subheader("تنبيه إعادة الطلب")
        c1, c2 = st.columns(2)
        lead = c1.number_input("مدة توريد المورد (يوم)", 1, 60, 7)
        safety = c2.number_input("هامش أمان (يوم)", 0, 30, 7)
        ra = reorder_alert(pd.read_excel(stockf), lead, safety, days)
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
        stockf.seek(0)
    except Exception as e:
        st.error(str(e))
if files and stockf:
    offers = []
    for f in files:
        sup = f.name.rsplit(".", 1)[0]
        if f.name.endswith("xlsx"): offers += parse_excel(f, sup)
        elif f.name.endswith("pdf"): offers += parse_pdf(f, sup)
        else: offers += parse_whatsapp(f.read().decode("utf-8", "ignore"), sup)
    st.write(f"تم قراءة {len(offers)} عرض")
    if not offers:
        st.error("ما قدرتش أقرا أي عروض من الملفات. اتأكد إن فيها أعمدة صنف وسعر.")
        st.stop()
    try:
        stock = pd.read_excel(stockf)
        allo, cmp_, un = compare(offers, stock, days, months)
    except Exception as e:
        st.error(str(e)); st.stop()
    if len(un): st.warning("أصناف مش متطابقة مع المخزون"); st.dataframe(pd.DataFrame(un))
    if cmp_.empty:
        st.error("مفيش صنف من العروض اتطابق مع ملف المخزون. اتأكد إن أسماء الأصناف متشابهة.")
        st.stop()
    st.subheader("المقارنة"); st.dataframe(cmp_, use_container_width=True)
    st.subheader("كل العروض"); st.dataframe(allo, use_container_width=True)
    b = io.BytesIO()
    with pd.ExcelWriter(b, engine="openpyxl") as w:
        cmp_.to_excel(w, sheet_name="comparison", index=False)
        allo.to_excel(w, sheet_name="offers", index=False)
    st.download_button("حمّل النتيجة إكسيل", b.getvalue(), "comparison.xlsx")


st.divider()
st.subheader("مساعد التفاوض (مسودة بس، مش بيبعت حاجة)")
rep = st.text_area("الصق رد المورد", placeholder="سرنجة 5مل - 110 جنيه خصم 3% أقل كمية 100", key="rep")
c1, c2, c3 = st.columns(3)
comp = c1.number_input("أقل سعر عرض تاني بعد الخصم (0 = مفيش)", 0.0, 1000000.0, 0.0)
dl = c2.number_input("أيام المخزون المتبقية (0 = مش معروف)", 0.0, 365.0, 0.0)
ld = c3.number_input("مدة التوريد (يوم)", 1, 60, 7, key="ld2")
sty = st.selectbox("الأسلوب", ["ودي", "حازم", "التزام", "سريع"], format_func=lambda x: {"ودي":"ودي (علاقة)","حازم":"حازم ومباشر","التزام":"التزام بالكمية/تكرار","سريع":"قرار سريع"}[x])
c4, c5 = st.columns(2)
cp = c4.number_input("السعر المتفق عليه لإعادة التأكيد (اختياري، 0 = مفيش)", 0.0, 1000000.0, 0.0)
cd = c5.number_input("الخصم المتفق عليه % (اختياري، 0 = مفيش)", 0.0, 99.0, 0.0)
if st.button("جهّز المسودة") and rep.strip():
    d, why = draft_counter(rep, comp or None, dl or None, ld, style=sty, confirm_price=cp or None, confirm_discount=cd or None)
    if d:
        st.text_area("المسودة (راجعها وابعتها بنفسك)", d, height=200)
    st.caption(" | ".join(why))
