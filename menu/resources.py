import streamlit as st
import sqlite3
import os

# Create a 'data' directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Database setup with persistent storage
class Database:
    def __init__(self, db_name='data/resourcelib.db'):
        # Use absolute path to ensure database file is created in the correct location
        self.db_path = os.path.abspath(db_name)
        # Create connection with check_same_thread=False for Streamlit's threading model
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.setup_database()

    def setup_database(self):
        cursor = self.conn.cursor()
        
        # Create resources table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            url TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.conn.commit()

    def add_resource(self, title, category, url, description):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO resources (title, category, url, description)
                VALUES (?, ?, ?, ?)
            ''', (title, category, url, description))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"Error adding resource: {e}")
            return False

    def get_resources(self, category=None, search=None):
        cursor = self.conn.cursor()
        try:
            if category and search:
                cursor.execute('''
                    SELECT title, url, description, category FROM resources 
                    WHERE category = ? AND (title LIKE ? OR description LIKE ?)
                    ORDER BY created_at DESC
                ''', (category, f'%{search}%', f'%{search}%'))
            elif category and category != "All":
                cursor.execute('''
                    SELECT title, url, description, category FROM resources 
                    WHERE category = ?
                    ORDER BY created_at DESC
                ''', (category,))
            elif search:
                cursor.execute('''
                    SELECT title, url, description, category FROM resources 
                    WHERE title LIKE ? OR description LIKE ?
                    ORDER BY created_at DESC
                ''', (f'%{search}%', f'%{search}%'))
            else:
                cursor.execute('''
                    SELECT title, url, description, category 
                    FROM resources
                    ORDER BY created_at DESC
                ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"Error retrieving resources: {e}")
            return []

    def delete_resource(self, title):
        cursor = self.conn.cursor()
        try:
            cursor.execute('DELETE FROM resources WHERE title = ?', (title,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"Error deleting resource: {e}")
            return False

    def __del__(self):
        """Ensure database connection is properly closed"""
        if hasattr(self, 'conn'):
            self.conn.close()

# Initialize database in session state
def init_db():
    if 'db' not in st.session_state:
        st.session_state.db = Database()

# Resource library page function
def main():
    # Ensure database is initialized
    init_db()
    
    st.title("Resource Library")
    
    # Add CSS that works with both light and dark themes
    st.markdown("""
        <style>
        .resource-card {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .resource-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .resource-category {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            background-color: rgba(70, 130, 180, 0.5);
            margin-bottom: 10px;
        }
        .resource-link a {
            text-decoration: none;
            color: #4CAF50;
            font-weight: bold;
        }
        .resource-description {
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main content area with tabs
    tab1, tab2 = st.tabs(["Browse Resources", "Add New Resource"])

    with tab1:
        # Filters
        col1, col2 = st.columns([2, 3])
        
        with col1:
            selected_category = st.selectbox(
                "Select Category",
                ["All"] + ["Video Lectures", "Practice Problems", "Reference Materials", "Past Papers", "Study Notes", "Other"]
            )
            
        with col2:
            search_query = st.text_input("Search Resources", placeholder="Enter keywords...")

        # Display resources
        resources = st.session_state.db.get_resources(
            category=selected_category if selected_category != "All" else None,
            search=search_query if search_query else None
        )
        
        if not resources:
            st.info("No resources found. Add some resources to get started!")
        
        for i, resource in enumerate(resources):
            title, url, description, category = resource
            
            # Use regular st components instead of HTML markdown for better dark mode compatibility
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.subheader(title)
                
                with col2:
                    if st.button("Delete", key=f"delete_{i}_{title}", use_container_width=True):
                        if st.session_state.db.delete_resource(title):
                            st.success("Resource deleted successfully!")
                            st.session_state["rerun"] = True
                            st.rerun()
                
                st.caption(f"Category: {category}")
                
                if url:
                    st.markdown(f"[Access Resource]({url})")
                
                st.text_area("Description", description, height=100, key=f"desc_{i}", disabled=False)
                st.divider()

    with tab2:
        st.subheader("Add New Resource")
        with st.form("add_resource", clear_on_submit=True):
            title = st.text_input("Title*")
            category = st.selectbox(
                "Category*",
                ["Video Lectures", "Practice Problems", "Reference Materials", "Past Papers", "Study Notes", "Other"]
            )
            url = st.text_input("URL (optional)")
            description = st.text_area("Description*")
            
            col1, col2, col3 = st.columns([2, 2, 2])
            with col2:
                submitted = st.form_submit_button("Add Resource", use_container_width=True)
            
            if submitted:
                if title and description:
                    if st.session_state.db.add_resource(title, category, url, description):
                        st.success("Resource added successfully!")
                        st.session_state["rerun"] = True
                        st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")

if __name__ == "__main__":
    main()