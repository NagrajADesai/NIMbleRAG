import streamlit as st
import time
from api_client import APIClient

def main():
    st.set_page_config("Create Knowledgebase", page_icon="📂", layout="wide")
    st.title("📂 Knowledgebase Manager")

    # Sidebar
    dbs = APIClient.get_databases()
    with st.sidebar:
        st.header("Existing Databases")
        if dbs:
            st.markdown("\n".join([f"- {db}" for db in dbs]))
        else:
            st.info("No databases found.")

    # Main Area
    st.subheader("🆕 Create or Update a Knowledgebase")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        db_name = st.text_input("Database Name", placeholder="e.g., Finance_Reports_2024")
        
        uploaded_files = st.file_uploader(
            "Upload Documents",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'pptx', 'xlsx', 'txt']
        )
        
        if st.button("🚀 Process & Create/Update", type="primary"):
            if not db_name:
                st.error("⚠️ Please specify a Database Name.")
            elif not uploaded_files:
                st.error("⚠️ Please upload at least one file.")
            else:
                 safe_name = "".join([c for c in db_name if c.isalnum() or c in ('_', '-')])
                 
                 with st.spinner(f"⏳ Processing into '{safe_name}' (this may take a while)..."):
                     try:
                        result = APIClient.upload_documents(safe_name, uploaded_files)
                        
                        # Show Data Engineering Logs
                        if result.get("logs"):
                            with st.status("🛠️ Data Engineering Log", expanded=True):
                                for log in result["logs"]:
                                    if log['step'] == 'Error':
                                        st.error(f"**{log['file']}**: {log['details']}")
                                    elif log['step'] == 'Warning':
                                        st.warning(f"**{log['file']}**: {log['details']}")
                                    else:
                                        st.write(f"**[{log['step']}]** {log['file']}: {log['details']}")
                        
                        st.info(f"Generated {result.get('chunks_created', 0)} chunks.")
                        st.success(f"✅ {result.get('message')}")
                        time.sleep(1)
                        st.rerun()
                     except Exception as e:
                         st.error(f"❌ Error: {str(e)}")

    with col2:
         st.warning("⚠️ **Note**: Updating an existing database with the same name will merge new documents into it.")
         st.markdown("""
         ### Supported Formats:
         - **PDF** (.pdf)
         - **Word** (.docx)
         - **PowerPoint** (.pptx)
         - **Excel** (.xlsx)
         - **Text** (.txt)
         """)

if __name__ == "__main__":
    main()
