import streamlit as st

#set page configuration
st.set_page_config(
    page_title="⚡ Transmission Line Design",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Set the title of the app
st.title(":rainbow[Transmission Line Design App] :zap:", text_alignment="center")

st.space(size="medium")

st.markdown("""

                                     
Welcome to the complete transmission line design application.

            
    
Use the sidebar to navigate:
- Tower Design
- Earth Wire Design
- Conductor Selection
- Insulation Design
""")