import streamlit as st
import json
import os
from keyword_generator import generate_keyword_structure, test_openai_connection, test_gemini_connection
from mindmap_visualizer import visualize_mindmap
from data_processor import process_data_for_visualization

st.set_page_config(
    page_title="SEO Keyword Mindmap Generator",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state for API keys
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""
if 'google_search_api_key' not in st.session_state:
    st.session_state.google_search_api_key = ""
if 'google_search_cx' not in st.session_state:
    st.session_state.google_search_cx = ""

st.title("🔍 SEO Keyword Mindmap Generator")
st.markdown("""
Generate an interactive mindmap visualization from a main keyword with intent categorization and competitor analysis.
This tool helps you:
- Create a structured keyword hierarchy
- Categorize keywords by search intent
- Generate SEO-friendly article titles
- Recommend ideal word counts
- Identify potential competitors
""")

# API settings in expander
with st.expander("⚙️ API Settings (Optional)", expanded=False):
    st.info("Using API keys enhances keyword generation with more accurate results.")
    
    api_col1, api_col2 = st.columns(2)
    
    with api_col1:
        st.subheader("AI Generation APIs")
        # API options
        api_option = st.radio(
            "Select AI provider:",
            options=["None", "OpenAI", "Google Gemini"],
            horizontal=True,
            index=0 if st.session_state.openai_api_key == "" and st.session_state.gemini_api_key == "" else 
                   1 if st.session_state.openai_api_key != "" else 2,
            help="Choose an AI provider for enhanced keyword generation",
            key="api_provider"
        )
        
        if api_option == "OpenAI":
            api_col1_1, api_col1_2 = st.columns([3, 1])
            with api_col1_1:
                st.session_state.openai_api_key = st.text_input(
                    "OpenAI API Key:", 
                    type="password",
                    value=st.session_state.openai_api_key,
                    help="Enter your OpenAI API key for better keyword generation"
                )
            with api_col1_2:
                if st.button("Test Connection", key="test_openai"):
                    if st.session_state.openai_api_key:
                        with st.spinner("Testing OpenAI API connection..."):
                            # Temporarily set the API key for testing
                            os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key
                            result = test_openai_connection()
                            if result["success"]:
                                st.success(result["message"])
                            else:
                                st.error(result["message"])
                    else:
                        st.error("Please enter an OpenAI API key first")
        
        elif api_option == "Google Gemini":
            api_col1_1, api_col1_2 = st.columns([3, 1])
            with api_col1_1:
                st.session_state.gemini_api_key = st.text_input(
                    "Google Gemini API Key:", 
                    type="password",
                    value=st.session_state.gemini_api_key,
                    help="Enter your Google Gemini API key for better keyword generation"
                )
            with api_col1_2:
                if st.button("Test Connection", key="test_gemini"):
                    if st.session_state.gemini_api_key:
                        with st.spinner("Testing Gemini API connection..."):
                            # Temporarily set the API key for testing
                            os.environ["GEMINI_API_KEY"] = st.session_state.gemini_api_key
                            result = test_gemini_connection()
                            if result["success"]:
                                st.success(result["message"])
                            else:
                                st.error(result["message"])
                    else:
                        st.error("Please enter a Gemini API key first")
    
    with api_col2:
        st.subheader("Search Data APIs")
        st.markdown("For more accurate competitor analysis:")
        st.session_state.google_search_api_key = st.text_input(
            "Google Search API Key (Optional):", 
            type="password",
            value=st.session_state.google_search_api_key,
            help="Enter your Google Custom Search API key"
        )
        st.session_state.google_search_cx = st.text_input(
            "Google Search Engine ID (CX) (Optional):", 
            value=st.session_state.google_search_cx,
            help="Enter your Google Custom Search Engine ID"
        )

# Main form for keyword input
with st.form(key="keyword_form"):
    main_keyword = st.text_input("Enter your main keyword:", placeholder="e.g., digital marketing")
    depth = st.slider("Keyword depth (higher = more keywords, slower generation)", 1, 3, 2)
    
    # Create advanced options in expander
    with st.expander("Advanced Options", expanded=False):
        custom_prompt = st.text_area(
            "Custom Prompt for Title Generation (Optional):",
            placeholder="e.g., Use a formal tone, include numbers in titles, focus on beginners, etc.",
            help="This prompt will guide the AI when generating titles for your keywords."
        )
        st.info("Custom prompts work best with OpenAI or Google Gemini APIs enabled.")
    
    submit_button = st.form_submit_button(label="Generate Mindmap")

if submit_button and main_keyword:
    with st.spinner("Generating keyword structure..."):
        # Set the appropriate API keys if provided
        if st.session_state.api_provider == "OpenAI" and st.session_state.openai_api_key:
            # Temporarily set the OpenAI API key for this session
            os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key
            st.info("Using OpenAI for enhanced keyword generation.")
        elif st.session_state.api_provider == "Google Gemini" and st.session_state.gemini_api_key:
            # Temporarily set the Gemini API key for this session
            os.environ["GEMINI_API_KEY"] = st.session_state.gemini_api_key
            st.info("Using Google Gemini for enhanced keyword generation.")
        else:
            st.info("Using built-in rules for keyword generation.")
        
        # Set Google Search API key if provided
        if st.session_state.google_search_api_key and st.session_state.google_search_cx:
            os.environ["GOOGLE_SEARCH_API_KEY"] = st.session_state.google_search_api_key
            os.environ["GOOGLE_SEARCH_CX"] = st.session_state.google_search_cx
            st.info("Using Google Search API for competitor analysis.")
            
        # Generate keyword structure with custom prompt if provided
        custom_prompt_text = custom_prompt if custom_prompt else ""
        keyword_data = generate_keyword_structure(main_keyword, depth, custom_prompt=custom_prompt_text)
        
        # Process data for visualization
        nodes, edges = process_data_for_visualization(keyword_data)
        
        # Display the mindmap visualization
        visualize_mindmap(nodes, edges)
        
        # Add a expander for legend
        with st.expander("📊 Mindmap Color Legend"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div style="background-color:#4CAF50;padding:10px;border-radius:5px;color:white;text-align:center;">Commercial Intent</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div style="background-color:#2196F3;padding:10px;border-radius:5px;color:white;text-align:center;">Informational Intent</div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div style="background-color:#FFC107;padding:10px;border-radius:5px;color:white;text-align:center;">Navigational Intent</div>', unsafe_allow_html=True)
        
        # Add space before export
        st.write("")
        
        # Create a better download experience
        download_col1, download_col2 = st.columns([1, 1])
        with download_col1:
            # Export option with prominent styling
            st.download_button(
                label="📥 Export as JSON",
                data=json.dumps(keyword_data, indent=2),
                file_name=f"{main_keyword.replace(' ', '_')}_seo_mindmap.json",
                mime="application/json",
                use_container_width=True
            )
        
        with download_col2:
            # Extract all keywords from the structure
            all_keywords = []
            all_keywords_with_intent = []
            
            def extract_keywords(node, depth=0, path=""):
                current_path = path + " > " + node["keyword"] if path else node["keyword"]
                all_keywords.append(node["keyword"])
                all_keywords_with_intent.append(f"{node['keyword']},{node['intent']},{node['word_count']},\"{node['title']}\"")
                
                for child in node["children"]:
                    extract_keywords(child, depth+1, current_path)
            
            extract_keywords(keyword_data)
            
            # Create a download container with tabs for different formats
            tab1, tab2 = st.tabs(["Plain Keywords", "CSV Format"])
            
            with tab1:
                # Create a copyable list of keywords
                keywords_text = "\n".join(all_keywords)
                st.download_button(
                    label="📋 Copy All Keywords",
                    data=keywords_text,
                    file_name=f"{main_keyword.replace(' ', '_')}_keywords.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with tab2:
                # Create CSV format with headers
                csv_text = "Keyword,Intent,Word Count,Title\n" + "\n".join(all_keywords_with_intent)
                st.download_button(
                    label="📊 Export as CSV",
                    data=csv_text,
                    file_name=f"{main_keyword.replace(' ', '_')}_keywords.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # Display keyword data in a structured, user-friendly way
        st.subheader("Keyword Details")
        
        with st.expander("View Structured Data", expanded=False):
            # Function to recursively display keyword data in a more readable format
            def display_keyword_data(node, level=0):
                indent = "  " * level
                icon = "🔍" if level == 0 else "➡️"
                
                # Format the node data
                st.markdown(f"{indent}{icon} **{node['keyword']}** ({node['intent']})")
                
                # Create columns for details
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"{indent}  Word Count: {node['word_count']}")
                
                with col2:
                    st.markdown(f"{indent}  Title: *{node['title']}*")
                
                # Display competitors if available
                if node.get('competitors') and len(node['competitors']) > 0:
                    st.markdown(f"{indent}  **Competitors:**")
                    for i, comp in enumerate(node['competitors']):
                        st.markdown(f"{indent}  {i+1}. [{comp.get('title', 'Unknown')}]({comp.get('url', '#')})")
                
                # Recursively display children
                if node['children']:
                    for child in node['children']:
                        display_keyword_data(child, level + 1)
            
            # Display the data
            display_keyword_data(keyword_data)
            
        # Also provide raw JSON for developers
        with st.expander("Raw JSON Data", expanded=False):
            st.json(keyword_data)
elif submit_button:
    st.error("Please enter a main keyword to generate the mindmap.")

st.markdown("---")
st.markdown("### How to use this tool")
st.markdown("""
1. Expand the **⚙️ API Settings** section to configure your API keys (optional but recommended)
2. Enter a main keyword in the text field
3. For enhanced titles, add a custom prompt like "use formal tone" or "add numbers in title" (requires AI API)
4. Set the keyword depth (more depth = more keywords)
5. Click 'Generate Mindmap' to create your keyword structure
6. Explore the interactive mindmap visualization - hover over nodes for details
7. Download the results in various formats:
   - Export as JSON for complete data structure
   - Copy All Keywords as plain text list
   - Export as CSV with intent, word count, and title data
""")

st.markdown("### API Options")
with st.expander("API Information", expanded=False):
    st.markdown("""
    **AI Generation APIs** (Choose one):
    - **OpenAI**: Enhanced keyword generation and AI-generated titles using GPT-4o. Judul akan dibuat oleh AI secara langsung berdasarkan kata kunci dan intent, bukan diambil dari Google. OpenAI juga memproses custom prompt dengan lebih baik. Requires an API key from [OpenAI](https://platform.openai.com/).
    - **Google Gemini**: Enhanced keyword generation and AI-generated titles using Gemini 2.0 Flash. Judul akan dibuat oleh AI secara langsung berdasarkan kata kunci dan intent, bukan diambil dari Google. Requires an API key from [Google AI Studio](https://makersuite.google.com/).
    
    You can test your API connection before generating keywords using the "Test Connection" button.
    
    **Search Data APIs** (Optional):
    - **Google Search API**: Real-time competitor data from Google search results. With this API, competitor information will be actual websites ranking for your keywords in Google instead of AI-generated examples. Requires:
        1. A Google Search API Key from [Google Cloud Console](https://console.cloud.google.com/)
        2. A Custom Search Engine ID (CX) from [Programmable Search Engine](https://programmablesearchengine.google.com/)
    """)
    
    st.info("Without API keys, the tool will still work using AI-generated examples, but results will be less accurate. Custom title prompts like 'use formal tone' or 'add numbers in title' require an AI API key to work effectively.")
