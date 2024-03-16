import streamlit as st
import json
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib_venn import venn2
from collections import Counter



@st.cache_data
def load_data():
    df = pd.read_parquet("data/data_counts.parquet")
    experience_groups = df["Experience Group"].dropna().unique()
    countries = df["Country"].dropna().unique()

    experience_groups.sort()
    countries.sort()
    return df, experience_groups, countries

# Function to generate a word cloud from a list of texts
def generate_wordcloud(texts):
    # Lowercase and strip each text
    texts = [text.lower().strip() for text in texts]
    
    # Join the texts into a single string
    all_text = " ".join(texts)

    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)

    # Display the word cloud using matplotlib
    plt.figure(figsize=(8, 4), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    st.pyplot(plt)

    # Count the occurrences of each word
    word_counts = Counter(all_text.split())

    # Sort the dictionary by count number
    sorted_word_counts = dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True))

    # Display the sorted word counts
    st.write(sorted_word_counts)

# Assuming df has 'gender' and 'words' columns
def generate_venn_diagram(df, category, topn):
    # Flatten the lists of words for each gender
    male_words = [word for sublist in df[df['Gender'] == 'M'][f'{category}_texts'] for word in sublist]
    female_words = [word for sublist in df[df['Gender'] == 'F'][f'{category}_texts'] for word in sublist]

    # Count the frequency of words
    male_counts = Counter(male_words)
    female_counts = Counter(female_words)

    # Find the common words
    common_words = set(male_words) & set(female_words)

    # Find the unique top 5 words for each gender and top 5 common words
    top_male_words = [word for word, count in male_counts.most_common() if word not in common_words][:topn]
    top_female_words = [word for word, count in female_counts.most_common() if word not in common_words][:topn]
    top_common_words = [word for word, count in male_counts.most_common() if word in common_words][:topn]

    # Create Venn diagram
    plt.figure(figsize=(8, 6))
    venn = venn2([set(male_words), set(female_words)], ('Male', 'Female'))

    st.sidebar.pyplot(plt)

    # Optionally, display the lists as tables or bullet points below the diagram
    st.subheader('Top Words')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Top Male Words**")
        st.write(top_male_words)
    with col2:
        st.markdown("**Top Common Words**")
        st.write(top_common_words)
    with col3:
        st.markdown("**Top Female Words**")
        st.write(top_female_words)

st.title("Placing the Holocaust Visualizer")

df, experience_groups, countries = load_data()

st.write(df)
# Categories to explore
categories = [
    'BUILDING', 'NPIP', 'COUNTRY', 'POPULATED_PLACE', 'DLF', 
    'SPATIAL_OBJ', 'REGION', 'ENV_FEATURES', 'INT_SPACE', 
    'RIVER', 'FOREST'
]

style = st.sidebar.selectbox("Select Method", ["Testimony", "Most"])

if style=="Testimony":
    testimony_options = ["All"]+df.file.tolist()
    testimonies = st.sidebar.multiselect("Select Testimonies", testimony_options)

category = st.sidebar.selectbox("Select Category", categories)

gender_true = st.sidebar.checkbox("Gender")
survivor_true = st.sidebar.checkbox("Survivor")
country_selected = st.sidebar.multiselect("Country", countries)
group_selected = st.sidebar.multiselect("Group", experience_groups)

if survivor_true:
    df = df[df["Experience Group"] == "Survivor"]
if country_selected:
    df = df.dropna(subset=['Country'])
    df = df[df["Country"].isin(country_selected)]
if group_selected:
    df = df.dropna(subset=['Experience Group'])
    df = df[df["Experience Group"].isin(group_selected)]

if gender_true:
    topn = st.sidebar.number_input("Top-N", 1, 100)

if style=="Most":
    max_count = df[category].max()
    max_testimonies = df[df[category] == max_count]
    st.write(max_testimonies)
    generate_wordcloud(max_testimonies[f"{category}_texts"].tolist()[0])

if style=="Testimony":
    if testimonies:
        if "All" in testimonies:
            df_test = df
        else:   
            df_test = df[df["file"].isin(testimonies)]
        # st.write(df_test)
        if gender_true:
            generate_venn_diagram(df, category, topn)
        generate_wordcloud([word for sublist in df_test[f"{category}_texts"].tolist() for word in sublist])
