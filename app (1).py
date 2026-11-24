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
