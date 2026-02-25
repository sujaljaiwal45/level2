import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
INVENTORY_FILE = "amar_store_inventory.csv"
CATEGORIES_FILE = "amar_store_categories.csv"
HISTORY_FILE = "amar_store_history.csv"
PAGE_TITLE = "Amar Store: Safety Inventory"

# Default categories
DEFAULT_CATEGORIES = ["Boiler Suits", "Safety Shoes", "Helmets", "Gloves", "Safety Jackets", "Face Shields"]

# --- DATA FUNCTIONS ---

def load_inventory():
    """Load inventory from CSV."""
    if not os.path.exists(INVENTORY_FILE):
        return []
    try:
        df = pd.read_csv(INVENTORY_FILE)
        return df.to_dict('records')
    except Exception:
        return []

def save_inventory(data):
    """Save inventory to CSV."""
    if not data:
        pd.DataFrame(columns=["id", "category", "name", "size", "stock", "last_updated"]).to_csv(INVENTORY_FILE, index=False)
    else:
        df = pd.DataFrame(data)
        df.to_csv(INVENTORY_FILE, index=False)

def load_categories():
    """Load categories from CSV."""
    if not os.path.exists(CATEGORIES_FILE):
        return DEFAULT_CATEGORIES
    try:
        df = pd.read_csv(CATEGORIES_FILE)
        if 'category_name' in df.columns:
            return df['category_name'].tolist()
        return DEFAULT_CATEGORIES
    except:
        return DEFAULT_CATEGORIES

def save_categories(data_list):
    """Save categories to CSV."""
    df = pd.DataFrame(data_list, columns=["category_name"])
    df.to_csv(CATEGORIES_FILE, index=False)

def log_history(product_name, size, action, change_qty, current_stock):
    """
    Logs an action to the history CSV.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {
        "timestamp": timestamp,
        "product_name": product_name,
        "size": size,
        "action": action,
        "change": change_qty,
        "final_stock": current_stock
    }
    
    if os.path.exists(HISTORY_FILE):
        try:
            df = pd.read_csv(HISTORY_FILE)
            new_df = pd.DataFrame([new_entry])
            df = pd.concat([df, new_df], ignore_index=True)
        except:
            df = pd.DataFrame([new_entry])
    else:
        df = pd.DataFrame([new_entry])
        
    df.to_csv(HISTORY_FILE, index=False)

# --- APP LAYOUT ---
st.set_page_config(page_title=PAGE_TITLE, layout="wide")
st.title(f"🦺 {PAGE_TITLE}")

# Initialize Session State
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_inventory()

if 'categories' not in st.session_state:
    st.session_state.categories = load_categories()

# --- NAVIGATION ---
page = st.sidebar.radio("Go to", ["📦 Inventory Dashboard", "📜 History Log", "⚙️ Manage Categories"])
st.sidebar.divider()

# ==========================================
# PAGE 1: INVENTORY DASHBOARD
# ==========================================
if page == "📦 Inventory Dashboard":
    
    # --- BIG PICTURE SUMMARY (Top of Page) ---
    st.subheader("📊 Shop Health")
    df_summary = pd.DataFrame(st.session_state.inventory)
    
    if not df_summary.empty:
        total_items = df_summary['stock'].sum()
        low_stock_count = len(df_summary[df_summary['stock'] < 5])
        
        sc1, sc2 = st.columns(2)
        with sc1:
            st.info(f"📦 Total Items in Stock: **{total_items}**")
        with sc2:
            if low_stock_count > 0:
                st.error(f"⚠️ Low Stock Alerts: **{low_stock_count} variants** are under 5!")
            else:
                st.success("✅ All stock levels are healthy!")
        st.divider()
    else:
        st.info("Start adding products to see your shop health here.")

    # --- SIDEBAR: ADD PRODUCTS ---
    with st.sidebar:
        st.header("Manage Stock Items")
        tab1, tab2 = st.tabs(["🆕 New Product", "➕ Add Variant"])
        
        # TAB 1: CREATE NEW PRODUCT
        with tab1:
            with st.form("add_new_item_form", clear_on_submit=True):
                new_cat = st.selectbox("Category", st.session_state.categories) if st.session_state.categories else st.selectbox("Category", ["None"])
                new_name = st.text_input("Name (e.g. TC Boiler Suit)")
                sizes_input = st.text_input("Sizes (e.g. S, M, L)")
                initial_stock = st.number_input("Initial Stock", value=0, min_value=0, step=1)
                
                if st.form_submit_button("Create Product"):
                    if new_name and sizes_input:
                        sizes_list = [s.strip() for s in sizes_input.split(',') if s.strip()]
                        count = 0
                        for size in sizes_list:
                            if not any(i['name'].lower() == new_name.lower() and i['size'].lower() == size.lower() for i in st.session_state.inventory):
                                new_item = {
                                    "id": int(datetime.now().timestamp() * 1000) + count,
                                    "category": new_cat, "name": new_name, "size": size,
                                    "stock": initial_stock, "last_updated": datetime.now().strftime("%Y-%m-%d")
                                }
                                st.session_state.inventory.append(new_item)
                                log_history(new_name, size, "Created", initial_stock, initial_stock)
                                count += 1
                        
                        save_inventory(st.session_state.inventory)
                        st.success(f"Created {count} variants")
                        st.rerun()

        # TAB 2: ADD VARIANT
        with tab2:
            existing_names = sorted(list(set(item['name'] for item in st.session_state.inventory)))
            if existing_names:
                with st.form("add_var_form", clear_on_submit=True):
                    sel_prod = st.selectbox("Product", existing_names)
                    new_sizes = st.text_input("New Sizes")
                    var_stock = st.number_input("Stock", value=0)
                    
                    if st.form_submit_button("Add Variant"):
                        if sel_prod and new_sizes:
                            parent_cat = next((i['category'] for i in st.session_state.inventory if i['name'] == sel_prod), "Uncategorized")
                            sizes_list = [s.strip() for s in new_sizes.split(',') if s.strip()]
                            count = 0
                            for size in sizes_list:
                                if not any(i['name'] == sel_prod and i['size'].lower() == size.lower() for i in st.session_state.inventory):
                                    new_item = {
                                        "id": int(datetime.now().timestamp() * 1000) + count,
                                        "category": parent_cat, "name": sel_prod, "size": size,
                                        "stock": var_stock, "last_updated": datetime.now().strftime("%Y-%m-%d")
                                    }
                                    st.session_state.inventory.append(new_item)
                                    log_history(sel_prod, size, "Created Variant", var_stock, var_stock)
                                    count += 1
                            save_inventory(st.session_state.inventory)
                            st.success(f"Added {count} sizes")
                            st.rerun()

    # --- MAIN DASHBOARD ---
    search_query = st.text_input("🔍 Search Product...", "")
    df = pd.DataFrame(st.session_state.inventory)

    if not df.empty:
        if search_query:
            mask = df.apply(lambda x: search_query.lower() in str(x).lower(), axis=1)
            df = df[mask]

        for cat in df['category'].unique():
            st.markdown(f"### 📂 {cat}")
            cat_df = df[df['category'] == cat]
            
            for product_name in cat_df['name'].unique():
                p_vars = cat_df[cat_df['name'] == product_name].sort_values('id')
                total = p_vars['stock'].sum()
                
                with st.expander(f"**{product_name}** (Total: {total})"):
                    for _, row in p_vars.iterrows():
                        c1, c2, c3, c4 = st.columns([2, 1, 2, 1])
                        with c1: st.markdown(f"##### Size: {row['size']}")
                        with c2: 
                            color = "red" if row['stock'] < 5 else "green"
                            st.markdown(f"<span style='color:{color}; font-size:20px; font-weight:bold'>{row['stock']}</span>", unsafe_allow_html=True)
                        
                        with c3:
                            b1, b2 = st.columns(2)
                            if b1.button("➖", key=f"dec_{row['id']}"):
                                for i in st.session_state.inventory:
                                    if i['id'] == row['id'] and i['stock'] > 0:
                                        i['stock'] -= 1
                                        log_history(row['name'], row['size'], "Stock Out", -1, i['stock'])
                                save_inventory(st.session_state.inventory)
                                st.rerun()
                            
                            if b2.button("➕", key=f"inc_{row['id']}"):
                                for i in st.session_state.inventory:
                                    if i['id'] == row['id']:
                                        i['stock'] += 1
                                        log_history(row['name'], row['size'], "Stock In", 1, i['stock'])
                                save_inventory(st.session_state.inventory)
                                st.rerun()
                        
                        with c4:
                            if st.button("🗑️", key=f"del_{row['id']}"):
                                st.session_state.inventory = [i for i in st.session_state.inventory if i['id'] != row['id']]
                                log_history(row['name'], row['size'], "Deleted Variant", 0, 0)
                                save_inventory(st.session_state.inventory)
                                st.rerun()
                    
                    if st.button(f"🚨 Delete '{product_name}'", key=f"del_all_{product_name}"):
                        st.session_state.inventory = [i for i in st.session_state.inventory if i['name'] != product_name]
                        log_history(product_name, "ALL", "Deleted Product", 0, 0)
                        save_inventory(st.session_state.inventory)
                        st.rerun()
            st.divider()

# ==========================================
# PAGE 2: HISTORY LOG
# ==========================================
elif page == "📜 History Log":
    st.header("Transaction History")
    
    if os.path.exists(HISTORY_FILE):
        try:
            df_hist = pd.read_csv(HISTORY_FILE)
            if 'timestamp' in df_hist.columns:
                df_hist = df_hist.sort_values(by='timestamp', ascending=False)
            
            search_hist = st.text_input("Search History (Product Name or Action)", "")
            if search_hist:
                mask = df_hist.apply(lambda x: search_hist.lower() in str(x).lower(), axis=1)
                df_hist = df_hist[mask]
                
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
            
            with open(HISTORY_FILE, "rb") as f:
                st.download_button("📥 Download History CSV", f, file_name="amar_store_history.csv")
                
        except Exception as e:
            st.error(f"Error reading history: {e}")
    else:
        st.info("No history found yet.")

# ==========================================
# PAGE 3: MANAGE CATEGORIES
# ==========================================
elif page == "⚙️ Manage Categories":
    st.header("Manage Categories")
    
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        new_cat = c1.text_input("New Category", label_visibility="collapsed")
        if c2.button("Add"):
            if new_cat and new_cat not in st.session_state.categories:
                st.session_state.categories.append(new_cat)
                save_categories(st.session_state.categories)
                st.success("Added!")
                st.rerun()
    
    for cat in st.session_state.categories:
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"**📂 {cat}**")
        if c2.button("Delete", key=f"dcat_{cat}"):
            st.session_state.categories.remove(cat)
            save_categories(st.session_state.categories)
            st.session_state.inventory = [i for i in st.session_state.inventory if i['category'] != cat]
            save_inventory(st.session_state.inventory)
            st.rerun()
        st.divider()