import streamlit as st
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from rapidfuzz import fuzz
from sklearn.metrics import confusion_matrix

st.set_page_config(page_title="Aviation Maintenance Dashboard", layout="wide")
st.title("✈️ Smart Aviation Maintenance Analytics Dashboard")
st.markdown("Developed by Niki - Production-Grade Predictive Maintenance System (Final Advanced Edition)")
st.write("---")

@st.cache_data
def load_live_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            live_data = json.load(f)
        
        if 'data' in live_data:
            df = pd.DataFrame(live_data['data'])
        else:
            df = pd.DataFrame(live_data)
            
        if 'part_info' not in df.columns and len(df.columns) > 0:
            df['part_info'] = df.iloc[:, 0]
        if 'actions_done' not in df.columns and len(df.columns) > 1:
            df['actions_done'] = df.iloc[:, 1]

        df['part_info'] = df['part_info'].fillna("Unknown").astype(str)
        df['actions_done'] = df['actions_done'].fillna("No record").astype(str)
        return df
    except Exception as e:
        st.error(f"❌ Error loading data.json: {e}")
        return pd.DataFrame()

df = load_live_data()

if not df.empty:
    def extract_sub_components(text):
        text_lower = text.lower()
        component_map = {
            'motor': 'Electrical Motor', 'diode': 'Diode', 'switch': 'Micro/Limit Switch',
            'gearbox': 'Gearbox', 'harness': 'Wiring Harness', 'wiring': 'Wiring Harness',
            'transformer': 'Transformer', 'dial': 'Dial/Display Assy', 'lighting': 'Lighting Module',
            'synchro': 'Synchro Receiver', 'valve': 'Actuator Valve', 'amp': 'Amplifier', 'sw': 'switch'
        }
        found_parts = [formal_name for keyword, formal_name in component_map.items() if keyword in text_lower]
        found_parts = list(set(found_parts))
        return " + ".join(found_parts) if found_parts else "General Assembly"

    def fuzzy_categorize_text_log(text):
        text_lower = str(text).lower()
        words = text_lower.split()
        THRESHOLD = 85.0
        
        if 'cannibalize' in text_lower or 'قطعه‌برداری' in text_lower:
            return 'Cannibalization & Parts Harvesting'

        if 'replace' in text_lower or 'change' in text_lower or 'new one' in text_lower or 'تعویض' in text_lower:
            return 'Unit Replacement & Component Overhaul'

        repair_keywords = ['repair', 'resolder', 'fix', 'reconnect', 'لحیم', 'تعمیر']
        for word in words:
            for keyword in repair_keywords:
                if fuzz.ratio(word, keyword) >= THRESHOLD or keyword in word:
                    return 'General Shop-Floor Repair'

        calib_keywords = ['adjust', 'calibrate', 'check', 'test', 'no record', 'clean', 'تنظیم']
        for word in words:
            for keyword in calib_keywords:
                if fuzz.ratio(word, keyword) >= THRESHOLD or keyword in word:
                    return 'Calibration, Inspection & Testing'
            
        return 'Other Custom Technical Actions'

    df['standardized_action'] = df['actions_done'].apply(fuzzy_categorize_text_log)
    df['affected_sub_parts'] = df['actions_done'].apply(extract_sub_components)

    st.sidebar.header("🔍 Filter & Search Options")
    user_input = st.sidebar.text_input("Enter Component Name or Part Number:", "1342").strip()

    if user_input:
        matched_df = df[df['part_info'].str.lower().str.contains(user_input.lower())]
        
        if matched_df.empty:
            st.error(f"❌ No historical maintenance records found for component: '{user_input}'")        
        else:
            total_cases = len(matched_df)
            st.subheader(f"📊 Analytics Result for '{user_input}' ({total_cases} records found)")
            st.write("---")
            
            actions_counter = matched_df['standardized_action'].value_counts()
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Total Records", f"{total_cases}")
            with col_m2:
                st.metric("Repairs Needed", f"{actions_counter.get('General Shop-Floor Repair', 0)}")
            with col_m3:
                st.metric("Calibrations Checked", f"{actions_counter.get('Calibration, Inspection & Testing', 0)}")
                
            st.write("---")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.write("### 🍩 Action Breakdown Percentages")
                if not actions_counter.empty:
                    fig, ax = plt.subplots(figsize=(5, 5))
                    colors = ['#2b5c8f', '#4682b4', '#a0c4df', '#d3e2f2']
                    ax.pie(actions_counter, labels=actions_counter.index, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 8})
                    centre_circle = plt.Circle((0,0), 0.70, fc='white')
                    fig.gca().add_artist(centre_circle)
                    st.pyplot(fig)
                else:
                    st.write("No actions to display.")
                    
            with col_chart2:
                st.write("### 📈 Machine Learning Confusion Matrix")
                
                if 'actual_label' in matched_df.columns:
                    clean_matched = matched_df.dropna(subset=['actual_label', 'standardized_action'])
                    
                    if len(clean_matched) > 0:
                        correct_predictions = (clean_matched['standardized_action'] == clean_matched['actual_label']).sum()
                        accuracy = (correct_predictions / len(clean_matched)) * 100
                        st.sidebar.metric("System Accuracy", f"{accuracy:.2f}%")
                        
                        all_labels = sorted(list(set(clean_matched['actual_label'].unique()) | set(clean_matched['standardized_action'].unique())))
                        cm = confusion_matrix(clean_matched['actual_label'], clean_matched['standardized_action'], labels=all_labels)
                        
                        fig_cm, ax_cm = plt.subplots(figsize=(6, 5))
                        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                                    xticklabels=all_labels, yticklabels=all_labels,
                                    annot_kws={'size': 9, 'weight': 'bold'})
                        plt.ylabel("Actual Label")
                        plt.xlabel("Predicted Label")
                        plt.xticks(rotation=45, ha='right')
                        st.pyplot(fig_cm) 
                    else:
                        st.sidebar.metric("System Accuracy", "N/A (No Labels)")
                        st.write("No clean labeled data available for this component.")
                else:
                    st.write("Please add 'actual_label' column to data.")

            most_common_action = actions_counter.index[0] if not actions_counter.empty else "None"
            
            if 'Replacement' in most_common_action:
                st.error("**RECOMMENDATION:** High replacement rate detected. Verify stock levels immediately.")
            elif 'Calibration' in most_common_action:
                st.success("**RECOMMENDATION:** Calibration dependency detected. Focus on CMM physical alignments and tolerances.")
            elif 'General Shop-Floor Repair' in most_common_action:
                st.warning("**RECOMMENDATION:** High repair frequency in wiring and circuits. Inspect vibration isolation mounts and connector strain reliefs.")
            else:
                st.info("**RECOMMENDATION:** Standard component servicing required. Perform routine bench testing.")

            st.write("---")
            
            st.write("### 📋 Specific Shop-Floor Records & Logs")
            display_df = matched_df[['affected_sub_parts', 'actions_done', 'standardized_action']].rename(
                columns={'affected_sub_parts': 'Affected Sub-Component', 'actions_done': 'Raw Log Text', 'standardized_action': 'Model Classification'}
            )
            st.dataframe(display_df, use_container_width=True)
