import streamlit as st
import csv
import os

CSV_FILE = 'festival_ledger.csv'
FIELDNAMES = ['Entry_ID', 'Festival_Name', 'Person_Name', 'Amount_INR', 'Type']
DEFAULT_FESTIVALS = ["Ganesh Utsav", "Makar Sankranti", "Janmashtami", "Navratri","Holi", "Diwali"]

def load_data():
    rows = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
    return rows

def save_all_data(rows):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

def get_next_id(rows):
    if not rows: return "ENT001"
    max_num = 0
    for r in rows:
        try:
            num = int(r['Entry_ID'].replace('ENT',''))
            if num > max_num: max_num = num
        except: pass
    return f"ENT{max_num+1:03d}"

def get_all_festivals(data_rows):
    from_file = list(set([row['Festival_Name'] for row in data_rows])) if data_rows else []
    combined = list(set(DEFAULT_FESTIVALS + from_file))
    combined.sort()
    return combined

data_rows = load_data()
all_festivals_list = get_all_festivals(data_rows)
if 'new_fest' in st.session_state and st.session_state['new_fest'] not in all_festivals_list:
    all_festivals_list.append(st.session_state['new_fest'])
    all_festivals_list.sort()

# --- DESIGN CSS (No Pandas Needed) ---
st.set_page_config(page_title="Festival Ledger", layout="wide", page_icon="🪔")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.stApp { background: #FFF8F0; }
.main-title { font-size: 42px; font-weight: 800; color: #5D2A00; text-align: center; }
.sub-title { text-align: center; color: #8D5B2C; font-size: 16px; margin-bottom: 25px; }
.metric-card {
    background: white; padding: 20px; border-radius: 18px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.06); border-left: 6px solid; text-align: left;
}
.metric-card.donation { border-color: #2ECC71; }
.metric-card.expense { border-color: #E74C3C; }
.metric-card.balance { border-color: #F39C12; }
.metric-label { font-size: 13px; color: #888; font-weight: 600; letter-spacing: 1px; }
.metric-value { font-size: 28px; font-weight: 800; color: #2C3E50; margin-top: 5px; }
.stTabs [data-baseweb="tab-list"] { gap: 10px; }
.stTabs [data-baseweb="tab"] { background: white; border-radius: 10px; padding: 10px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); font-weight: 600; }
.stTabs [aria-selected="true"] { background: #FF6B00!important; color: white!important; }
.stButton>button { border-radius: 12px; font-weight: 700; height: 48px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🪔 Festival Financial Dashboard</p>', unsafe_allow_html=True)
# st.markdown('<p class="sub-title">Aapke sabhi festivals ka hisab-kitab ek jagah</p>', unsafe_allow_html=True)

# --- CALCULATION ---
total_donation = sum(int(r['Amount_INR']) for r in data_rows if r['Type']=='Donation' and r['Amount_INR'].isdigit())
total_expense = sum(int(r['Amount_INR']) for r in data_rows if r['Type']=='Expense' and r['Amount_INR'].isdigit())
net_balance = total_donation - total_expense
balance_color = "#2ECC71" if net_balance >=0 else "#E74C3C"

# --- METRIC CARDS ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card donation"><div class="metric-label">💰 TOTAL DONATION</div><div class="metric-value">₹{total_donation:,}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card expense"><div class="metric-label">💸 TOTAL EXPENSE</div><div class="metric-value">₹{total_expense:,}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card balance"><div class="metric-label">📊 NET BALANCE</div><div class="metric-value" style="color:{balance_color}">₹{net_balance:,}</div></div>', unsafe_allow_html=True)

st.write("")

# --- SIMPLE CHART WITHOUT PANDAS ---
if data_rows:
    st.markdown("#### 📊 Festival Hisab")
    # Festival wise total nikalo
    fest_totals = {}
    for r in data_rows:
        if not r['Amount_INR'].isdigit(): continue
        fest = r['Festival_Name']
        amt = int(r['Amount_INR'])
        if fest not in fest_totals:
            fest_totals[fest] = {'Donation': 0, 'Expense': 0}
        fest_totals[fest][r['Type']] += amt

    # Chart ke liye data banao
    chart_data = []
    for fest, vals in fest_totals.items():
        chart_data.append({"Festival": fest, "Donation": vals['Donation'], "Expense": vals['Expense']})

    st.bar_chart(chart_data, x="Festival", y=["Donation", "Expense"], color=["#2ECC71", "#E74C3C"])

# --- ADD FESTIVAL ---
with st.expander("➕ Add New Festival"):
    col1, col2 = st.columns([3,1])
    with col1:
        new_fest_name = st.text_input("Festival ka Naam", placeholder="Ex: Durga Puja", label_visibility="collapsed")
    with col2:
        if st.button("Add", width='stretch'):
            if new_fest_name and new_fest_name not in all_festivals_list:
                st.session_state['new_fest'] = new_fest_name.strip()
                st.success(f"'{new_fest_name}' add ho gaya!")
                st.rerun()
            else:
                st.warning("Please Enter Name")

# --- TABS ---
tab_read, tab_create, tab_update, tab_delete = st.tabs(["📖 Read Data", "➕ Create Entry", "✏️ Update", "🗑️ Delete"])

with tab_read:
    st.sidebar.markdown("🎯 Filter")
    selected_fest = st.sidebar.multiselect("Choose Festival", options=all_festivals_list, default=all_festivals_list)
    display_rows = [row for row in data_rows if row['Festival_Name'] in selected_fest] if selected_fest else data_rows
    if display_rows:
        st.dataframe(display_rows, width='stretch', hide_index=True)
    else:
        st.info("No Data")

with tab_create:
    st.markdown("Enter Your Data")
    with st.form("create_entry_form", clear_on_submit=True):
        festival_options = all_festivals_list + ["➕ Add New Festival..."]
        f_name_selected = st.selectbox("Select Festival", festival_options)
        final_f_name = f_name_selected
        if f_name_selected == "➕ Add New Festival...":
            final_f_name = st.text_input("Add New Festival...")

        c1, c2 = st.columns(2)
        with c1: p_name = st.text_input("Person / Vendor Name")
        with c2: amount = st.number_input("Amount INR", min_value=0, step=100)
        type = st.radio("Type", ["Donation", "Expense"], horizontal=True)

        if st.form_submit_button("💾 Save", width='stretch'):
            if not final_f_name or not p_name:
                st.error("Add Festival and Name!")
            else:
                new_entry = {'Entry_ID': get_next_id(data_rows), 'Festival_Name': final_f_name.strip(), 'Person_Name': p_name, 'Amount_INR': str(amount), 'Type': type}
                data_rows.append(new_entry)
                save_all_data(data_rows)
                st.success(f"✅ {new_entry['Entry_ID']} Saved! Festival: {final_f_name}")
                st.rerun()

with tab_update:
    if data_rows:
        select_id = st.selectbox("Select Entry ID", [row['Entry_ID'] for row in data_rows])
        target_index = next((i for i, r in enumerate(data_rows) if r['Entry_ID'] == select_id), None)
        if target_index is not None:
            old = data_rows[target_index]
            with st.form("update_form"):
                try: old_index = all_festivals_list.index(old['Festival_Name'])
                except: old_index = 0
                u_fest = st.selectbox("Festival", all_festivals_list, index=old_index)
                u_name = st.text_input("Name", value=old['Person_Name'])
                u_amount = st.number_input("Amount", value=int(old['Amount_INR']) if old['Amount_INR'].isdigit() else 0)
                u_type = st.radio("Type", ["Donation", "Expense"], index=["Donation", "Expense"].index(old['Type']), horizontal=True)
                if st.form_submit_button("Update", width='stretch'):
                    data_rows[target_index].update({'Festival_Name': u_fest, 'Person_Name': u_name, 'Amount_INR': str(u_amount), 'Type': u_type})
                    save_all_data(data_rows)
                    st.success("Updated!")
                    st.rerun()

with tab_delete:
    if data_rows:
        del_id = st.selectbox("Select Delete ID", [row['Entry_ID'] for row in data_rows], key="del")
        st.warning(f"Do You Want to Delete Entry ID {del_id} ?")
        if st.button("🗑️Delete ", type="primary", width='stretch'):
            data_rows = [r for r in data_rows if r['Entry_ID']!= del_id]
            save_all_data(data_rows)
            st.error(f"{del_id} Deleted")
            st.rerun()