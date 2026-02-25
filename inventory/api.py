import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
INVENTORY_FILE = "amar_store_inventory.csv"
CATEGORIES_FILE = "amar_store_categories.csv"
PAGE_TITLE = "Amar Store: Safety Inventory"

# Default categories if file doesn't exist
DEFAULT_CATEGORIES = [
    "Boiler Suits", 
    "Safety Shoes", 
    "Helmets", 
    "Gloves", 
    "Safety Jackets", 
    "Face Shields"
]

# --- DATA FUNCTIONS (CSV VERSION) ---

def load_inventory():
    """Load inventory from CSV to a List of Dictionaries."""
    if not os.path.exists(INVENTORY_FILE):
        return []
    try:
        # Read CSV and convert to list of dicts
        df = pd.read_csv(INVENTORY_FILE)
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error loading inventory: {e}")
        return []

def save_inventory(data):
    """Save List of Dictionaries to CSV."""
    if not data:
        # Save an empty CSV with headers if list is empty
        pd.DataFrame(columns=["id", "category", "name", "size", "stock", "last_updated"]).to_csv(INVENTORY_FILE, index=False)
    else:
        df = pd.DataFrame(data)
        df.to_csv(INVENTORY_FILE, index=False)

def load_categories():
    """Load categories from CSV to a simple List."""
    if not os.path.exists(CATEGORIES_FILE):
        return DEFAULT_CATEGORIES
    try:
        df = pd.read_csv(CATEGORIES_FILE)
        # We expect a column named 'category_name'
        if 'category_name' in df.columns:
            return df['category_name'].tolist()
        return DEFAULT_CATEGORIES
    except:
        return DEFAULT_CATEGORIES

def save_categories(data_list):
    """Save List of Strings to CSV."""
    # Convert list of strings to DataFrame
    df = pd.DataFrame(data_list, columns=["category_name"])
    df.to_csv(CATEGORIES_FILE, index=False)


# --- APP LAYOUT ---
st.set_page_config(page_title=PAGE_TITLE, layout="wide")
st.title(f"🛡️ {PAGE_TITLE}")

# Initialize Session State
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_inventory()

if 'categories' not in st.session_state:
    st.session_state.categories = load_categories()

# --- NAVIGATION ---
page = st.sidebar.radio("Go to", ["📦 Inventory Dashboard", "⚙️ Manage Categories"])

st.sidebar.divider()

# ==========================================
# PAGE 1: INVENTORY DASHBOARD
# ==========================================
if page == "📦 Inventory Dashboard":
    
    # --- SIDEBAR: ADD PRODUCTS ---
    with st.sidebar:
        st.header("Manage Stock Items")
        
        tab1, tab2 = st.tabs(["🆕 New Product", "➕ Add Variant"])
        
        # TAB 1: CREATE COMPLETELY NEW PRODUCT
        with tab1:
            with st.form("add_new_item_form", clear_on_submit=True):
                if st.session_state.categories:
                    new_category = st.selectbox("Select Category", st.session_state.categories)
                else:
                    new_category = st.selectbox("Select Category", ["No Categories Found"])
                    
                new_name = st.text_input("Product Name (e.g. TC Boiler Suit)")
                
                st.write("Enter sizes separated by comma.")
                sizes_input = st.text_input("Sizes (e.g. S, M, L)", key="new_sizes")
                initial_stock = st.number_input("Initial Stock", value=0, min_value=0, step=1, key="new_stock")
                
                submitted_new = st.form_submit_button("Create Product")
                
                if submitted_new:
                    if new_name and sizes_input and st.session_state.categories:
                        sizes_list = [s.strip() for s in sizes_input.split(',') if s.strip()]
                        count_added = 0
                        
                        for size in sizes_list:
                            # Check duplicate
                            exists = False
                            for item in st.session_state.inventory:
                                if item['name'].lower() == new_name.lower() and item['size'].lower() == size.lower():
                                    exists = True
                                    break
                            
                            if not exists:
                                new_item = {
                                    "id": int(datetime.now().timestamp() * 1000) + count_added, 
                                    "category": new_category,
                                    "name": new_name,
                                    "size": size,
                                    "stock": initial_stock,
                                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                                }
                                st.session_state.inventory.append(new_item)
                                count_added += 1
                        
                        save_inventory(st.session_state.inventory)
                        st.success(f"✅ Created {count_added} variants")
                        st.rerun()
                    else:
                        st.warning("Please enter Name, Sizes and ensure a Category exists.")

        # TAB 2: ADD SIZE TO EXISTING PRODUCT
        with tab2:
            existing_names = sorted(list(set(item['name'] for item in st.session_state.inventory)))
            
            if existing_names:
                with st.form("add_variant_form", clear_on_submit=True):
                    selected_product = st.selectbox("Select Existing Product", existing_names)
                    
                    st.write("Enter NEW sizes separated by comma.")
                    new_sizes_input = st.text_input("New Sizes (e.g. XL, XXL)", key="exist_sizes")
                    variant_stock = st.number_input("Initial Stock", value=0, min_value=0, step=1, key="exist_stock")
                    
                    submitted_variant = st.form_submit_button("Add Variants")
                    
                    if submitted_variant:
                        if selected_product and new_sizes_input:
                            parent_category = next((item['category'] for item in st.session_state.inventory if item['name'] == selected_product), "Uncategorized")
                            sizes_list = [s.strip() for s in new_sizes_input.split(',') if s.strip()]
                            count_added = 0
                            
                            for size in sizes_list:
                                exists = False
                                for item in st.session_state.inventory:
                                    if item['name'] == selected_product and item['size'].lower() == size.lower():
                                        exists = True
                                        break
                                
                                if not exists:
                                    new_item = {
                                        "id": int(datetime.now().timestamp() * 1000) + count_added, 
                                        "category": parent_category,
                                        "name": selected_product,
                                        "size": size,
                                        "stock": variant_stock,
                                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                                    }
                                    st.session_state.inventory.append(new_item)
                                    count_added += 1
                                else:
                                    st.toast(f"Skipped {size} (Already exists)")
                            
                            if count_added > 0:
                                save_inventory(st.session_state.inventory)
                                st.success(f"✅ Added {count_added} new sizes")
                                st.rerun()
                            else:
                                st.warning("No new items added.")
                        else:
                            st.warning("Please enter at least one size.")
            else:
                st.info("No existing products found. Use 'New Product' tab first.")

    # --- MAIN DASHBOARD CONTENT ---
    search_query = st.text_input("🔍 Search Product...", "")

    df = pd.DataFrame(st.session_state.inventory)

    if not df.empty:
        if search_query:
            mask = df.apply(lambda x: search_query.lower() in str(x).lower(), axis=1)
            df = df[mask]

        categories_in_stock = df['category'].unique()
        
        for cat in categories_in_stock:
            st.markdown(f"### 📂 {cat}")
            
            cat_df = df[df['category'] == cat]
            unique_products = cat_df['name'].unique()
            
            for product_name in unique_products:
                product_variants = cat_df[cat_df['name'] == product_name]
                product_variants = product_variants.sort_values('id')
                total_stock = product_variants['stock'].sum()
                
                # --- PRODUCT CARD ---
                with st.expander(f"**{product_name}** (Total Stock: {total_stock})"):
                    
                    # 1. LIST VARIANTS
                    for index, row in product_variants.iterrows():
                        c1, c2, c3, c4 = st.columns([2, 1, 2, 1]) 
                        
                        with c1:
                            st.markdown(f"##### Size: {row['size']}")
                        
                        with c2:
                            color = "red" if row['stock'] < 5 else "green"
                            st.markdown(f"<span style='color:{color}; font-size: 20px; font-weight:bold'>{row['stock']}</span>", unsafe_allow_html=True)
                            
                        with c3:
                            b1, b2 = st.columns(2)
                            if b1.button("➖", key=f"dec_{row['id']}"):
                                for i in st.session_state.inventory:
                                    if i['id'] == row['id'] and i['stock'] > 0:
                                        i['stock'] -= 1
                                save_inventory(st.session_state.inventory)
                                st.rerun()
                                
                            if b2.button("➕", key=f"inc_{row['id']}"):
                                for i in st.session_state.inventory:
                                    if i['id'] == row['id']:
                                        i['stock'] += 1
                                save_inventory(st.session_state.inventory)
                                st.rerun()
                        
                        # DELETE SINGLE VARIANT
                        with c4:
                            if st.button("🗑️", key=f"del_var_{row['id']}", help="Delete this size only"):
                                st.session_state.inventory = [item for item in st.session_state.inventory if item['id'] != row['id']]
                                save_inventory(st.session_state.inventory)
                                st.rerun()

                    st.divider()
                    
                    # 2. DELETE ENTIRE PRODUCT BUTTON
                    if st.button(f"🚨 Delete Entire '{product_name}' Product", key=f"del_prod_{product_name}"):
                        st.session_state.inventory = [
                            item for item in st.session_state.inventory 
                            if item['name'] != product_name
                        ]
                        save_inventory(st.session_state.inventory)
                        st.success(f"Deleted {product_name}!")
                        st.rerun()

            st.divider()
    else:
        st.info("Inventory is empty.")

# ==========================================
# PAGE 2: MANAGE CATEGORIES
# ==========================================
elif page == "⚙️ Manage Categories":
    st.header("Manage Categories")
    st.write("⚠️ Deleting a category will also delete ALL products inside it.")
    
    with st.container(border=True):
        st.subheader("Add New Category")
        c1, c2 = st.columns([3, 1])
        new_cat_input = c1.text_input("New Category Name", label_visibility="collapsed", placeholder="Enter category name...")
        if c2.button("Add Category", use_container_width=True):
            if new_cat_input:
                if new_cat_input not in st.session_state.categories:
                    st.session_state.categories.append(new_cat_input)
                    save_categories(st.session_state.categories)
                    st.success(f"Added: {new_cat_input}")
                    st.rerun()
                else:
                    st.warning("Category already exists.")
    
    st.subheader("Existing Categories")
    
    if st.session_state.categories:
        for cat in st.session_state.categories:
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**📂 {cat}**")
            
            if c2.button("Delete", key=f"del_cat_{cat}"):
                st.session_state.categories.remove(cat)
                save_categories(st.session_state.categories)
                
                before_count = len(st.session_state.inventory)
                st.session_state.inventory = [
                    item for item in st.session_state.inventory 
                    if item['category'] != cat
                ]
                deleted_count = before_count - len(st.session_state.inventory)
                save_inventory(st.session_state.inventory)
                
                st.toast(f"Deleted '{cat}' and {deleted_count} items!")
                st.rerun()
            st.divider()
    else:
        st.info("No categories found.")