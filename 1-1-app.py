import streamlit as st, pandas as pd, io
import importlib as _il, core as _core_mod
_il.reload(_core_mod)  # Streamlit Cloud reuses the process across pushes; reload picks up the deployed core.py every rerun.
from core import *
from core import _canon_fast
st.set_page_config(page_title="مساعد الصيدلي", page_icon="icon_32.png", layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
[data-testid="stDataFrame"]{padding-top:30px;background:transparent;border-radius:12px}

body,.stApp{direction:rtl;text-align:right;font-family:'Cairo',system-ui,-apple-system,'Segoe UI',Tahoma,sans-serif}
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],.stDeployButton,[data-testid="stHeader"]{display:none!important}
.brand{background:linear-gradient(135deg,#0d7377,#14919b);-webkit-background-clip:text;background-clip:text;color:transparent;font-size:2.1rem;font-weight:800;margin:0}
.brand-sub{color:#5a6b6b;margin-top:-4px;font-weight:600}
.block-container{padding-bottom:7rem;max-width:1100px}
h1,h2,h3{font-family:inherit!important;font-weight:800!important}
.stButton>button,.stDownloadButton>button,.stLinkButton>a{border-radius:12px!important;min-height:46px;font-weight:700!important;font-family:inherit!important;border:1.5px solid rgba(13,115,119,.35)!important;transition:all .15s ease}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:#0d7377!important;box-shadow:0 3px 12px rgba(13,115,119,.18);transform:translateY(-1px)}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#0d7377,#14919b)!important;border:none!important;color:#fff!important}
div[role="radiogroup"] label,[data-testid="stPills"] button{border-radius:999px!important}
div[role="radiogroup"] button,[data-testid="stPills"] button{min-height:42px!important;font-weight:600!important}
.stTextInput input,.stNumberInput input,.stTextArea textarea,div[data-baseweb="select"]>div{border-radius:10px!important}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px!important;border:1px solid rgba(13,115,119,.22)!important;box-shadow:0 2px 10px rgba(15,40,40,.07)}
[data-testid="stExpander"]{border-radius:12px!important;border:1px solid rgba(13,115,119,.22)!important;overflow:hidden}
[data-testid="stAlert"]{border-radius:12px!important}
[data-testid="stMetric"]{background:rgba(13,115,119,.07);border-radius:12px;padding:.6rem .9rem}
@media (max-width:640px){.block-container{padding-left:.9rem;padding-right:.9rem;padding-top:1.2rem}.brand{font-size:1.7rem}.stButton>button,.stDownloadButton>button{min-height:52px;font-size:1.02rem}}
/* ---------- v46: هوية أقوى وحركة ---------- */
@keyframes heroShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes shine{0%{transform:translateX(160%) skewX(-18deg)}100%{transform:translateX(-260%) skewX(-18deg)}}
.hero{position:relative;overflow:hidden;border-radius:18px;padding:1.5rem 1.3rem 1.3rem;background:linear-gradient(120deg,#0d7377,#14919b,#0aa06e,#0d7377);background-size:300% 300%;animation:heroShift 14s ease infinite;box-shadow:0 10px 30px rgba(13,115,119,.35);margin-bottom:1rem}
.hero::after{content:"";position:absolute;top:0;bottom:0;width:38%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.16),transparent);animation:shine 7s ease-in-out infinite;pointer-events:none}
.hero h1{color:#fff!important;font-size:2.2rem!important;font-weight:800!important;margin:0!important;text-shadow:0 2px 8px rgba(0,0,0,.18)}
.hero p{color:#eaf6f6;margin:.3rem 0 0;font-weight:600}
.hero-badge{display:inline-block;background:rgba(255,255,255,.16);color:#fff;border:1px solid rgba(255,255,255,.38);border-radius:999px;padding:.18rem .75rem;font-size:.8rem;font-weight:700;margin-bottom:.5rem}
[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stExpander"],[data-testid="stAlert"],[data-testid="stMetric"]{animation:fadeUp .45s ease both}
.pagechip{display:flex;align-items:center;gap:.6rem;border-radius:14px;padding:.55rem 1rem;font-weight:800;font-size:1.2rem;color:#fff;margin:.2rem 0 .6rem;box-shadow:0 4px 14px rgba(15,40,40,.20)}
.pagechip small{font-weight:600;font-size:.8rem;opacity:.92}
@media (prefers-reduced-motion:reduce){.hero,.hero::after,[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stExpander"],[data-testid="stAlert"],[data-testid="stMetric"]{animation:none!important}}
@media (max-width:640px){.hero{padding:1.1rem 1rem}.hero h1{font-size:1.55rem!important}}
</style>
<link rel="apple-touch-icon" href="https://raw.githubusercontent.com/mohmedabothabet-ui/-procurementcopilot-/main/icon_180.png">
<meta name="theme-color" content="#0d7377">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="مساعد الصيدلي">
""", unsafe_allow_html=True)
_bc1,_bc2 = st.columns([1,11])
with _bc1:
    try:
        import os as _os
        st.image(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "icon_180.png"), width=72)
    except Exception: pass
with _bc2:
    st.markdown('<p class="brand">مساعد الصيدلي</p><p class="brand-sub">أداة المشتريات والأسعار لصيدليتك - بياناتك على جهازك</p>', unsafe_allow_html=True)
try:
    _app_pw = str(st.secrets.get("app_password", "") or "")
except Exception:
    _app_pw = ""
if _app_pw and not st.session_state.get("gate_ok"):
    with st.form("gate_form"):
        _g = st.text_input("كلمة السر", type="password", key="gate_in")
        _ok = st.form_submit_button("دخول", use_container_width=True, type="primary")
    if _ok:
        if _g == _app_pw:
            st.session_state["gate_ok"] = True
            st.rerun()
        else:
            st.error("كلمة السر غلط. حاول تاني.")
    st.info("التطبيق ده خاص بيك. اكتب كلمة السر ودوس «دخول» علشان تكمل.")
    st.stop()
st.caption("الملفات بتتعالج في الذاكرة بس ومبتتخزنش. استخدم بيانات تجريبية لحد ما تتأكد.")
st.caption("اختار الأداة من الرئيسية — كل الأدوات مربوطة ببعضها من ملف بياناتي الواحد.")

@st.cache_data
def _load_drug_dict():
    try:
        return extend_aliases(pd.read_csv("drugs_dict.csv"))
    except Exception:
        return 0
_nd = _load_drug_dict()
if _nd: st.caption(f"الربط التلقائي شغال بقاموس {_nd:,} دواء مصري (عربي/إنجليزي). مصدر القاموس: eg-drugs — CC BY 4.0.")


FIELDS_AR = {"item": "الصنف", "stock": "المخزون / الكمية", "monthly_sales": "مبيعات الشهر",
             "expiry": "تاريخ الصلاحية", "cost": "تكلفة الوحدة"}

# ---------- v45: أوامر الجداول المكتوبة + طبقة "تفكر قبلك" + شارة الباتش/الصلاحية ----------
def table_actions(df, key, label="الجدول"):
    """شريط أوامر مكتوب فوق أي جدول: بحث، تنزيل Excel، عرض مكبّر. يرجع DataFrame بعد الفلترة."""
    import io as _io
    _c1, _c2, _c3 = st.columns([3, 1, 1])
    with _c1:
        _q = st.text_input("🔍 ابحث جوّه " + label + " (اكتب أي جزء)", key=f"ta_q_{key}")
    out = df
    if _q:
        _m = pd.Series(False, index=df.index)
        for _c in df.columns:
            _m = _m | df[_c].astype(str).str.contains(str(_q), case=False, na=False)
        out = df[_m]
        st.caption(f"نتايج البحث: {len(out)} من {len(df)}")
    with _c2:
        _b = _io.BytesIO()
        with pd.ExcelWriter(_b, engine="openpyxl") as _xw:
            out.to_excel(_xw, index=False, sheet_name="data")
        st.download_button("⬇️ نزّل Excel", _b.getvalue(), file_name=f"{label}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key=f"ta_dl_{key}", use_container_width=True)
    with _c3:
        if st.button("🖥️ اعرض مكبّر", key=f"ta_big_{key}", use_container_width=True,
                     help="يفتح الجدول كبير تحت في نفس الصفحة"):
            st.session_state[f"ta_showbig_{key}"] = not st.session_state.get(f"ta_showbig_{key}")
    if st.session_state.get(f"ta_showbig_{key}"):
        st.dataframe(out, use_container_width=True, height=560)
        st.caption("👆 الجدول مكبّر — اسحبه يمين وشمال لو أعمدته كتير")
    return out

def _norm_ar(s):
    return re.sub(r"[أإآ]", "ا", re.sub(r"[ةه]$", "ه", str(s).strip())).lower()

def expiry_badge(item_name):
    """شارة الباتش/الصلاحية تظهر تلقائي جنب اسم الصنف في أي شاشة. ترجع '' لو مفيش بيانات."""
    try:
        _bt = st.session_state.get("mydata_batches")
        if _bt is None or _bt.empty or "الصنف" not in _bt.columns:
            return ""
        _t = _norm_ar(item_name)
        _hit = _bt[_bt["الصنف"].astype(str).map(_norm_ar).str.contains(_t, na=False)]
        if _hit.empty:
            return ""
        _d = pd.to_datetime(_hit["تاريخ انتهاء الصلاحية"], errors="coerce").dropna()
        if not _d.empty:
            _days = int((_d.min() - pd.Timestamp.now()).days)
            if _days < 0:
                return " ⛔ منتهي الصلاحية"
            if _days <= 90:
                return f" 🟠 صلاحية قريبة ({_days} يوم)"
            return f" 📅 صلاحية {_d.min().strftime('%Y-%m')}"
    except Exception:
        pass
    return ""

def _qty_col(df):
    """عمود الكمية الفعلي في شيت المخزون (يتسامح مع التسميتين)."""
    if df is None: return None
    for c in ("الكمية", "المخزون / الكمية", "المخزون"):
        if c in df.columns: return c
    return None


def morning_dashboard():
    """🌅 لوحة المتابعة على الرئيسية: أهم أرقام النهاردة من ملفه + زرار يوصله للقسم.
    محلي 100%، ميعرضش حاجة من غير بيانات، وكل رقم معروض زي ما هو (وصف مش توصية)."""
    _ms = st.session_state.get("mydata_stock")
    _bt = st.session_state.get("mydata_batches")
    _hist = st.session_state.get("mydata_history")
    _has = any(x is not None and hasattr(x, "__len__") and len(x)
               for x in (_ms, _bt, _hist))
    if not _has:
        return
    try:
        _low = None
        if _ms is not None and not _ms.empty and "الصنف" in _ms.columns and _qty_col(_ms):
            _q = pd.to_numeric(_ms[_qty_col(_ms)], errors="coerce")
            _m = pd.to_numeric(_ms.get("مبيعات الشهر"), errors="coerce")
            _low = int(((_m > 0) & (_q / _m * 30 <= 14)).sum())
        _soon = None
        if _bt is not None and not _bt.empty and "تاريخ انتهاء الصلاحية" in _bt.columns:
            _d = pd.to_datetime(_bt["تاريخ انتهاء الصلاحية"], errors="coerce")
            _soon = int((_d.notna() & (_d <= pd.Timestamp.now() + pd.DateOffset(days=90))).sum())
        _chg = None
        if _hist is not None and not _hist.empty:
            _ps = price_history_summary(_hist)
            if "التغير عن السابق %" in _ps.columns:
                _chg = int((_ps["التغير عن السابق %"].fillna(0) != 0).sum())
        _apn = None
        _ap = fix_approved(st.session_state.get("mydata_approved"))
        if not _ap.empty and "تاريخ السريان" in _ap.columns:
            _ad = pd.to_datetime(_ap["تاريخ السريان"], errors="coerce")
            _apn = int((_ad.notna() & (_ad <= pd.Timestamp.now() + pd.DateOffset(days=30))).sum())
        st.markdown("**🌅 لوحة المتابعة — أهم حاجة النهاردة**")
        _fmt = lambda v: "—" if v is None else (f"{v}" if v else "0 ✅")
        _c1, _c2, _c3, _c4 = st.columns(4)
        with _c1:
            st.metric("📉 نواقص محتملة", _fmt(_low))
            st.button("المخزون والتنبيه", key="dash_stock", use_container_width=True, on_click=_go, args=("stock",))
        with _c2:
            st.metric("🟠 قربت تخلص (90 يوم)", _fmt(_soon))
            st.button("المرتجعات", key="dash_exp", use_container_width=True, on_click=_go, args=("stock",))
        with _c3:
            st.metric("💹 أسعار اتغيرت", _fmt(_chg))
            st.button("تغيرات الأسعار", key="dash_chg", use_container_width=True, on_click=_go, args=("tools",))
        with _c4:
            st.metric("✅ تغييرات معتمدة سارية", _fmt(_apn))
            st.button("رادار الأسعار", key="dash_ap", use_container_width=True, on_click=_go, args=("tools",))
        st.caption("الأرقام دي من ملفك إنت: وصف للي موجود، مش توصية شراء.")
    except Exception:
        pass

def think_ahead(context_item=None, page=None):
    """طبقة 'تفكر قبلك': تقرأ إشارات أرقامه المحلية وتعرض الاقتراح في مكانه. محلي 100%."""
    notes = []
    try:
        if context_item:
            _t = _norm_ar(context_item)
            _ms = st.session_state.get("mydata_stock")
            if _ms is not None and not _ms.empty and "الصنف" in _ms.columns:
                _hit = _ms[_ms["الصنف"].astype(str).map(_norm_ar).str.contains(_t, na=False)]
                if not _hit.empty:
                    _r = _hit.iloc[0]
                    _q = pd.to_numeric(_r.get(_qty_col(_ms)), errors="coerce") if _qty_col(_ms) else None
                    _m = pd.to_numeric(_r.get("مبيعات الشهر"), errors="coerce")
                    if _q is not None and pd.notna(_q) and pd.notna(_m) and _m > 0 and _q / _m * 30 <= 14:
                        notes.append(f"📉 **{_r['الصنف']}**: مخزونه يكفي حوالي {int(_q/_m*30)} يوم بس — يتحط في الطلب المقترح")
            _bd = expiry_badge(context_item)
            if "🟠" in _bd or "⛔" in _bd:
                notes.append(f"📅 **{context_item}**:{_bd} — راجعه في المخزون قبل ما تطلب")
            _hist = st.session_state.get("mydata_history")
            if _hist is not None and not _hist.empty and "الصنف" in _hist.columns:
                _hh = _hist[_hist["الصنف"].astype(str).map(_norm_ar).str.contains(_t, na=False)]
                if not _hh.empty:
                    _net = pd.to_numeric(_hh.get("الصافي"), errors="coerce")
                    if _net.notna().any():
                        _i = _net.idxmin()
                        _sup = _hh.loc[_i].get("المورد", "")
                        _v = _hh.loc[_i].get("الصافي", "")
                        notes.append(f"💰 **{context_item}**: أقل صافي شفته في عروضك {_v} عند **{_sup}** — قارنه بالعرض الحالي")
        elif page == "offers":
            _hist = st.session_state.get("mydata_history")
            if _hist is not None and not _hist.empty:
                _ps = price_history_summary(_hist)
                if "التغير عن السابق %" in _ps.columns:
                    _nc = int((_ps["التغير عن السابق %"].fillna(0) != 0).sum())
                    if _nc:
                        notes.append(f"💹 في **{_nc}** صنف اتغيّر سعرهم في سجل عروضك — راجع «تغيرات الأسعار» في الأدوات قبل ما تقرر")
        elif page == "home":
            _ms = st.session_state.get("mydata_stock")
            if _ms is not None and not _ms.empty and "الصنف" in _ms.columns and _qty_col(_ms):
                _q = pd.to_numeric(_ms[_qty_col(_ms)], errors="coerce")
                _m = pd.to_numeric(_ms.get("مبيعات الشهر"), errors="coerce")
                _low = int(((_m > 0) & (_q / _m * 30 <= 14)).sum())
                if _low:
                    notes.append(f"📉 في **{_low}** صنف مخزونهم يكفي أقل من أسبوعين — افتح «المخزون والتنبيه»")
            for _ic, _tx in anticipation_notes(st.session_state.get("mydata_stock"),
                                               st.session_state.get("mydata_history"),
                                               st.session_state.get("mydata_batches"))[:2]:
                notes.append(f"{_ic} {_tx}")
            _bt = st.session_state.get("mydata_batches")
            if _bt is not None and not _bt.empty and "تاريخ انتهاء الصلاحية" in _bt.columns:
                _d = pd.to_datetime(_bt["تاريخ انتهاء الصلاحية"], errors="coerce")
                _soon = int((_d.notna() & (_d <= pd.Timestamp.now() + pd.DateOffset(days=90))).sum())
                if _soon:
                    notes.append(f"🟠 في **{_soon}** تشغيلة صلاحيتها خلال 90 يوم — افتح «المرتجعات»")
        elif page == "data":
            if st.session_state.get("mydata_stock") is None:
                notes.append("📥 شيت المخزون مش موجود في ملفك — من غيره مفيش تنبيه نواقص ولا طلب مقترح")
            if st.session_state.get("mydata_history") is None:
                notes.append("📜 سجل العروض مش موجود — من غيره مفيش «نمط السعر» ولا إشارات الزيادات المتكررة")
            if st.session_state.get("mydata_batches") is None:
                notes.append("📅 شيت التشغيلات مش موجود — من غيره مفيش إنذار قرب الانتهاء")
            if (st.session_state.get("data_sub") or "").startswith("📊"):
                _ssa = supplier_stats(st.session_state.get("mydata_history"))
                if not _ssa.empty:
                    _old = pd.to_datetime(_ssa["آخر عرض"], errors="coerce")
                    _stale = int((_old.notna() & (_old <= pd.Timestamp.now() - pd.DateOffset(days=60))).sum())
                    if _stale:
                        notes.append(f"📊 **{_stale}** مورد آخر عرض مسجل ليهم أقدم من 60 يوم — التحليلات عنهم وصف لتاريخ قديم، مش صورة دلوقتي")
            _ln2 = len(st.session_state.get("manual_map") or {})
            if _ln2:
                notes.append(f"🔗 عندك **{_ln2}** صنف مربوطين بقاموس الأدوية — الربط بيخلي المقارنة والبحث أدق")
            for _ic, _tx in anticipation_notes(st.session_state.get("mydata_stock"),
                                               st.session_state.get("mydata_history"),
                                               st.session_state.get("mydata_batches"))[:2]:
                notes.append(f"{_ic} {_tx}")
        elif page == "stock":
            _sub2 = st.session_state.get("stock_sub") or ""
            _ms = st.session_state.get("mydata_stock")
            if _sub2.startswith("📥") or not _sub2:
                for _ic, _tx in anticipation_notes(_ms, st.session_state.get("mydata_history"),
                                                   st.session_state.get("mydata_batches"))[:3]:
                    notes.append(f"{_ic} {_tx}")
            elif _sub2.startswith("🛒"):
                _hist2 = st.session_state.get("mydata_history")
                if _hist2 is not None and not _hist2.empty:
                    _cyc = offer_cycle_notes(_hist2)
                    _nr = sum(1 for v in _cyc.values() if v.startswith("⬆"))
                    if _nr:
                        notes.append(f"📈 **{_nr}** صنف سعرهم زاد متتالي في سجل عروضك — ده وصف للي حصل مش توقّع، راجعهم في «رادار الأسعار» قبل ما تعتمد الطلب")
                _bt2 = st.session_state.get("mydata_batches")
                if _bt2 is not None and not _bt2.empty and "تاريخ انتهاء الصلاحية" in _bt2.columns:
                    _d2 = pd.to_datetime(_bt2["تاريخ انتهاء الصلاحية"], errors="coerce")
                    _s2 = int((_d2.notna() & (_d2 <= pd.Timestamp.now() + pd.DateOffset(days=90))).sum())
                    if _s2:
                        notes.append(f"🟠 **{_s2}** تشغيلة صلاحيتها خلال 90 يوم — راجع إن الطلب المقترح ميكبّرش رصيدها")
            elif _sub2.startswith("📋"):
                _odp = orders_pending_receipt(st.session_state.get("mydata_orders"), days=3)
                if not _odp.empty:
                    notes.append(f"📤 **{len(_odp)}** طلب متعلّم «اتبعت» من 3 أيام أو أكتر وماتعلّمش استلام — الأولوية لمتابعتهم مع المورد")
                _odq = fix_orders(st.session_state.get("mydata_orders"))
                _nw = int((_odq["الحالة"] == "قيد الانتظار").sum()) if not _odq.empty else 0
                if _nw:
                    notes.append(f"🕓 **{_nw}** مسودة قيد الانتظار — لو بعتّها خلاص علّمها «اتبعت» علشان المتابعة تفضل صح")
            elif _sub2.startswith("⚠️"):
                _anm2 = match_announcements_to_stock(st.session_state.get("mydata_announcements"), st.session_state.get("mydata_stock"))
                if not _anm2.empty:
                    notes.append(f"⚠️ **{len(_anm2)}** تطابق بين إعلانات رسمية مسجلة ومخزونك — راجع المنشور الأصلي على موقع هيئة الدواء بنفسك")
                else:
                    notes.append("💡 سجّل أي إعلان سحب أو إيقاف بتشوفه على موقع هيئة الدواء edaegypt.gov.eg والتطبيق هيطابقه مع مخزونك أول بأول")
            elif _sub2.startswith("💉"):
                _csm2 = controlled_vs_stock(st.session_state.get("mydata_controlled"), st.session_state.get("mydata_stock"))
                if not _csm2.empty:
                    _bad2 = int((_csm2["الفرق"].fillna(0) != 0).sum())
                    if _bad2:
                        notes.append(f"💉 **{_bad2}** صنف في سجل المواد المخدرة رصيده مختلف عن المخزون — راجعهم بنفسك")
                    else:
                        notes.append("💉 سجل المواد المخدرة مطابق للمخزون في كل الأصناف المسجلة")
                else:
                    notes.append("💡 سجّل حركة الأصناف الخاضعة للرقابة (واردة/منصرفة لكل تشغيلة) والتطبيق يحسب الرصيد ويقارنه بالمخزون")
            elif _sub2.startswith("💸"):
                notes.append("💡 القائمة بتحسب هامشك من الأساسي المتعلم من عروضك وفواتيرك — لو أساسي صنف اتفاوض جديد، حدّثه من «بياناتي ← خصومات الأصناف» علشان الصائد يفضل دقيق")
            elif _sub2.startswith("↩️"):
                _bt3 = st.session_state.get("mydata_batches")
                if _bt3 is not None and not _bt3.empty and "تاريخ انتهاء الصلاحية" in _bt3.columns:
                    _d3 = pd.to_datetime(_bt3["تاريخ انتهاء الصلاحية"], errors="coerce")
                    _x3 = int((_d3.notna() & (_d3 <= pd.Timestamp.now())).sum())
                    if _x3:
                        notes.append(f"⛔ **{_x3}** تشغيلة عدّت تاريخ صلاحيتها — افصلها عن البيع وسجّلها مرتجع")
                    else:
                        notes.append("✅ مفيش تشغيلات عدّت تاريخها — أي تشغيلة توصل 90 يوم هتلاقيها هنا قبلها بوقت كافي")
                else:
                    notes.append("💡 ارفع شيت التشغيلات من «بياناتي» علشان إنذارات الصلاحية والمرتجعات تشتغل")
        elif page == "invoice":
            notes.append("💡 بعد ما ترفع الفاتورة، أي سطر سعره أعلى من آخر صافي مسجل عندك بيظهر في الجدول — قارنه قبل ما تعتمد")
        elif page == "tools":
            _ts2 = st.session_state.get("tools_sub") or ""
            if _ts2.startswith("📡") or not _ts2:
                notes.append("💡 تحت في الرادار: مؤشرات عامة مؤرخة بمصادرها + إشارات «من سجلك» + التغييرات المعتمدة — كل حاجة معروضة بمصدرها وتاريخها")
            elif _ts2.startswith("💹"):
                _hist3 = st.session_state.get("mydata_history")
                if _hist3 is not None and not _hist3.empty:
                    _cyc2 = offer_cycle_notes(_hist3)
                    _nr2 = sum(1 for v in _cyc2.values() if v.startswith("⬆"))
                    _nf2 = sum(1 for v in _cyc2.values() if v.startswith("⬇"))
                    if _nr2 or _nf2:
                        notes.append(f"📊 في سجلك: **{_nr2}** صنف زادوا متتالي و**{_nf2}** نزلوا — وصف للي حصل مش توقّع")
            elif _ts2.startswith("🧮"):
                notes.append("💡 لو الصنف في سجل عروضك، حاسبة التكلفة بتقترح أقل صافي سجلته — استخدمه نقطة بداية للتفاوض")
            elif _ts2.startswith("🤝"):
                notes.append("💡 قبل المكالمة: بص على «سجل الأسعار» للمورد ده — آخر خصم واتفاق سابق معاه أقوى ورقة تفاوض")
            elif _ts2.startswith("📅"):
                _bt4 = st.session_state.get("mydata_batches")
                if _bt4 is not None and not _bt4.empty and "تاريخ انتهاء الصلاحية" in _bt4.columns:
                    _d4 = pd.to_datetime(_bt4["تاريخ انتهاء الصلاحية"], errors="coerce")
                    _s4 = int((_d4.notna() & (_d4 <= pd.Timestamp.now() + pd.DateOffset(days=90))).sum())
                    if _s4:
                        notes.append(f"🟠 **{_s4}** تشغيلة صلاحيتها خلال 90 يوم — الأولوية للأقرب في الجدول")
            elif _ts2.startswith("💬"):
                notes.append("💡 ذاكرة واتس بتلخّص آخر ما اتفقت عليه مع كل مورد — راجعها قبل أي تفاوض جديد")
            elif _ts2.startswith("📜"):
                _hist4 = st.session_state.get("mydata_history")
                if _hist4 is not None and not _hist4.empty:
                    _cyc3 = offer_cycle_notes(_hist4)
                    _nr3 = sum(1 for v in _cyc3.values() if v.startswith("⬆"))
                    if _nr3:
                        notes.append(f"📈 **{_nr3}** صنف عندهم زيادات متتالية مسجلة — اتعرض في «رادار الأسعار» مع باقي الإشارات")
            elif _ts2.startswith("🏢"):
                notes.append("💡 أي اسم شركة مش متعرف عليه بيستنى تصحيحك هنا — الاسم الصح بيخلي المقارنة والصائد أدق")
        elif page == "download":
            notes.append("💡 حمّل نسخة جديدة من «بياناتي.xlsx» بعد أي تعديل في التصحيحات أو التغييرات المعتمدة علشان تفضل محفوظة عندك")
    except Exception:
        pass
    if notes:
        with st.container(border=True):
            st.markdown("**🧠 تفكر قبلك** — اقتراحات من أرقامك، محلي على جهازك")
            for _n in notes[:5]:
                st.markdown("- " + _n)




def page_chip(icon, name, desc, color1, color2):
    """شريط عنوان ملوّن متدرّج فوق كل صفحة - الهوية البصرية للقسم."""
    st.markdown(
        f"<div class='pagechip' style='background:linear-gradient(135deg,{color1},{color2})'>"
        f"<span style='font-size:1.5rem'>{icon}</span><span>{name}<br><small>{desc}</small></span></div>",
        unsafe_allow_html=True)

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

def _ensure_suggested_order():
    """Compute the suggested order once per session if any page needs it (offers drafts)."""
    if "suggested_order_df" in st.session_state:
        return
    _ms = st.session_state.get("mydata_stock")
    if _ms is None:
        return
    try:
        _so = suggested_order(_ms, st.session_state.get("so_dmin", 5))
        if not _so.empty:
            st.session_state["suggested_order_df"] = _so
    except Exception:
        pass


# ---------------- pages & navigation (v43) ----------------
_PAGES = [
    ("data", "📁", "بياناتي", "ملفك الواحد فيه كل حاجة"),
    ("stock", "📦", "المخزون والطلبات", "التنبيه والطلب المقترح وصائد الهامش والمرتجعات"),
    ("offers", "💰", "العروض والمقارنة", "ارفع عروض الموردين وقارنها ببعض"),
    ("invoice", "🧾", "مطابقة الفاتورة", "طابق الفاتورة بعرض السعر"),
    ("tools", "🧰", "أدوات إضافية", "التفاوض والصلاحيات وذاكرة المورد وسجل الأسعار"),
    ("search", "🔎", "البحث الموحد", "أي صنف: سعره وبدائله وبياناته"),
    ("download", "⬇️", "تحميل بياناتك", "حمّل بياناتي.xlsx المحدّث"),
]
if "_page" not in st.session_state:
    st.session_state["_page"] = "home"
_page = st.session_state["_page"]
_PAGE_NAMES = {k: f"{ic} {nm}" for k, ic, nm, _d in _PAGES}

def _go(p):
    st.session_state["_page"] = p

if _page == "home":
    st.markdown("""<div class='hero'><span class='hero-badge'>🗓️ نسخة 57 - ملخص الأسبوع</span>
<h1>مساعد الصيدلي</h1>
<p>مشتريات صيدليتك في مكان واحد: المخزون، العروض، المقارنة، والأسعار - من ملفك على جهازك.</p>
</div>""", unsafe_allow_html=True)
    _ms = st.session_state.get("mydata_stock")
    _mo = st.session_state.get("mydata_offers")
    _c1, _c2, _c3 = st.columns(3)
    _c1.metric("ملف بياناتي", "مرفوع ✅" if st.session_state.get("mydata_loaded") else "لسه")
    _c2.metric("أصناف المخزون", f"{len(_ms):,}" if _ms is not None and len(_ms) else "—")
    _c3.metric("سجل الأسعار", "فيه ✅" if st.session_state.get("mydata_history") is not None and len(st.session_state["mydata_history"]) else "—")
    st.caption("اختار الأداة اللي عايزها — كل حاجة مربوطة ببعضها من ملف بياناتي.")
    morning_dashboard()
    if st.session_state.get("mydata_loaded"):
        with st.expander("🗓️ ملخص الأسبوع (نص جاهز تنسخه)"):
            try:
                _ws = weekly_summary(
                    stock=st.session_state.get("mydata_stock"),
                    history=st.session_state.get("mydata_history"),
                    batches=st.session_state.get("mydata_batches"),
                    orders=st.session_state.get("mydata_orders"),
                    controlled=st.session_state.get("mydata_controlled"))
                st.code(_ws, language=None)
                st.download_button("⬇️ حمّل الملخص (نص)", data=_ws.encode("utf-8-sig"),
                                   file_name="weekly_summary.txt", mime="text/plain",
                                   key="ws_dl", use_container_width=True)
            except Exception:
                st.warning("مقدرناش نجهز الملخص من الملف ده — راجع شيتات بياناتي.")
            st.caption("كل الأرقام من ملفك إنت: وصف للي موجود، مش توقع ولا توصية شراء. النص ليك إنت — انسخه وابعته لنفسك أو لأي حد بإيدك.")
    think_ahead(page="home")
    for _r in range(0, len(_PAGES), 2):
        _cols = st.columns(2)
        for _c, (_k, _ic, _nm, _ds) in zip(_cols, _PAGES[_r:_r+2]):
            with _c:
                st.button(f"{_ic}  {_nm}", key=f"nav_{_k}", use_container_width=True,
                          on_click=_go, args=(_k,))
                st.caption(_ds)
    st.stop()

_hc1, _hc2 = st.columns([1, 3])
with _hc1:
    st.button("🏠 الرئيسية", key="nav_home", use_container_width=True, on_click=_go, args=("home",))
with _hc2:
    st.markdown(f"**{_PAGE_NAMES.get(_page, '')}**")

if _page == "data":
    page_chip("📁", "بياناتي", "ملفك الواحد فيه كل حاجة", "#0d7377", "#14919b")
    st.subheader("١) ملف بياناتي (كل حاجة في ملف واحد)")
    st.caption("ارفع بياناتي.xlsx أول ما تفتح: بيرجّع الروابط وسجل الأسعار وخصومات الأصناف وإعداداتك ومدة توريد كل مورد، ولو فيها قائمة أسعار الجمهور بيظهر سعر الجمهور جنب الأصناف ويتعلّم أساسي كل صنف من عروضك وفواتيرك (تقديري). في آخر الشغل حمّل النسخة المحدّثة من تحت وخزّنها عندك للمرة الجاية. مفيش ملف أول مرة؟ سيبه فاضي والتطبيق هيجهزهولك.")
    myf = st.file_uploader("بياناتي.xlsx", type=["xlsx"], key="mydata")
    if myf is not None and st.session_state.get("mydata_loaded") != (myf.name, myf.size):
        md = load_my_data(myf)
        if md["links"]:
            st.session_state["manual_map"] = {**md["links"], **st.session_state.get("manual_map", {})}
        if md["history"] is not None:
            st.session_state["mydata_history"] = md["history"]
            st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
        if md["suppliers"] is not None:
            st.session_state["mydata_suppliers"] = md["suppliers"]
        if md.get("discounts") is not None:
            st.session_state["mydata_discounts"] = md["discounts"]
        if md.get("public") is not None:
            st.session_state["mydata_public"] = md["public"]
            st.session_state["mydata_public_src"] = md.get("public_src")
            st.session_state.pop("pub_index", None)
        if md.get("item_disc") is not None:
            st.session_state["mydata_item_disc"] = md["item_disc"]
            st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
        if md.get("reference") is not None:
            st.session_state["mydata_reference"] = md["reference"]
            st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
            for _k in ("ref_index", "ref_barcodes", "ref_search"):
                st.session_state.pop(_k, None)
        if md.get("stock") is not None:
            st.session_state["mydata_stock"] = md["stock"]
        if md.get("batches") is not None:
            st.session_state["mydata_batches"] = md["batches"]
        if md.get("returns") is not None:
            st.session_state["mydata_returns"] = md["returns"]
        if md.get("cofix") is not None:
            st.session_state["mydata_cofix"] = md["cofix"]
        if md.get("approved") is not None:
            st.session_state["mydata_approved"] = md["approved"]
        if md.get("orders") is not None:
            st.session_state["mydata_orders"] = md["orders"]
        if md.get("announcements") is not None:
            st.session_state["mydata_announcements"] = md["announcements"]
        if md.get("controlled") is not None:
            st.session_state["mydata_controlled"] = md["controlled"]
        st.session_state["mydata_settings"] = md["settings"]
        st.session_state["mydata_loaded"] = (myf.name, myf.size)
        got = []
        if md["links"]: got.append(f"{len(md['links'])} ربط")
        if md["history"] is not None: got.append(f"{len(md['history'])} عرض في سجل الأسعار")
        if md["suppliers"] is not None: got.append(f"{len(md['suppliers'])} مورد")
        if md.get("discounts") is not None: got.append(f"خصومات {len(md['discounts'])} صنف")
        if md.get("public") is not None: got.append(f"أسعار الجمهور الرسمية ({len(md['public'])} صنف)")
        if md.get("item_disc") is not None: got.append(f"أساسي متعلم لـ {len(md['item_disc'])} صنف")
        if md.get("reference") is not None: got.append(f"مرجع فارما أوفرسيز ({len(md['reference']):,} صنف)")
        if md.get("stock") is not None: got.append(f"المخزون ({len(md['stock']):,} صنف)")
        if md.get("batches") is not None: got.append(f"التشغيلات ({len(md['batches']):,} باتش)")
        if md.get("returns") is not None: got.append(f"مرتجعات ونواقص ({len(md['returns']):,} سطر)")
        if md.get("cofix") is not None: got.append(f"تصحيحات شركات ({len(md['cofix'])})")
        if md.get("controlled") is not None: got.append(f"سجل مواد مخدرة ({len(md['controlled'])} حركة)")
        if md["settings"]: got.append("الإعدادات")
        st.success("اتحمّلت بياناتك" + (": " + "، ".join(got) if got else " (الملف فاضي أو مش مفهوم، هيبدأ من الصفر)."))
    think_ahead(page="data")
    _dsub = st.pills("أقسام بياناتك", ["🚚 مدة التوريد", "🏷️ خصومات الأصناف", "🎓 الأساسي المتعلم", "💲 أسعار الجمهور", "📊 تحليلات الموردين"], default="🚚 مدة التوريد", key="data_sub", label_visibility="collapsed")
    _ms = st.session_state.get("mydata_settings", {})
    def _setnum(key, dv):
        try: return float(_ms.get(key, dv))
        except (TypeError, ValueError): return float(dv)
    if "days_in" not in st.session_state: st.session_state["days_in"] = int(min(120, max(15, _setnum("cover_days", 45))))
    if "months_in" not in st.session_state: st.session_state["months_in"] = int(min(36, max(0, _setnum("min_months", 6))))
    if "lead_in" not in st.session_state: st.session_state["lead_in"] = int(min(60, max(1, _setnum("lead_days", 7))))
    if "safety_in" not in st.session_state: st.session_state["safety_in"] = int(min(30, max(0, _setnum("safety_days", 7))))
    if "buyer_in" not in st.session_state: st.session_state["buyer_in"] = str(_ms.get("buyer", ""))
    if "obuyer_in" not in st.session_state: st.session_state["obuyer_in"] = str(_ms.get("buyer", ""))
    if _dsub == "📊 تحليلات الموردين":
        st.subheader("تحليلات الموردين (من سجل عروضك)")
        _hst = st.session_state.get("mydata_history")
        _ss = supplier_stats(_hst)
        if _ss.empty:
            st.caption("مفيش عروض مسجلة في سجل الأسعار لسه. كل ما تضيف عروض موردين، التحليلات دي بتتملى لوحدها.")
        else:
            _m1, _m2, _m3 = st.columns(3)
            _m1.metric("موردين", len(_ss))
            _m2.metric("إجمالي العروض", int(_ss["عدد العروض"].sum()))
            _m3.metric("أوسع تغطية أصناف", str(_ss.iloc[0]["المورد"]))
            st.caption("الأرقام دي وصف لعروضك المسجلة بس، مش تقييم لمورد ولا توصية تتعامل مع حد. الجدول أوسع من الشاشة: اسحبه يمين وشمال.")
            st.dataframe(_ss, use_container_width=True)
    if _dsub == "🚚 مدة التوريد":
        _sdf = st.session_state.get("mydata_suppliers")
        if _sdf is None: _sdf = pd.DataFrame(columns=SUPPLIER_COLS)
        _ed = st.data_editor(_sdf, num_rows="dynamic", key=f"sup_edit_{st.session_state.get('mydata_loaded')}", use_container_width=True)
        st.session_state["mydata_suppliers"] = _ed

    if _dsub == "🏷️ خصومات الأصناف":
        st.caption("سجّل الأساسي % والهامش/الدعم بالجنيه لكل صنف من نشرات موردينك مرة واحدة، والحاسبة تملأ منها لوحدها. الأرقام دي من بياناتك أنت، مش مصدر رسمي عام. اكتب التركيز في اسم الصنف لو للصنف أكتر من تركيز (تلفاست 120 مش تلفاست 180).")
        _ddf = st.session_state.get("mydata_discounts")
        if _ddf is None: _ddf = pd.DataFrame(columns=DISCOUNT_COLS)
        _ded = st.data_editor(_ddf, num_rows="dynamic", key=f"disc_edit_{st.session_state.get('mydata_loaded')}", use_container_width=True)
        st.session_state["mydata_discounts"] = _ded

    if _dsub == "🎓 الأساسي المتعلم":
        st.caption("التطبيق بيتعلّم أساسي كل صنف لوحده من أسعاره في ملفاتك مقابل سعر الجمهور الرسمي، وبيقدّر بيه سعر الصيدلي للصنف ده بس. الأصناف اللي ماشفتش أسعارها مالهاش تقدير — على الأكثر «تخمين تقريبي» من متوسط شركتها ومتعلّم عليه إنه تخمين. الأرقام تقديرات من بياناتك أنت مش أسعار رسمية؛ عدّلها بإيدك لو عندك نشرة أدق.")
        _idf0 = st.session_state.get("mydata_item_disc")
        if _idf0 is None: _idf0 = pd.DataFrame(columns=ITEM_DISC_COLS)
        _ied = st.data_editor(_idf0, num_rows="dynamic", key=f"idisc_edit_{st.session_state.get('mydata_loaded')}", use_container_width=True)
        st.session_state["mydata_item_disc"] = fix_item_learned(_ied) if len(_ied) else _ied
        st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1

    _pub0 = st.session_state.get("mydata_public")
    if _dsub == "💲 أسعار الجمهور" and (_pub0 is None or not len(_pub0)):
        st.caption("لسه مفيش قائمة أسعار جمهور في ملفك — لما تضيفها هتظهر هنا.")
    if _pub0 is not None and len(_pub0) and _dsub == "💲 أسعار الجمهور":
        if True:
            st.caption("ابحث باسم الصنف عربي أو إنجليزي. «سعر الصيدلي التقديري» بيتحسب من أساسي الشركة المتعلم أعلاه — تقدير مش سعر رسمي.")
            _q = st.text_input("اسم الصنف", key="pub_search")
            if _q.strip():
                _qq = norm(_q).lower()
                _m = _pub0[_pub0["الصنف"].str.lower().str.contains(_qq, na=False) | _pub0["الاسم الإنجليزي"].str.lower().str.contains(_qq, na=False)]
                _m = _m.head(50).copy()
                _idf3 = st.session_state.get("mydata_item_disc")
                _m["سعر الصيدلي التقديري (متعلم)"] = _m.apply(lambda r: est_pharmacy_price(r["سعر الجمهور"], item_base(r["الصنف"], _idf3)), axis=1)
                def _g3(r):
                    if item_base(r["الصنف"], _idf3) is not None: return None
                    return est_pharmacy_price(r["سعر الجمهور"], company_median_base(r["الشركة"], _idf3))
                _m["تخمين تقريبي (متوسط الشركة)"] = _m.apply(_g3, axis=1)
                _m["الشركة"] = _m["الشركة"].map(company_ar)
                _show = [c for c in ["الصنف", "الشركة", "سعر الجمهور", "سعر الصيدلي التقديري (متعلم)", "تخمين تقريبي (متوسط الشركة)", "السعر السابق", "المادة الفعالة", "الفئة"] if c in _m.columns]
                st.dataframe(_m[_show], use_container_width=True)
                st.caption("الجدول أوسع من الشاشة: اسحبه يمين وشمال عشان تشوف باقي الأعمدة.")

if _page == "stock":
    page_chip("📦", "المخزون والطلبات", "التنبيه والطلب المقترح وصائد الهامش والمرتجعات", "#b45309", "#f59e0b")
    think_ahead(page="stock")
    _sub = st.pills("أدوات المخزون", ["📥 المخزون والتنبيه", "🛒 الطلب المقترح", "📋 طلباتي", "⚠️ إعلانات رسمية", "💉 المواد المخدرة", "💸 صائد الهامش", "↩️ المرتجعات"], default="📥 المخزون والتنبيه", key="stock_sub", label_visibility="collapsed")

    if _sub == "📥 المخزون والتنبيه":
        st.subheader("٢) المخزون وتنبيه إعادة الطلب")
        _bc_stock = st.session_state.get("mydata_stock")
        if _bc_stock is not None and not _bc_stock.empty:
            with st.expander("⚡ إدخال سريع بالباركود (واردة)"):
                st.caption("امسح الباركود بقارئ USB أو اكتبه ودوس Enter. لو الصنف متسجل بباركوده في ملفك، التطبيق بيجيبه وتضيف الكمية الواردة على رصيده. التعديل بيتحفظ لما تحمّل بياناتي.xlsx. الكمية بس — التكلفة والتشغيلة سجلها من شاشة المخزون لو محتاجها.")
                _bc_code = st.text_input("الباركود", key=f"bc_in_{st.session_state.get('bc_salt', 0)}", placeholder="مثال: 6221234567890")
                if _bc_code and _bc_code.strip():
                    _hits = barcode_find(_bc_stock, _bc_code)
                    if len(_hits) == 1:
                        _h = _hits.iloc[0]
                        st.success(f"**{_h['الصنف']}** — {_h['الشركة'] or 'بدون شركة'} — الرصيد الحالي: {_h['الكمية']:g}")
                        _bc_qty = st.number_input("الكمية الواردة", 1, 100000, 1, key="bc_qty")
                        if st.button("➕ سجّل الوارد على الرصيد", key="bc_add", use_container_width=True):
                            _ns, _nm = barcode_add(_bc_stock, _bc_code, _bc_qty)
                            if _nm == 1:
                                st.session_state["mydata_stock"] = _ns
                                st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
                                st.session_state.pop("suggested_order_df", None)
                                st.session_state["bc_salt"] = st.session_state.get("bc_salt", 0) + 1
                                st.success(f"اتسجلت: {_h['الصنف']} بقى رصيده {float(pd.to_numeric(pd.Series([_h['الكمية']]), errors='coerce').fillna(0).iloc[0]) + _bc_qty:g}. حمّل بياناتي.xlsx علشان تحفظها.")
                                st.rerun()
                    elif len(_hits) > 1:
                        st.warning("الباركود ده متسجل لأكتر من صنف — راجعهم بنفسك وعدّل من شاشة المخزون، التطبيق مش هيخمن:")
                        st.dataframe(_hits[["الصنف", "الشركة", "الكمية"]], use_container_width=True)
                    else:
                        _di = barcode_dict_info(st.session_state.get("mydata_public"), _bc_code)
                        if _di:
                            st.info(f"الباركود مش في شيت المخزون، لكنه في قاموس أسعار الجمهور بتاعك: **{_di['الصنف']}** — {_di['الشركة'] or 'بدون شركة'}" + (f" — سعر الجمهور {_di['سعر الجمهور']}" if pd.notna(_di.get('سعر الجمهور')) else "") + ". سجّله في شيت المخزون بباركوده الأول وبعدها الإدخال السريع هيلقطه.")
                        else:
                            st.warning("الباركود ده مش متسجل لا في المخزون ولا في قاموسك. سجّله الأول في شيت المخزون (عمود باركود) وبعدها امسحه تاني.")
        days = st.number_input("أيام التغطية", 15, 120, key="days_in")
        months = st.number_input("أقل مدة صلاحية متبقية مقبولة (شهر)", 0, 36, key="months_in")
        stockf = st.file_uploader("المخزون (أعمدة: صنف ومخزون ومبيعات شهرية، بأي اسم أو ترتيب)", type=["xlsx"])


        stock_df = None
        if stockf:
            try:
                raw_df, pre_map, sheet, nsheets = read_excel_smart(stockf, ["item", "stock", "monthly_sales"])
                if nsheets > 1: st.caption(f"الملف فيه {nsheets} sheets، اشتغلت على: {sheet}")
                stock_df = map_excel_ui(raw_df, ["item", "stock", "monthly_sales"], "map_stock", pre_map)
                if stock_df is not None:
                    st.session_state["_stock_df_cache"] = stock_df
            except Exception as e:
                st.error(str(e))
        if stock_df is not None:
            try:
                st.subheader("تنبيه إعادة الطلب")
                c1, c2 = st.columns(2)
                lead = c1.number_input("مدة توريد المورد (يوم)", 1, 60, key="lead_in")
                safety = c2.number_input("هامش أمان (يوم)", 0, 30, key="safety_in")
                ra = reorder_alert(stock_df, lead, safety, days)
                if "الصنف" in ra.columns and st.session_state.get("mydata_batches") is not None:
                    ra["الصلاحية"] = ra["الصنف"].map(lambda x: expiry_badge(x).strip())
                _ptf = price_trend_flags(st.session_state.get("mydata_history"))
                if _ptf and "الصنف" in ra.columns:
                    ra["🧠 تنبيه السعر"] = ra["الصنف"].map(lambda x: _ptf.get(_canon_fast(x), ""))
                    _nup = int((ra["🧠 تنبيه السعر"] == "⬆ زاد").sum())
                    if _nup:
                        st.warning(f"🧠 تفكر قبلك: {_nup} صنف في التنبيه سعرهم زاد في آخر عروضك — متأخرش طلبهم.")
                        ra = pd.concat([ra[ra["🧠 تنبيه السعر"] == "⬆ زاد"], ra[ra["🧠 تنبيه السعر"] != "⬆ زاد"]])
                st.dataframe(ra, use_container_width=True)
                n = int(ra["الحالة"].str.startswith("عاجل").sum())
                if n: st.error(f"{n} صنف لازم يتطلب النهارده")
                with st.expander("رسالة طلب سعر جاهزة"):
                    sup = st.text_input("اسم المورد (اختياري)")
                    buyer = st.text_input("اسمك / شركتك (اختياري)", key="buyer_in")
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
    if _sub == "🛒 الطلب المقترح":

        st.subheader("الطلب المقترح (من ملف بياناتي)")
        _stock_so = st.session_state.get("mydata_stock")
        if _stock_so is None:
            st.caption("ارفع بياناتي.xlsx من الخطوة ١ والطلب المقترح هيظهر هنا.")
        else:
            _dmin = st.number_input("الحد الأدنى الافتراضي لأي صنف مش متسجل له حد", 1, 100, 5, key="so_dmin")
            try:
                so = suggested_order(_stock_so, _dmin)
                if not so.empty and "الصنف" in so.columns and st.session_state.get("mydata_batches") is not None:
                    so["الصلاحية"] = so["الصنف"].map(lambda x: expiry_badge(x).strip())
                _ptf2 = price_trend_flags(st.session_state.get("mydata_history"))
                if not so.empty and _ptf2 and "الصنف" in so.columns:
                    so["🧠 تنبيه السعر"] = so["الصنف"].map(lambda x: _ptf2.get(_canon_fast(x), ""))
                    _nup2 = int((so["🧠 تنبيه السعر"] == "⬆ زاد").sum())
                    if _nup2:
                        st.warning(f"🧠 تفكر قبلك: {_nup2} صنف في الطلب سعرهم زاد في آخر عروضك — الأولوية ليهم.")
                        so = pd.concat([so[so["🧠 تنبيه السعر"] == "⬆ زاد"], so[so["🧠 تنبيه السعر"] != "⬆ زاد"]])
                if not so.empty:
                    _dl46 = {}
                    try:
                        _ms46 = st.session_state.get("mydata_stock")
                        if _ms46 is not None and not _ms46.empty and "الصنف" in _ms46.columns:
                            _qc46 = "الكمية" if "الكمية" in _ms46.columns else ("المخزون / الكمية" if "المخزون / الكمية" in _ms46.columns else None)
                            _mc46 = "مبيعات الشهر" if "مبيعات الشهر" in _ms46.columns else None
                            if _qc46 and _mc46:
                                _q46 = pd.to_numeric(_ms46[_qc46], errors="coerce")
                                _m46 = pd.to_numeric(_ms46[_mc46], errors="coerce")
                                for _nm46, _qq46, _mm46 in zip(_ms46["الصنف"], _q46, _m46):
                                    if pd.notna(_qq46) and pd.notna(_mm46) and _mm46 > 0:
                                        _dl46[_canon_fast(_nm46)] = _qq46 / _mm46 * 30
                    except Exception:
                        _dl46 = {}
                    try:
                        so = smart_priority(so, days_left=_dl46, trend=_ptf2 or {},
                                            exp_days=expiry_days_map(st.session_state.get("mydata_batches")))
                        st.caption("🎯 الأولوية بتحسب من أرقامك بس: أيام المخزون المتبقية + اتجاه السعر في عروضك + الصلاحية + الكوته. التفسير مكتوب في عمود «ليه الأولوية».")
                    except Exception:
                        pass
                if so.empty:
                    st.session_state.pop("suggested_order_df", None)
                    st.success("مفيش صنف تحت حده الأدنى دلوقتي.")
                else:
                    st.session_state["suggested_order_df"] = so
                    _tot = so["قيمة مقترحة"].sum(min_count=1)
                    st.warning(f"{len(so):,} صنف نازل تحت حده الأدنى أو مساوي له" + (f" - قيمة الطلب المقترح حوالي {_tot:,.0f} جنيه" if pd.notna(_tot) else ""))
                    st.caption("الكمية المقترحة = ضعف الحد الأدنى ناقص الموجود (تكفي دورتين من عروض السبت). دي قاعدة مبدئية لحد ما المبيعات الشهرية تتسجل، وبعدها بتتحسب من سرعة البيع. تكلفة الوحدة من متوسط تكلفة الشراء الحقيقية. الجدول بيسحب يمين وشمال.")
                    st.dataframe(so, use_container_width=True)
                    st.download_button("⬇️ صدّر الطلب المقترح (Excel مقسّم لكل مورد)", suggested_order_xlsx(so),
                                       "الطلب المقترح.xlsx", key="so_export", use_container_width=True)
                    st.caption("الملف فيه ورقة ملخص وورقة لكل مورد بأصنافه وكمياته وقيمتها — نسخة تراجعها وتبعتها بنفسك، التطبيق مبيبعتش حاجة.")
                    with st.expander("مسودة طلب جاهزة للواتساب (راجعها وابعتها بنفسك)"):
                        _lines = []
                        for _comp, _g in so.groupby("الشركة", dropna=False):
                            _lines.append(f"-- {_comp or 'بدون شركة'} --")
                            for _, _r in _g.iterrows():
                                _lines.append(f"{_r['الصنف']} × {int(_r['الكمية المقترحة'])}")
                        _so_msg = "طلب مقترح:\n" + "\n".join(_lines)
                        st.text_area("انسخها وابعتها", _so_msg, height=260, key="so_msg")
                        import urllib.parse as _up
                        st.link_button("افتح واتساب بالمسودة", "https://wa.me/?text=" + _up.quote(_so_msg))
                    if st.button("📌 سجّل الطلب ده في «طلباتي» (قيد الانتظار)", key="so_record", use_container_width=True):
                        _lines2 = [f"{_r['الصنف']} × {int(_r['الكمية المقترحة'])}" for _, _r in so.iterrows()]
                        st.session_state["mydata_orders"] = add_order(
                            st.session_state.get("mydata_orders"), _lines2,
                            total=float(_tot) if pd.notna(_tot) else None)
                        st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
                        st.success("اتسجل في «📋 طلباتي» بحالة قيد الانتظار. التطبيق مبيبعتش حاجة — إنت اللي بتبعت وبتعلّم عليه.")
                        st.rerun()
            except Exception as e:
                st.error(str(e))
    if _sub == "📋 طلباتي":
        st.subheader("طلباتي (سجل محلي في ملفك)")
        st.caption("سجل مسودات طلباتك وحالتها. التطبيق مبيبعتش أي طلب — الحالة بتتعلّم بيدك، والسجل بيتحفظ في بياناتي.xlsx لما تحمّله.")
        _odf = fix_orders(st.session_state.get("mydata_orders"))
        if _odf.empty:
            st.caption("مفيش طلبات مسجلة لسه. من «🛒 الطلب المقترح» دوس «سجّل الطلب ده في طلباتي».")
        else:
            _late = orders_pending_receipt(_odf, days=3)
            if not _late.empty:
                st.warning(f"🧠 تفكر قبلك: {len(_late)} طلب متعلّم «اتبعت» من 3 أيام أو أكتر وماتعلّمش استلام — تابع المورد.")
            st.download_button("⬇️ صدّر سجل الطلبات كله (Excel)", orders_to_xlsx(_odf), "طلباتي.xlsx",
                               key="ord_export_all", use_container_width=True)
            st.caption("الملف ده نسخة للمراجعة أو المشاركة اللي إنت تعملها بنفسك — التطبيق مبيبعتش حاجة.")
            for _i, _or in _odf.iloc[::-1].iterrows():
                _stt = _or["الحالة"]
                _ic = {"قيد الانتظار": "🕓", "اتبعت": "📤", "استلمت": "📥", "اتلغى": "🚫"}.get(_stt, "🕓")
                _tot_o = _or["القيمة المقترحة"]
                _lbl = f"{_ic} {_or['رقم الطلب']} — {_or['التاريخ']} — {int(_or['عدد الأصناف']) if pd.notna(_or['عدد الأصناف']) else '—'} صنف" + (f" — حوالي {_tot_o:,.0f} جنيه" if pd.notna(_tot_o) else "") + f" — {_stt}"
                with st.expander(_lbl):
                    st.caption(_or["الأصناف"])
                    st.text_area("نسخة نصية للطلب (انسخها وابعتها بنفسك)", order_text(_or), height=140, key=f"ord_txt_{_i}")
                    _c1, _c2, _c3 = st.columns(3)
                    if _stt == "قيد الانتظار":
                        if _c1.button("📤 اتبعت", key=f"ord_sent_{_i}", use_container_width=True):
                            st.session_state["mydata_orders"] = set_order_status(_odf, _or["رقم الطلب"], "اتبعت")
                            st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
                            st.rerun()
                    if _stt in ("قيد الانتظار", "اتبعت"):
                        if _c2.button("📥 استلمت", key=f"ord_recv_{_i}", use_container_width=True):
                            st.session_state["mydata_orders"] = set_order_status(_odf, _or["رقم الطلب"], "استلمت")
                            st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
                            st.rerun()
                        if _c3.button("🚫 إلغاء", key=f"ord_cxl_{_i}", use_container_width=True):
                            st.session_state["mydata_orders"] = set_order_status(_odf, _or["رقم الطلب"], "اتلغى")
                            st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
                            st.rerun()
    if _sub == "⚠️ إعلانات رسمية":
        st.subheader("إعلانات السحب والإيقاف الرسمية (تسجّلها إنت)")
        st.caption("سجّل هنا أي إعلان رسمي من هيئة الدواء المصرية بتشوفه بنفسك: سحب تشغيلة أو مستحضر أو إيقاف تداول أو تحذير. المصادر الرسمية: موقع هيئة الدواء edaegypt.gov.eg (قسم المنشورات) وخدمة الاستعلام eservices.edaegypt.gov.eg. التطبيق مبيقدمش تغذية آلية — اللي بتسجله إنت هو اللي بيتعرض، ومكتوب جنبه إنه من تسجيلك.")
        _andf = st.session_state.get("mydata_announcements")
        if _andf is None: _andf = pd.DataFrame(columns=ANN_COLS)
        _ane = st.data_editor(_andf, num_rows="dynamic", key=f"ann_edit_{st.session_state.get('mydata_loaded')}", use_container_width=True)
        st.session_state["mydata_announcements"] = _ane
        st.session_state["md_salt"] = st.session_state.get("md_salt", 0)
        _anm = match_announcements_to_stock(_ane, st.session_state.get("mydata_stock"))
        if not _anm.empty:
            st.warning(f"⚠️ {len(_anm)} تطابق بين إعلان مسجل وأصناف في مخزونك — راجع المنشور الأصلي على موقع هيئة الدواء بنفسك قبل أي قرار. التطبيق بيطابق أسماء بس، وممكن يغلط في الأسماء المتشابهة.")
            st.dataframe(_anm, use_container_width=True)
        elif len(_ane):
            st.caption("مفيش تطابق بين الإعلانات المسجلة وأصناف المخزون الحالي (مطابقة أسماء فقط).")
    if _sub == "💉 المواد المخدرة":
        st.subheader("سجل المواد المخدرة (متابعة داخلية)")
        st.caption("سجّل حركة الأصناف الخاضعة للرقابة: واردة ومنصرفة لكل تشغيلة مع التاريخ. التطبيق بيحسب الرصيد المتحرك ويقارنه بمخزونك. السجل ده للمتابعة الداخلية بس — مش بديل عن السجلات الرسمية المطلوبة قانونًا، ومفيش فيه أي استشارة قانونية. راجع المتطلبات الرسمية بنفسك.")
        _csdf = st.session_state.get("mydata_controlled")
        if _csdf is None: _csdf = pd.DataFrame(columns=CS_COLS)
        _cse = st.data_editor(_csdf, num_rows="dynamic", key=f"cs_edit_{st.session_state.get('mydata_loaded')}", use_container_width=True,
            column_config={"واردة": st.column_config.NumberColumn("واردة", min_value=0),
                           "منصرفة": st.column_config.NumberColumn("منصرفة", min_value=0)})
        st.session_state["mydata_controlled"] = fix_controlled(_cse)
        if len(st.session_state["mydata_controlled"]):
            _csb = controlled_balances(st.session_state["mydata_controlled"])
            st.caption("الرصيد المتحرك لكل تشغيلة (واردة ناقص منصرفة بالترتيب الزمني). الجدول بيسحب يمين وشمال.")
            st.dataframe(_csb, use_container_width=True)
            if st.session_state.get("mydata_stock") is not None:
                _csm = controlled_vs_stock(st.session_state["mydata_controlled"], st.session_state["mydata_stock"])
                _bad = _csm[_csm["الفرق"].fillna(0) != 0]
                if not _bad.empty:
                    st.warning(f"⚠️ {len(_bad)} صنف رصيد سجلهم مختلف عن المخزون — راجعهم بنفسك. الفرق = رصيد السجل ناقص رصيد المخزون. التطبيق بيقارن بس، مبيعدّلش أي رقم لوحده.")
                    st.dataframe(_bad, use_container_width=True)
                else:
                    st.success("رصيد السجل مطابق للمخزون في كل الأصناف المسجلة.")
        else:
            st.caption("لسه مفيش حركات مسجلة. اكتب أول حركة في الجدول فوق — بتتحفظ مع بياناتي.xlsx المحدّث.")
    if _sub == "💸 صائد الهامش":

        st.subheader("صائد الهامش (بالتكلفة الحقيقية)")
        if st.session_state.get("mydata_stock") is None:
            st.caption("ارفع بياناتي.xlsx من الخطوة ١ وصائد الهامش هيظهر هنا.")
        elif st.session_state.get("mydata_public") is None or not len(st.session_state.get("mydata_public")):
            st.caption("محتاج قائمة أسعار الجمهور في بياناتي.xlsx علشان يحسب الهامش.")
        else:
            if "pub_index" not in st.session_state:
                st.session_state["pub_index"] = public_price_index(st.session_state["mydata_public"])
            _thin = st.number_input("اعتبر الهامش ضعيف لو أقل من %", 1, 60, 20, key="mh_thin")
            _mh = margin_hunter(st.session_state["mydata_stock"], st.session_state["pub_index"], _thin, cofix=st.session_state.get("mydata_cofix"))
            if _mh.empty:
                st.caption("مفيش أصناف ليها سعر جمهور وتكلفة معروفين في الملف.")
            else:
                _loss = int((_mh["هامشك (جنيه)"] < 0).sum())
                _thinn = int(((_mh["هامشك (جنيه)"] >= 0) & (_mh["هامشك %"] < _thin)).sum())
                if _loss: st.error(f"{_loss} صنف بتبيعه بخسارة (تكلفتك الحقيقية فوق سعر الجمهور)")
                if _thinn: st.warning(f"{_thinn} صنف هامشهم ضعيف (أقل من {_thin}%)")
                if not _loss and not _thinn: st.success("كل الأصناف اللي ليها بيانات هامشها كويس.")
                st.caption("الحساب: هامشك = سعر الجمهور الرسمي ناقص تكلفتك الحقيقية (متوسط ما دفعته من إجمالي التكلفة على إجمالي الكمية). «أساسيك الفعلي» هو الخصم اللي تكلفتك بتعنيه جنب سعر الجمهور - لو أقل من أساسي السوق للصنف، في مجال تفاوض. الأصناف اللي ملهاش سعر جمهور أو تكلفة بتتساب، مش بنخمنها. الأسوأ الأول. الجدول بيسحب يمين وشمال.")
                _mh = table_actions(_mh, "mh_main", "صائد الهامش")
                st.dataframe(_mh, use_container_width=True)
    if _sub == "↩️ المرتجعات":

        st.subheader("المرتجعات والنواقص")
        st.caption("سجّل أي مرتجع لمورد أو صنف ناقص. بيتحفظ في بياناتي.xlsx مع التحميل.")
        _bt = st.session_state.get("mydata_batches")
        if _bt is not None and not _bt.empty:
            _bbd = pd.to_datetime(_bt["تاريخ انتهاء الصلاحية"], errors="coerce")
            _cut = pd.Timestamp.now() + pd.DateOffset(months=int(st.session_state.get("months_in", 6)))
            _soon = _bt[_bbd.notna() & (_bbd <= _cut)]
            if not _soon.empty:
                st.info(f"{len(_soon)} تشغيلة قربت تخلص خلال {int(st.session_state.get('months_in', 6))} شهر")
                st.dataframe(_soon, use_container_width=True)
                if st.button("ضيفهم كمرتجعات مسودة", key="ret_add_soon"):
                    _new = pd.DataFrame({"التاريخ": pd.Timestamp.now().strftime("%Y-%m-%d"),
                                         "الصنف": _soon["الصنف"], "المورد": "", "الكمية": _soon["الكمية"],
                                         "النوع": "مرتجع", "السبب": "قرب الانتهاء", "الحالة": "مسودة"})
                    _base = st.session_state.get("mydata_returns")
                    st.session_state["mydata_returns"] = fix_returns_sheet(pd.concat([_base, _new], ignore_index=True))
                    st.rerun()
        _ret = st.session_state.get("mydata_returns")
        _ret = _ret if _ret is not None else pd.DataFrame(columns=RETURNS_SHEET_COLS)
        _ed = st.data_editor(_ret, num_rows="dynamic", use_container_width=True, key="ret_editor",
            column_config={"النوع": st.column_config.SelectboxColumn("النوع", options=["مرتجع", "ناقص"]),
                           "الحالة": st.column_config.SelectboxColumn("الحالة", options=["مسودة", "اتبعت", "اتسوّى"])})
        if st.button("احفظ المرتجعات والنواقص", key="ret_save"):
            st.session_state["mydata_returns"] = fix_returns_sheet(_ed)
            st.success("اتحفظت - هتنزل مع بياناتي.xlsx المحدّث.")
if _page == "offers":
    page_chip("💰", "العروض والمقارنة", "ارفع عروض الموردين وقارنها", "#047857", "#10b981")
    think_ahead(page="offers")
    _ensure_suggested_order()
    days = st.session_state.get("days_in", 30)
    months = st.session_state.get("months_in", 6)
    stock_df = st.session_state.get("_stock_df_cache")
    st.subheader("٣) عروض الموردين والمقارنة")
    files = st.file_uploader("عروض الموردين (إكسيل / PDF / نص واتس)", accept_multiple_files=True, type=["xlsx", "pdf", "txt"])
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
        if st.session_state.get("mydata_public") is not None and st.session_state.get("pub_index"):
            _lines = [{"item": str(r["item"]), "price": r["price"]} for _, r in allo.iterrows() if r.get("price")]
            _smp = implied_base_samples(_lines, st.session_state["pub_index"])
            _lk = hash((len(_lines), tuple(sorted(_smp))))
            if _smp and st.session_state.get("learned_from") != _lk:
                st.session_state["mydata_item_disc"] = merge_item_bases(st.session_state.get("mydata_item_disc"), _smp)
                st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
                st.session_state["learned_from"] = _lk
                st.success(f"اتعلّم أساسي تقديري لـ {len(_smp)} صنف من {sum(len(v['bases']) for v in _smp.values())} سطر عرض (لكل صنف لوحده، تقديري من ملفاتك، بيتحفظ في بياناتي.xlsx لما تحمّله).")
        _hst = st.session_state.get("mydata_history")
        _hstats = history_price_stats(_hst, list(cmp_["الصنف"])) if _hst is not None and len(_hst) else {}
        if _hstats:
            cmp_["آخر صافي في السجل"] = cmp_["الصنف"].map(lambda x: _hstats.get(x, {}).get("last"))
            cmp_["أقل صافي في السجل"] = cmp_["الصنف"].map(lambda x: _hstats.get(x, {}).get("min"))
            def _verdict(r):
                stt = _hstats.get(r["الصنف"])
                if not stt or not stt.get("min"): return ""
                if r["السعر بعد الخصم"] <= stt["min"]: return "زي أقل سعر شفته أو أحسن"
                return f"أعلى من أقل سعر شفته بـ {round((r['السعر بعد الخصم'] / stt['min'] - 1) * 100, 1)}%"
            cmp_["حكم السجل"] = cmp_.apply(_verdict, axis=1)
        else:
            st.caption("لو رفعت بياناتي.xlsx فيها سجل أسعار (أو ضفت عروض للسجل من تحت)، هيظهر جنب كل صنف آخر وأقل سعر شفته وحكم السجل على العرض الحالي.")
        _pub = st.session_state.get("mydata_public")
        if _pub is not None and len(_pub):
            if "pub_index" not in st.session_state:
                st.session_state["pub_index"] = public_price_index(_pub)
            _pidx = st.session_state["pub_index"]
            cmp_["سعر الجمهور"] = cmp_["الصنف"].map(lambda x: find_public_price(x, _pidx))
            _idf = st.session_state.get("mydata_item_disc")
            def _est(x):
                hit = find_public_row(x, _pidx)
                if not hit: return None
                return est_pharmacy_price(hit[0], item_base(hit[2] or x, _idf))
            cmp_["سعر الصيدلي التقديري (متعلم)"] = cmp_["الصنف"].map(_est)
            def _est_g(x):
                hit = find_public_row(x, _pidx)
                if not hit: return None
                if item_base(hit[2] or x, _idf) is not None: return None
                return est_pharmacy_price(hit[0], company_median_base(hit[1], _idf))
            cmp_["تخمين تقريبي (متوسط الشركة)"] = cmp_["الصنف"].map(_est_g)
            def _pm(r):
                p = r["سعر الجمهور"]
                if not p: return ""
                return round((1 - r["السعر بعد الخصم"] / p) * 100, 1)
            cmp_["هامشك عن سعر الجمهور %"] = cmp_.apply(_pm, axis=1)
            _cols = list(cmp_.columns)
            for _c in ("سعر الجمهور", "سعر الصيدلي التقديري (متعلم)", "تخمين تقريبي (متوسط الشركة)", "هامشك عن سعر الجمهور %"):
                _cols.remove(_c)
            _at = _cols.index("السعر بعد الخصم") + 1 if "السعر بعد الخصم" in _cols else len(_cols)
            cmp_ = cmp_[_cols[:_at] + ["سعر الجمهور", "سعر الصيدلي التقديري (متعلم)", "تخمين تقريبي (متوسط الشركة)", "هامشك عن سعر الجمهور %"] + _cols[_at:]]
            if _idf is not None and len(_idf):
                st.caption("«سعر الصيدلي التقديري (متعلم)» = سعر الجمهور ناقص أساسي الصنف نفسه المتعلم من فواتيرك وعروضك. «تخمين تقريبي» للأصناف اللي مش متعلمة، من متوسط أساسي شركتها — تخمين أولي بعيد عن الدقة، مش سعر رسمي.")
        _ref = st.session_state.get("mydata_reference")
        if _ref is not None and len(_ref) and "الصنف" in cmp_.columns:
            if "ref_index" not in st.session_state:
                st.session_state["ref_index"] = reference_index(_ref)
            _ridx = st.session_state["ref_index"]
            def _rf(x, col):
                h = find_reference(x, _ridx)
                return h[col] if h else ""
            cmp_["فارما أوفرسيز جمهور"] = cmp_["الصنف"].map(lambda x: _rf(x, "سعر الجمهور"))
            cmp_["فارما أوفرسيز صيدلي"] = cmp_["الصنف"].map(lambda x: _rf(x, "سعر الصيدلي"))
            cmp_["فارما أوفرسيز أساسي %"] = cmp_["الصنف"].map(lambda x: _rf(x, "الأساسي %"))
            st.caption("أعمدة «فارما أوفرسيز» مرجع من حسابك على الموقع: سعر الجمهور وسعر الصيدلي والأساسي (تقديري غالبًا - درجة الثقة في صفحة المرجع في ملفك).")
        if "الصنف" in cmp_.columns and st.session_state.get("mydata_batches") is not None:
            cmp_["تنبيه الصلاحية"] = cmp_["الصنف"].map(lambda x: expiry_badge(x).strip())
        _ptf3 = price_trend_flags(st.session_state.get("mydata_history"))
        if _ptf3 and "الصنف" in cmp_.columns:
            cmp_["🧠 اتجاه السعر (آخر تغيّر)"] = cmp_["الصنف"].map(lambda x: _ptf3.get(_canon_fast(x), ""))
        _ocn46 = offer_cycle_notes(st.session_state.get("mydata_history"))
        if _ocn46 and "الصنف" in cmp_.columns:
            cmp_["🧠 نمط السعر (من سجلك)"] = cmp_["الصنف"].map(lambda x: _ocn46.get(_canon_fast(x), ""))
        st.subheader("المقارنة")
        if "البونص" in cmp_.columns and cmp_["البونص"].astype(str).str.strip().replace("", None).notna().any():
            st.caption("«السعر بعد الخصم» شامل البونص لما يكون مكتوب في العرض: «10+2» بيوزع التكلفة على الوحدات المستلمة، و«5%» بيتخصم زيادة.")
        cmp_ = table_actions(cmp_, "cmp_main", "المقارنة")
        st.dataframe(cmp_, use_container_width=True)
        st.caption("الجدول أوسع من الشاشة: اسحبه يمين وشمال عشان تشوف باقي الأعمدة.")
        allo_ar = offers_display(allo)
        if _pub is not None and len(_pub) and "الصنف" in allo_ar.columns:
            allo_ar["سعر الجمهور"] = allo_ar["الصنف"].map(lambda x: find_public_price(x, st.session_state["pub_index"]))
            _idf2 = st.session_state.get("mydata_item_disc")
            def _est2(x):
                hit = find_public_row(x, st.session_state["pub_index"])
                if not hit: return None
                return est_pharmacy_price(hit[0], item_base(hit[2] or x, _idf2))
            allo_ar["سعر الصيدلي التقديري (متعلم)"] = allo_ar["الصنف"].map(_est2)
        st.subheader("كل العروض"); st.dataframe(allo_ar, use_container_width=True)
        st.caption("الجدول أوسع من الشاشة: اسحبه يمين وشمال عشان تشوف باقي الأعمدة.")
        st.subheader("فرص الأسبوع (العرض أحسن من أساسيك المسجل)")
        _opp = weekly_opportunities(allo, st.session_state.get("mydata_item_disc"), st.session_state.get("pub_index"))
        if len(_opp):
            st.success(f"{len(_opp)} فرصة: العرض بيدي أساسي أعلى من المسجل عندك للصنف نفسه.")
            st.dataframe(_opp, use_container_width=True)
            st.caption("فرصة = أساسي العرض المحسوب من سعر الجمهور أعلى من أساسيك المسجل للصنف بنقطة أو أكتر. حساب لكل صنف لوحده من ملفاتك. الجدول بيسحب يمين وشمال.")
        else:
            st.caption("مفيش صنف في العروض دي أعلى من أساسيك المسجل (أو الأصناف لسه متعلمتش أساسيها).")
        with st.expander("مسودة واتساب لكل مورد (طلبك + فرصه - راجعها وابعتها بنفسك)"):
            _so_df = st.session_state.get("suggested_order_df")
            def _sup_key(s):
                return " ".join(t for t in norm(str(s or "")).split() if t not in ("عرض", "عروض", "ملف"))
            def _sup_match(a, b):
                a, b = _sup_key(a), _sup_key(b)
                return bool(a and b) and (a in b or b in a)
            for _sup in sorted({str(s).strip() for s in allo["supplier"] if str(s).strip()}):
                _oi = None
                if _so_df is not None and len(_so_df) and "الشركة" in _so_df.columns:
                    _oi = _so_df[_so_df["الشركة"].map(lambda x: _sup_match(x, _sup))]
                    if not len(_oi): _oi = None
                _pi = _opp[_opp["المورد"] == _sup] if len(_opp) else None
                if _oi is None and (_pi is None or not len(_pi)):
                    continue
                _msg = supplier_weekly_draft(_sup, _oi, _pi)
                st.markdown(f"**{_sup}**")
                st.text_area("انسخها", _msg, height=180, key=f"supdraft_{_sup}")
                import urllib.parse as _up2
                st.link_button(f"افتح واتساب بمسودة {_sup}", "https://wa.me/?text=" + _up2.quote(_msg), key=f"supwa_{_sup}")
            if _so_df is None and not len(_opp):
                st.caption("ارفع عروض الأسبوع وحسب الطلب المقترح من الخطوة اللي فوق علشان تظهر المسودات هنا.")
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
        if st.button("ضيف عروض النهارده لسجل الأسعار", key="btn_offers_to_hist"):
            try:
                import datetime as _dt
                _rows = [dict(r, date=_dt.date.today()) for r in offers]
                _hist = st.session_state.get("mydata_history")
                _before = len(_hist) if _hist is not None else 0
                _merged = update_price_history(_hist, _rows)
                st.session_state["mydata_history"] = _merged
                st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
                _added = len(_merged) - _before
                st.success(f"سجل الأسعار فيه دلوقتي {len(_merged)} عرض" + (f" (اتضاف {_added} جديد)." if _added else " (كلها موجودة قبل كده).") + " هيتخزن في بياناتي.xlsx لما تحمّله من تحت.")
            except Exception as e:
                st.error(str(e))
        orders = build_order_messages(cmp_)
        if orders:
            with st.expander("رسائل الطلب النهائية لكل مورد (مسودة، راجعها وابعتها بنفسك)", expanded=True):
                obuyer = st.text_input("اسمك / اسم الصيدلية (بيظهر في التوقيع، اختياري)", key="obuyer_in")
                _sup_leads = {}
                _sdf2 = st.session_state.get("mydata_suppliers")
                if _sdf2 is not None and not _sdf2.empty:
                    for _, _r in _sdf2.iterrows():
                        if pd.notna(_r[SUPPLIER_COLS[0]]):
                            _sup_leads[str(_r[SUPPLIER_COLS[0]]).strip()] = _r[SUPPLIER_COLS[1]]
                for od in build_order_messages(cmp_, obuyer.strip()):
                    if od["supplier"] in _sup_leads:
                        st.caption(f"مدة التوريد المسجلة لـ {od['supplier']}: {_sup_leads[od['supplier']]} يوم")
                    st.markdown(f"**طلب لـ {od['supplier']}** — {od['items']} صنف، إجمالي {od['total']:,.2f} جنيه")
                    st.text_area("المسودة", od["message"], height=200, key=f"ord_{od['supplier']}")
                    import urllib.parse
                    st.link_button(f"افتح واتساب بطلب {od['supplier']}", "https://wa.me/?text=" + urllib.parse.quote(od["message"]))
        _sup_opts = sorted(cmp_["أرخص مورد"].unique())
        with st.expander("اعتمد العروض المتفق عليها (لمطابقة الفاتورة تلقائي)"):
            st.caption("بعد ما تتفق مع المورد: اختاره هنا ودوس «اعتمد». مطابقة الفاتورة تحت هتستخدم الأسعار المتفق عليها دي على طول، من غير ما ترفع ملف العرض تاني.")
            _picked = st.multiselect("الموردون المتفق معاهم", _sup_opts, key="agreed_picked")
            if st.button("اعتمد الاختيار", key="btn_agree"):
                if not _picked:
                    st.error("اختار مورد واحد على الأقل الأول.")
                else:
                    _ag = build_agreed_offers(allo, cmp_, _picked)
                    st.session_state["agreed_offers"] = _ag
                    st.session_state["agreed_suppliers"] = list(_picked)
                    st.success(f"اتعتمد {len(_ag)} صنف من {len(_picked)} مورد. انزل لمطابقة الفاتورة تحت — هتلاقيها جاهزة.")
        _ag = st.session_state.get("agreed_offers") or []
        if _ag:
            st.caption(f"المعتمد دلوقتي للجلسة: {len(_ag)} صنف من {', '.join(st.session_state.get('agreed_suppliers', []))}.")


if _page == "invoice":
    page_chip("🧾", "مطابقة الفاتورة", "طابق الفاتورة بعرض السعر", "#7c3aed", "#a78bfa")
    think_ahead(page="invoice")
    st.subheader("٤) مطابقة الفاتورة بعرض السعر")
    st.caption("ارفع عرض السعر المتفق عليه والفاتورة، والتطبيق يطلّع أي سطر اتسعّر أعلى من المتفق عليه أو مش في العرض أصلًا. بيتحقق كمان من التركيز وحجم العبوة: أي اختلاف بيتحط في «محتاج مراجعة» بدل ما يتحاسب غلط.")
    _ag0 = st.session_state.get("agreed_offers") or []
    if _ag0:
        st.info(f"فيه عروض معتمدة من المقارنة فوق ({len(_ag0)} صنف من {', '.join(st.session_state.get('agreed_suppliers', []))}). لو ما رفعتش عرض يدوي، هستخدمها على طول. ولو رفعت ملف عرض، هو اللي هيتستخدم.")
    ioff = st.file_uploader("عرض السعر المتفق عليه (إكسيل، اختياري لو معتمد من فوق)", accept_multiple_files=True, type=["xlsx"], key="inv_off")
    invf = st.file_uploader("الفاتورة (صورة من الموبايل، أو إكسيل: صنف وسعر، والكمية اختياري)", type=["xlsx", "png", "jpg", "jpeg"], key="inv_f")
    cv1, cv2 = st.columns(2)
    offer_vat = cv1.checkbox("أسعار العرض شاملة ض.ق.م 14% (هتتفك قبل المقارنة)", key="offer_vat")
    inv_vat = cv2.checkbox("أسعار الفاتورة شاملة ض.ق.م 14% (هتتفك قبل المقارنة)", key="inv_vat")
    if not offer_vat and not inv_vat:
        st.caption("من غير تحديد، المقارنة بتفترض إن العرض والفاتورة على نفس الأساس الضريبي.")
    if (ioff or _ag0) and invf:
        try:
            ioffers = []
            if ioff:
                for f in ioff:
                    ioffers += parse_excel(f, f.name.rsplit(".", 1)[0])
            else:
                ioffers = [dict(x) for x in _ag0]
                st.caption(f"بيقارن بالعروض المعتمدة في الجلسة ({len(ioffers)} صنف).")
            if invf.name.lower().endswith((".png", ".jpg", ".jpeg")):
                _okey = (invf.name, invf.size)
                if st.session_state.get("_ocr_key") != _okey:
                    with st.spinner("بقرا صورة الفاتورة..."):
                        st.session_state["_ocr_res"] = ocr_invoice_image(invf.getvalue())
                        st.session_state["_ocr_key"] = _okey
                inv, _ocr_raw = st.session_state["_ocr_res"]
                with st.expander("النص اللي اتقرا من الصورة"):
                    st.text(_ocr_raw.strip() or "(مفيش نص اتقرا)")
                if inv:
                    st.caption("راجع السطور المقروءة وعدّل أي غلطة قبل المقارنة - قراءة الصور ممكن تغلط، ومفيش حاجة بتتحاسب غلط من غير ما تشوفها.")
                    _invdf = st.data_editor(pd.DataFrame(inv), num_rows="dynamic", key="inv_img_edit",
                        column_config={"item": st.column_config.TextColumn("الصنف"),
                                       "price": st.column_config.NumberColumn("السعر"),
                                       "qty": st.column_config.NumberColumn("الكمية")})
                    inv = [dict(item=str(r["item"]), price=num(r["price"]), qty=num(r.get("qty")))
                           for _, r in _invdf.iterrows() if str(r.get("item", "")).strip() and num(r.get("price"))]
            else:
                inv = parse_invoice(invf)
            if not inv:
                st.error("ما قدرتش أقرا الفاتورة. لازم أعمدة صنف وسعر (أو صورة أوضح).")
            else:
                chk = check_invoice(ioffers, inv, invoice_vat=inv_vat, offer_vat=offer_vat)
                if st.session_state.get("mydata_public") is not None and st.session_state.get("pub_index"):
                    _vd = 1.14 if inv_vat else 1
                    _ilines = [{"item": l["item"], "price": l["price"] / _vd} for l in inv if l.get("price")]
                    _ismp = implied_base_samples(_ilines, st.session_state["pub_index"])
                    if _ismp:
                        st.session_state["mydata_item_disc"] = merge_item_bases(st.session_state.get("mydata_item_disc"), _ismp)
                        st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
                        st.success(f"اتعلّم أساسي تقديري لـ {len(_ismp)} صنف من سطور الفاتورة (لكل صنف لوحده، تقديري، بيتحفظ في بياناتي.xlsx).")
                over = chk[chk["الحالة"].str.startswith("أعلى")]
                miss = chk[chk["الحالة"] == "صنف مش في العرض"]
                rev = chk[chk["الحالة"].str.startswith(("تحقق", "غامض"))]
                c1, c2, c3 = st.columns(3)
                c1.metric("سطور الفاتورة", len(chk))
                c2.metric("سطور أعلى من العرض", len(over))
                extra = float(over["قيمة الفرق"].sum()) if len(over) else 0
                c3.metric("إجمالي فرق التسعير", f"{extra:,.2f} جنيه")
                if len(over): st.error(f"{len(over)} سطر اتسعّر أعلى من المتفق عليه.")
                if len(rev): st.warning(f"{len(rev)} سطر محتاج مراجعة يدوية (تحقق/غامض): مش محسوب في فرق التسعير ولا في المسودة.")
                if not len(over) and not len(rev):
                    if len(miss): st.warning("في أصناف في الفاتورة مش موجودة في العرض.")
                    else: st.success("كل الفاتورة مطابقة للعرض (أو أقل).")
                st.dataframe(chk, use_container_width=True)
                st.session_state["_last_invoice_chk"] = chk
                st.caption("الجدول أوسع من الشاشة: اسحبه يمين وشمال عشان تشوف باقي الأعمدة.")
                sup_mode = over["المورد"].mode().iloc[0] if len(over) and over["المورد"].ne("").any() else ""
                d = draft_invoice_dispute(chk, supplier=sup_mode)
                if d:
                    with st.expander("مسودة رسالة للمورد بالفروق (راجعها وابعتها بنفسك)", expanded=True):
                        st.text_area("المسودة", d, height=220, key="inv_draft")
                        import urllib.parse
                        st.link_button("افتح واتساب بالمسودة", "https://wa.me/?text=" + urllib.parse.quote(d))
        except Exception as e:
            st.error(str(e))
    with st.expander("🇪🇬 جاهزية الفاتورة الإلكترونية وتتبع الدواء (تجهيز محلي بس - مفيش إرسال لأي جهة)"):
        st.caption("دي خطوة تجهيز على جهازك بس، مش بنبعت حاجة لمصلحة الضرائب ولا هيئة الدواء. الفاتورة الإلكترونية (ETA) محتاجة تسجيلك الرسمي والرقم الضريبي للمورد، وتتبع الدواء (EPTTS) محتاج باركود GS1 ورقم التشغيلة لكل صنف. الجدول تحت بيجهز بيانات آخر فاتورة اتفحصت، والخانات الناقصة بتفضل فاضية تكملها لما تسجّل رسميًا بنفسك.")
        _chk0 = st.session_state.get("_last_invoice_chk")
        if _chk0 is None or not len(_chk0):
            st.info("افحص فاتورة من فوق الأول، وبعدين صدّر جدول الجاهزية من هنا.")
        else:
            import io as _io2
            _exp = pd.DataFrame({
                "الصنف في الفاتورة": _chk0["الصنف في الفاتورة"],
                "الكمية": _chk0["الكمية"],
                "سعر الفاتورة": _chk0["سعر الفاتورة"],
                "المورد": _chk0["المورد"],
                "باركود GS1 (مطلوب للتتبع)": "",
                "رقم التشغيلة (مطلوب للتتبع)": "",
                "الرقم الضريبي للمورد (مطلوب للفاتورة الإلكترونية)": "",
            })
            _b2 = _io2.BytesIO()
            with pd.ExcelWriter(_b2, engine="openpyxl") as _xw2:
                _exp.to_excel(_xw2, index=False, sheet_name="جاهزية")
            st.download_button("⬇️ صدّر جدول الجاهزية (Excel)", _b2.getvalue(),
                               file_name="جاهزية-فاتورة-الكترونية-وتتبع.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               key="eta_export", use_container_width=True)
            st.caption("التصدير مسودة تجهيز محلية فقط. التسجيل الرسمي والإرسال قرارك أنت وبأرقام تسجيلك، ومش بيتم من التطبيق.")



if _page == "tools":
    page_chip("🧰", "أدوات إضافية", "التفاوض والصلاحيات وذاكرة المورد", "#0369a1", "#38bdf8")
    st.subheader("أدوات إضافية")
    think_ahead(page="tools")
    _tsub = st.pills("الأدوات", ["📡 رادار الأسعار", "💹 تغيرات الأسعار", "🧮 حاسبة التكلفة", "🤝 مساعد التفاوض", "📅 قريب الانتهاء", "💬 ذاكرة واتس", "📜 سجل الأسعار", "🏢 تصحيح الشركات"], default="📡 رادار الأسعار", key="tools_sub", label_visibility="collapsed")
    if _tsub == "📡 رادار الأسعار":
        st.subheader("📡 رادار الأسعار")
        st.caption("مؤشرات عامة مؤرخة بمصادرها + إشارات من سجلك أنت. دي معلومات للمتابعة، مش توقّع لسعر منتج معين ومش توصية شراء.")
        st.markdown("**🗞️ مؤشرات عامة**")
        for _mi in MACRO_INDICATORS:
            with st.container(border=True):
                st.markdown(f"**{_mi['title']}**")
                st.caption(f"📅 {_mi['date']}")
                st.markdown(_mi["body"])
                st.caption("المصادر: " + " · ".join(_mi["sources"]))
        st.markdown("**🧠 من سجلك**")
        _ld = int((st.session_state.get("mydata_settings") or {}).get("lead_days") or 7)
        _an = anticipation_notes(st.session_state.get("mydata_stock"), st.session_state.get("mydata_history"), st.session_state.get("mydata_batches"), lead_days=_ld)
        if _an:
            for _ic, _tx in _an:
                st.markdown(f"- {_ic} {_tx}")
        else:
            st.info("مفيش إشارات لسه — ارفع «بياناتي.xlsx» فيه المخزون والسجل والتشغيلات وشوف الإشارات هنا.")
        st.markdown("**✅ تغييرات أسعار معتمدة مسجلة**")
        st.caption("الزيادات أو التخفيضات الرسمية اللي اتأكدت — كل تغيير لازم يتسجل بمصدره وتاريخ سريانه، والتطبيق ميعرضش حاجة من غير مصدر.")
        _ap = fix_approved(st.session_state.get("mydata_approved"))
        if not _ap.empty:
            st.caption("الجدول أوسع من الشاشة: اسحبه يمين وشمال عشان تشوف باقي الأعمدة.")
            st.dataframe(_ap, use_container_width=True, hide_index=True)
        with st.expander("➕ سجّل تغيير معتمد", expanded=_ap.empty):
            with st.form("approved_add", clear_on_submit=True):
                _c1, _c2 = st.columns(2)
                _an_item = _c1.text_input("الصنف *", placeholder="اسم المستحضر زي ما هو معتمد")
                _an_pack = _c2.text_input("العبوة", placeholder="مثال: شريط 14 قرص")
                _c3, _c4 = st.columns(2)
                _an_old = _c3.number_input("السعر القديم", min_value=0.0, step=0.25, format="%.2f")
                _an_new = _c4.number_input("السعر الجديد *", min_value=0.0, step=0.25, format="%.2f")
                _c5, _c6 = st.columns(2)
                _an_date = _c5.date_input("تاريخ السريان *", value=None)
                _an_src = _c6.text_input("المصدر *", placeholder="منشور الشركة / إخطار التسعيرة / ...")
                if st.form_submit_button("احفظ التغيير المعتمد"):
                    _miss = []
                    if not str(_an_item).strip(): _miss.append("الصنف")
                    if not _an_new or float(_an_new) <= 0: _miss.append("السعر الجديد")
                    if _an_date is None: _miss.append("تاريخ السريان")
                    if not str(_an_src).strip(): _miss.append("المصدر")
                    if _miss:
                        st.error("ناقص: " + "، ".join(_miss) + " — التغيير المعتمد لازم يتسجل كامل بمصدره وتاريخه.")
                    else:
                        _row = {"الصنف": str(_an_item).strip(), "العبوة": str(_an_pack).strip(),
                                "السعر القديم": float(_an_old) if _an_old else None, "السعر الجديد": float(_an_new),
                                "تاريخ السريان": str(_an_date), "المصدر": str(_an_src).strip()}
                        st.session_state["mydata_approved"] = pd.concat([_ap, pd.DataFrame([_row])], ignore_index=True)
                        st.success("اتسجل ✅ — حمّل «بياناتي.xlsx» من صفحة التحميل علشان يتحفظ عندك على الجهاز.")
                        st.rerun()
    if _tsub == "💹 تغيرات الأسعار":
        _ph = st.session_state.get("mydata_history")
        if _ph is None or not len(_ph):
            st.info("لسه مفيش سجل أسعار. حدّث السجل من قسم ٣ (عروض الموردين) أو ارفع بياناتي.xlsx فيها سجل.")
        else:
            _ps = price_history_summary(_ph)
            _chg = _ps[_ps["عدد العروض"] > 1].copy()
            _chg = _chg[_chg["التغير عن السابق %"].notna() & (_chg["التغير عن السابق %"] != 0)]
            if not len(_chg):
                st.info("مفيش تغيّرات لسه: كل صنف اتسجّل بسعر واحد بس. لما يوصل عرض جديد بسعر مختلف هيظهر هنا.")
            else:
                _chg["_abs"] = _chg["التغير عن السابق %"].abs()
                _chg = _chg.sort_values("_abs", ascending=False).drop(columns="_abs").reset_index(drop=True)
                st.caption(f"{len(_chg)} صنف اتغيّر سعرهم عند الموردين، مرتّبين من أكبر تغيّر. الأسهم: ↑ زاد، ↓ قل.")
                _chg2 = table_actions(_chg[["المورد", "الصنف", "آخر صافي", "التغير عن السابق %", "الاتجاه", "آخر تاريخ", "عدد العروض"]], "chg_main", "تغيرات الأسعار")
                st.dataframe(_chg2, use_container_width=True)
    if _tsub == "🧮 حاسبة التكلفة":
        st.caption("بتحسب صافي تكلفة الوحدة الحقيقي من هيكل تسعير شركات الإنتاج والتوزيع: السعر ← الأساسي ← الخصم النقدي ← + الضريبة (بالجنيه أو نسبة من السعر بعد الخصم) ← − هامش الربح ← وفي الآخر البونص «10+2» بيوزّع التكلفة على الكمية المستلمة كلها. كل خطوة ظاهرة قدامك تراجعها بنفسك.")
        bc1, bc2, bc3 = st.columns(3)
        bp = bc1.number_input("سعر الوحدة", 0.0, 1000000.0, 0.0, key="nc_price")
        bbg = bc2.number_input("البونص: الكمية المدفوعة (مثلا 10)", 0, 10000, 0, key="nc_bg")
        bbf = bc3.number_input("البونص: المجاني (مثلا 2)", 0, 10000, 0, key="nc_bf")
        bn1, bn2 = st.columns(2)
        bn1.text_input("الصنف (للملء التلقائي من خصومات الأصناف)", key="nc_name")
        bretail = bn2.number_input("سعر الجمهور الرسمي (اختياري)", 0.0, 1000000.0, 0.0, key="nc_retail")
        def _fill_nc():
            _d = find_item_discount(st.session_state.get("nc_name"), st.session_state.get("mydata_discounts"))
            if _d:
                if pd.notna(_d.get("أساسي %")): st.session_state["nc_base"] = float(_d["أساسي %"])
                if pd.notna(_d.get("هامش جنيه")): st.session_state["nc_margin"] = float(_d["هامش جنيه"])
                st.session_state["_nc_note"] = f"اتملأ من خصومات الأصناف: {_d['الصنف']}" + (f" ({_d['الشركة']})." if _d.get("الشركة") else ".")
            else:
                st.session_state["_nc_note"] = "الصنف ده مش مسجل في خصومات الأصناف، أو له أكتر من تركيز فاكتب التركيز في الاسم."
        st.button("املأ الأساسي والهامش من خصومات الأصناف", key="btn_nc_fill", on_click=_fill_nc)
        if st.session_state.get("_nc_note"):
            st.caption(st.session_state.pop("_nc_note"))
        bc4, bc5 = st.columns(2)
        bb = bc4.number_input("الأساسي %", 0.0, 99.0, 0.0, key="nc_base")
        bcash = bc5.number_input("الخصم النقدي %", 0.0, 99.0, 0.0, key="nc_cash")
        bc6, bc7, bc8 = st.columns(3)
        bte = bc6.number_input("ضريبة بالجنيه", 0.0, 100000.0, 0.0, key="nc_taxe")
        btp = bc7.number_input("ضريبة %", 0.0, 99.0, 0.0, key="nc_taxp")
        bm = bc8.number_input("هامش ربح بالجنيه (بيقلل التكلفة)", 0.0, 100000.0, 0.0, key="nc_margin")
        if st.button("احسب صافي الوحدة", key="btn_nc") and bp > 0:
            _r = net_unit_cost(bp, bbg, bbf, bb, bcash, bte, btp, bm)
            st.table(pd.DataFrame(list(_r.items()), columns=["الخطوة", "القيمة"]))
            st.success(f"صافي تكلفة الوحدة: {_r['صافي الوحدة']:,.2f} جنيه — الخصم الفعلي الكلي: {_r['الخصم الفعلي الكلي %']}%")
            _w = discount_ceiling_warning(bb, bcash, pack_price=bp)
            if _w: st.warning(_w)
            if bretail > 0:
                _imp = implied_discount(bretail, _r["صافي الوحدة"])
                if _imp is not None:
                    st.caption(f"الخصم الضمني من سعر الجمهور: {_imp}% — تقدير محسوب من أرقامك أنت، مش رقم رسمي مؤكد، وبيشمل أثر الضريبة والهامش والبونص.")
        st.caption("لحساب كذا صنف مع بعض: املأ الجدول (دوس على آخر صف فاضي عشان تضيف):")
        _tpl = pd.DataFrame([{"الصنف": "", "السعر": 0.0, "بونص مدفوع": 0, "بونص مجاني": 0,
            "أساسي %": 0.0, "نقدي %": 0.0, "ضريبة جنيه": 0.0, "ضريبة %": 0.0, "هامش جنيه": 0.0,
            "سعر الجمهور": 0.0}])
        _edv = st.session_state.get("nc_editor_v", 0)
        _ned = st.data_editor(st.session_state.get("nc_bulk", _tpl), num_rows="dynamic", key=f"nc_editor_{_edv}", use_container_width=True)
        st.session_state["nc_bulk"] = _ned
        if st.button("املأ الأساسي والهامش من خصومات الأصناف", key="btn_nc_bulk_fill"):
            _filled = _ned.copy()
            _n = 0
            for _i, _x in _filled.iterrows():
                _d = find_item_discount(_x.get("الصنف"), st.session_state.get("mydata_discounts"))
                if _d is None: continue
                if pd.notna(_d.get("أساسي %")) and not _x.get("أساسي %"):
                    _filled.at[_i, "أساسي %"] = float(_d["أساسي %"]); _n += 1
                if pd.notna(_d.get("هامش جنيه")) and not _x.get("هامش جنيه"):
                    _filled.at[_i, "هامش جنيه"] = float(_d["هامش جنيه"]); _n += 1
            st.session_state["nc_bulk"] = _filled
            st.session_state["nc_editor_v"] = _edv + 1
            st.session_state["_nc_bulk_note"] = f"اتملأت {_n} خانة من خصومات الأصناف." if _n else "مفيش أصناف في الجدول مسجلة في خصومات الأصناف."
            st.rerun()
        if st.session_state.get("_nc_bulk_note"):
            st.caption(st.session_state.pop("_nc_bulk_note"))
        st.caption("الجدول أوسع من الشاشة: اسحبه يمين وشمال عشان تشوف باقي الأعمدة.")
        if st.button("احسب الجدول كله", key="btn_nc_bulk"):
            _rows = []
            for _, _x in _ned.iterrows():
                if not str(_x["الصنف"]).strip() or not _x["السعر"]:
                    continue
                _r = net_unit_cost(_x["السعر"], _x["بونص مدفوع"], _x["بونص مجاني"], _x["أساسي %"],
                    _x["نقدي %"], _x["ضريبة جنيه"], _x["ضريبة %"], _x["هامش جنيه"])
                _row = {"الصنف": str(_x["الصنف"]).strip(), "السعر": _x["السعر"],
                    "صافي الوحدة": _r["صافي الوحدة"], "الخصم الفعلي الكلي %": _r["الخصم الفعلي الكلي %"]}
                _imp = implied_discount(_x.get("سعر الجمهور"), _r["صافي الوحدة"])
                if _imp is not None: _row["خصم ضمني تقديري %"] = _imp
                if discount_ceiling_warning(_x["أساسي %"], _x["نقدي %"], pack_price=_x["السعر"]):
                    _row["تنبيه"] = "أعلى من الحد النظامي"
                _rows.append(_row)
            if _rows:
                _out = pd.DataFrame(_rows)
                st.dataframe(_out, use_container_width=True)
                _nb = io.BytesIO()
                with pd.ExcelWriter(_nb, engine="openpyxl") as w:
                    _out.to_excel(w, index=False)
                st.download_button("حمّل النتيجة إكسيل", _nb.getvalue(), "صافي_التكلفة.xlsx", key="dl_nc")
            else:
                st.info("املأ صف واحد على الأقل بصنف وسعر.")
    if _tsub == "🤝 مساعد التفاوض":
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
    if _tsub == "📅 قريب الانتهاء":
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
    if _tsub == "💬 ذاكرة واتس":
        st.caption("الصق الشات والتطبيق يطلّع لكل صنف: آخر سعر وخصم، وأفضل سعر شفناه قبل كده. مفيش حاجة بتتخزن.")
        supn = st.text_input("اسم المورد", key="sup_mem")
        st.caption("بيفهم تصدير واتساب من أندرويد وآيفون، والأرقام العربية، والرسائل اللي على أكتر من سطر.")
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
    if _tsub == "📜 سجل الأسعار":
        st.caption("السجل ملف بيتحفظ عندك إنت، مش في التطبيق: حمّله وخزّنه، وارفعه كل مرة ترجع تضيف شات جديد.")
        histf = st.file_uploader("ملف السجل من المرة اللي فاتت (price_history.xlsx، سيبه فاضي أول مرة)", type=["xlsx"], key="histf")
        suph = st.text_input("اسم المورد", key="sup_hist")
        st.caption("بيفهم تصدير واتساب من أندرويد وآيفون، والأرقام العربية، والرسائل اللي على أكتر من سطر.")
        chath = st.text_area("الصق شات واتس جديد للمورد", key="chat_hist", height=140,
            placeholder="26/11/2026, 10:00 ص - الحاج محمود: سرنجة 5مل - 113 جنيه خصم 6%")
        use_hist_sample = st.checkbox("جرّب بشات تجريبي (من غير لصق)", key="use_hist_sample")
        if st.button("حدّث السجل", key="btn_hist"):
            text = chath.strip() or (SAMPLE_CHAT if use_hist_sample else "")
            if not text and not histf:
                st.info("الصق شات جديد، أو فعّل الشات التجريبي، أو ارفع ملف السجل.")
            else:
                try:
                    hist = pd.read_excel(histf) if histf else st.session_state.get("mydata_history")
                    rows = parse_whatsapp_dated(text, suph.strip() or "المورد") if text else []
                    if text and not rows:
                        st.error("ما قدرتش أقرا أي أسعار من الشات. لازم كل سطر فيه سعر يكون معاه كلمة جنيه.")
                    else:
                        before = len(hist) if hist is not None else 0
                        merged = update_price_history(hist, rows)
                        st.session_state["mydata_history"] = merged
                        st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
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



if _page == "tools" and st.session_state.get("tools_sub") == "🏢 تصحيح الشركات":
    st.subheader("تصحيحات الشركات (قرارك بيتحفظ في ملفك)")
    st.caption("لما شركة صنف في شيتك تختلف عن القاموس العام، التطبيق مش بيخمن: بيسألك هنا مرة واحدة، وقرارك بيتحفظ في بياناتي.xlsx وبيحترم في كل الشاشات بعد كده.")
    if st.session_state.get("mydata_stock") is not None and st.session_state.get("mydata_public") is not None and len(st.session_state.get("mydata_public")):
        if "pub_index" not in st.session_state:
            st.session_state["pub_index"] = public_price_index(st.session_state["mydata_public"])
        _mhc = margin_hunter(st.session_state["mydata_stock"], st.session_state["pub_index"], 1.0, cofix=st.session_state.get("mydata_cofix"))
        _confs = _mhc[_mhc["ملاحظة الشركة"].astype(str).str.startswith("⚠")] if not _mhc.empty else _mhc
        if len(_confs):
            st.write(f"**{len(_confs)} صنف محتاجين قرارك:**")
            for _ci, _r in _confs.head(30).iterrows():
                with st.container(border=True):
                    st.markdown(f"**{_r['الصنف']}**")
                    st.caption(f"في شيتك: {_r['الشركة'] or '—'}  |  في القاموس: {_r['الشركة (القاموس)'] or '—'}")
                    _opts = [o for o in [f"شيتك: {_r['الشركة']}" if str(_r['الشركة']).strip() else None,
                                       f"القاموس: {_r['الشركة (القاموس)']}" if str(_r['الشركة (القاموس)']).strip() else None] if o]
                    _ch = st.pills("اعتمد", _opts, key=f"cofix_ch_{_ci}", label_visibility="collapsed")
                    if st.button("احفظ التصحيح", key=f"cofix_sv_{_ci}", use_container_width=True):
                        if _ch:
                            _co = _r["الشركة"] if _ch.startswith("شيتك") else _r["الشركة (القاموس)"]
                            st.session_state["mydata_cofix"] = cofix_upsert(st.session_state.get("mydata_cofix"), _r["الصنف"], _co)
                            st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
                            st.success(f"اتحفظ: {_r['الصنف']} ← {_co}. حمّل بياناتي.xlsx من صفحة التحميل عشان يفضل محفوظ عندك.")
                            st.rerun()
                        else:
                            st.warning("اختار الأول: شركة شيتك ولا شركة القاموس.")
        else:
            st.success("مفيش تعارضات شركات محتاجة قرار دلوقتي. ✅")
    else:
        st.info("محتاج المخزون وقائمة أسعار الجمهور في بياناتي.xlsx علشان نطلّع التعارضات.")
    _cf0 = fix_cofix(st.session_state.get("mydata_cofix"))
    if len(_cf0):
        st.write("**تصحيحاتك المحفوظة:**")
        _cfe = st.data_editor(_cf0, num_rows="dynamic", key="cofix_editor", use_container_width=True)
        if st.button("احفظ تعديلات الجدول", key="cofix_tbl_save"):
            st.session_state["mydata_cofix"] = fix_cofix(_cfe)
            st.session_state["md_salt"] = st.session_state.get("md_salt", 0) + 1
            st.success("اتحفظت التعديلات. حمّل بياناتي.xlsx من صفحة التحميل.")

if _page == "search":
    page_chip("🔎", "البحث الموحد", "أي صنف: سعره وبدائله وبياناته", "#be185d", "#f472b6")
    st.subheader("البحث الموحد والمثائل والبدائل")
    st.caption("ابحث بالاسم (عربي أو إنجليزي) أو الباركود: بيانات الصنف من قاموس عام (eg-drugs - CC BY 4.0)، وسعر الجمهور الرسمي من ملفك، ومرجع فارما أوفرسيز من حسابك، والمثائل بنفس المادة الفعالة. معلومات عامة مش نصيحة طبية ولا جرعات، واختيار أي بديل قرار مهني للصيدلي/الطبيب.")

    @st.cache_data
    def _load_full_dict():
        import os as _os
        try:
            import glob as _glob
            _d = _os.path.dirname(_os.path.abspath(__file__))
            _c = sorted(_glob.glob(_os.path.join(_d, "*dict_full*.csv")), key=_os.path.getsize, reverse=True)
            return pd.read_csv(_c[0], dtype=str).fillna("") if _c else None
        except Exception: return None
    _dfd = _load_full_dict()
    if _dfd is not None and "aidx" not in st.session_state:
        st.session_state["aidx"] = active_ingredient_index(_dfd)
        st.session_state["dict_cache"] = dict_search_cache(_dfd)
    def _show_unified_item(_i):
        """Render one dictionary item's full unified-search card (prices, reference, equivalents)."""
        _row = _dfd.iloc[_i]
        if str(_row['arabic']).strip():
            st.markdown(f"### {_row['arabic']}")
            st.caption(str(_row['name']))
        else:
            st.markdown(f"### {_row['name']}")
        _uco = user_company_override(str(_row['arabic']) or str(_row['name']))
        if _uco:
            st.caption(f"الشركة: {_uco['company']} (✅ {_uco['note']}) | المادة الفعالة: {_row['active'] or '—'} | الباركود: {_row['barcode'] or '—'}")
        else:
            st.caption(f"الشركة (من القاموس العام): {company_ar(_row['company']) or '—'} | المادة الفعالة: {_row['active'] or '—'} | الباركود: {_row['barcode'] or '—'}")
        if str(_row['uses']).strip():
            st.caption("الاستخدام (معلومة عامة من مصدر عام - مش نصيحة طبية): " + str(_row['uses']))
        _pub = st.session_state.get("mydata_public")
        if _pub is not None and len(_pub):
            if "pub_index" not in st.session_state:
                st.session_state["pub_index"] = public_price_index(_pub)
            _pp = find_public_row(_row['name'], st.session_state["pub_index"])
            if _pp and _pp[0]:
                st.write(f"سعر الجمهور الرسمي: **{_pp[0]} ج** ({_pp[1]})")
        _ref = st.session_state.get("mydata_reference")
        if _ref is not None and len(_ref):
            if "ref_search" not in st.session_state:
                st.session_state["ref_search"] = reference_search_cache(_ref)
                st.session_state["ref_index"] = reference_index(_ref)
            _h = find_reference_fast(_row['name'], st.session_state["ref_search"])
            if _h:
                st.write("مرجع فارما أوفرسيز (من حسابك):")
                st.dataframe(pd.DataFrame([{k: _h[k] for k in ("الصنف","الفئة","الشركة/المورد","سعر الجمهور","سعر الصيدلي","الخصم الضمني %","الأساسي %","ثقة الأساسي","الهامش جنيه (بعد الأساسي)","الضريبة (تقديري)")}]), use_container_width=True, hide_index=True)
                st.caption("الأساسي والهامش والضريبة تقديرية إلا لو مكتوب «مؤكد من الموقع» في عمود الثقة أو كتبت قيمة في عمودي التأكيد في ملفك.")
            else:
                st.caption("الصنف ده مش متسعّر في مرجع فارما أوفرسيز.")
        think_ahead(context_item=str(_row['name']))
        _idf = st.session_state.get("mydata_item_disc")
        if _idf is not None and len(_idf):
            _b = item_base(_row['name'], _idf)
            if _b is not None:
                st.caption(f"أساسي متعلم من فواتيرك وعروضك: {_b}% (تقديري).")
        _eq = [e for e in equivalents_for(_i, _dfd, st.session_state["aidx"]) if not e.pop("same_item")]
        if _eq:
            st.write(f"**مثائل وبدائل بنفس المادة الفعالة ({_row['active']}):**")
            _rows = []
            for e in _eq:
                r = {"الصنف": e["name"], "عربي": e["arabic"], "الشركة": company_ar(e["company"])}
                if _pub is not None and len(_pub):
                    _v = find_public_price(e["name"], st.session_state["pub_index"])
                    r["سعر الجمهور"] = str(_v) if _v else ""
                if _ref is not None and len(_ref):
                    _h2 = find_reference(e["name"], st.session_state["ref_index"])
                    r["فارما أوفرسيز صيدلي"] = str(_h2["سعر الصيدلي"]) if _h2 and _h2["سعر الصيدلي"] is not None else ""
                _rows.append(r)
            _eqd = pd.DataFrame(_rows)
            if "سعر الجمهور" in _eqd.columns:
                _eqd["_s"] = pd.to_numeric(_eqd["سعر الجمهور"], errors="coerce")
                _eqd = _eqd.sort_values("_s", na_position="last").drop(columns="_s")
            st.dataframe(_eqd, use_container_width=True, hide_index=True)
            st.caption("الأرخص بالسعر الرسمي في أول الجدول. عرض المثائل معلومة سعرية فقط، مش توصية بتغيير العلاج. الجدول أوسع من الشاشة: اسحبه يمين وشمال.")

    if _dfd is not None:
        if "dict_opts" not in st.session_state:
            _ar = _dfd['arabic'].astype(str)
            _nm = _dfd['name'].astype(str)
            _lbl = (_ar + ' | ' + _nm).where(_ar.str.strip() != '', _nm).tolist()
            _ord = sorted(range(len(_lbl)), key=lambda i: (0 if _lbl[i][:1] >= '\u0600' else 1, _lbl[i]))
            st.session_state["dict_opts"] = _lbl
            st.session_state["dict_ord"] = _ord
        _lbls = st.session_state["dict_opts"]
        _pick = st.selectbox("اختار الصنف من القاموس - اكتب أي جزء من الاسم (عربي أو إنجليزي) والنتايج بتظهر تحت الخانة على طول",
                             st.session_state["dict_ord"], format_func=lambda i: _lbls[i],
                             index=None, placeholder="اكتب واختار...", key="unified_pick")
        st.caption("مش لاقي الصنف في القايمة؟ ابحث بالباركود أو الاسم من تحت (ولو كتبت هنا، امسحها لو رجعت تختار من القايمة).")
        _q = st.text_input("باركود أو اسم", key="unified_q", placeholder="مثال: 6221000003295")
        if _q:
            _i = dict_lookup_fast(_q, _dfd, st.session_state.get("dict_cache")) or dict_lookup(_q, _dfd)
            if _i is None:
                st.warning("الصنف مش في القاموس العام. جرّب اسم تاني أو باركود.")
            else:
                _show_unified_item(_i)
        elif _pick is not None:
            _show_unified_item(_pick)

if _page == "download":
    page_chip("⬇️", "تحميل بياناتك", "حمّل بياناتي.xlsx المحدّث", "#475569", "#94a3b8")
    think_ahead(page="download")
    def _pub_out():
        """أسعار الجمهور sheet for download, with per-company estimated pharmacy price
    columns refreshed from the current learned bases (estimates, marked as such)."""
        _p = st.session_state.get("mydata_public")
        if _p is None or not len(_p): return _p
        _p = _p.copy()
        _idf4 = st.session_state.get("mydata_item_disc")
        _p["سعر الصيدلي التقديري (متعلم)"] = _p.apply(lambda r: est_pharmacy_price(r["سعر الجمهور"], item_base(r["الصنف"], _idf4)), axis=1)
        def _g4(r):
            if item_base(r["الصنف"], _idf4) is not None: return None
            return est_pharmacy_price(r["سعر الجمهور"], company_median_base(r["الشركة"], _idf4))
        _p["تخمين تقريبي (متوسط الشركة)"] = _p.apply(_g4, axis=1)
        return _p

    st.subheader("حمّل بياناتك المحدّثة")
    st.caption("ده الملف اللي ترفعه في أول المرة الجاية: فيه الروابط وسجل الأسعار وخصومات الأصناف والموردين وإعداداتك زي ما هي دلوقتي" + ("، ومعاهم قايمة أسعار الجمهور الرسمية." if st.session_state.get("mydata_public") is not None else "."))
    _idf_dl = st.session_state.get("mydata_item_disc")
    def _ln(x):
        return 0 if x is None else len(x)
    _fp = (st.session_state.get("md_salt", 0),
           _ln(st.session_state.get("manual_map")),
           _ln(st.session_state.get("mydata_history")),
           _ln(st.session_state.get("mydata_suppliers")),
           _ln(st.session_state.get("mydata_discounts")),
           _ln(st.session_state.get("mydata_public")),
           _ln(_idf_dl),
           _ln(st.session_state.get("mydata_reference")),
           _ln(st.session_state.get("mydata_stock")),
           _ln(st.session_state.get("mydata_batches")),
           _ln(st.session_state.get("mydata_returns")),
           _ln(st.session_state.get("mydata_cofix")),
           _ln(st.session_state.get("mydata_approved")),
           _ln(st.session_state.get("mydata_orders")),
           _ln(st.session_state.get("mydata_announcements")),
           _ln(st.session_state.get("mydata_controlled")),
           repr(sorted((st.session_state.get("mydata_settings") or {}).items())))
    if st.session_state.get("mydata_dl_fp") != _fp:
        st.session_state["mydata_dl_bytes"] = build_my_data(
            links=st.session_state.get("manual_map"),
            history=st.session_state.get("mydata_history"),
            suppliers=st.session_state.get("mydata_suppliers"),
            discounts=st.session_state.get("mydata_discounts"),
            public=_pub_out(),
            public_src=st.session_state.get("mydata_public_src"),
            item_disc=_idf_dl,
            reference=st.session_state.get("mydata_reference"),
            stock=st.session_state.get("mydata_stock"),
            batches=st.session_state.get("mydata_batches"),
            returns=st.session_state.get("mydata_returns"),
            cofix=st.session_state.get("mydata_cofix"),
            approved=st.session_state.get("mydata_approved"),
            orders=st.session_state.get("mydata_orders"),
            announcements=st.session_state.get("mydata_announcements"),
            controlled=st.session_state.get("mydata_controlled"),
            settings={"buyer": st.session_state.get("obuyer_in") or st.session_state.get("buyer_in") or "",
                      "cover_days": st.session_state.get("days_in", 45),
                      "min_months": st.session_state.get("months_in", 6),
                      "lead_days": st.session_state.get("lead_in", 7),
                      "safety_days": st.session_state.get("safety_in", 7)})
        st.session_state["mydata_dl_fp"] = _fp
    _dl = st.session_state["mydata_dl_bytes"]
    st.download_button("حمّل بياناتي.xlsx المحدّث (خزّنه عندك)", _dl, "بياناتي.xlsx")
