import streamlit as st
import pandas as pd
import plotly.express as px

# Must be the first Streamlit command
st.set_page_config(page_title="Green Coverage Dashboard", layout="wide")

# 💾 Load and clean data
df = pd.read_csv("PC4_TreesBushesGrass.csv", sep=';')
df.columns = df.columns.str.strip().str.lower()
df['postcode'] = df['postcode'].astype(str)

# 🧼 Fix commas in decimal numbers and convert to float
df['percentagetrees'] = df['percentagetrees'].str.replace(',', '.').astype(float)
df['percentagebushes'] = df['percentagebushes'].str.replace(',', '.').astype(float)
df['percentagegrass'] = df['percentagegrass'].str.replace(',', '.').astype(float)

# ➕ Create total_green column
df["total_green"] = df["percentagetrees"] + df["percentagebushes"] + df["percentagegrass"]

# 🔵 RGB mapping
df['R'] = (df['percentagetrees'] * 2.55).clip(0, 255).round().astype(int)
df['G'] = (df['percentagebushes'] * 2.55).clip(0, 255).round().astype(int)
df['B'] = (df['percentagegrass'] * 2.55).clip(0, 255).round().astype(int)
df['color'] = df.apply(lambda row: f"#{row['R']:02x}{row['G']:02x}{row['B']:02x}", axis=1)

# ✅ Optional: preview data
# st.write(df.head())

# 🟩 Title
st.title("🌿 Dutch Postcode Green Coverage Dashboard")
st.markdown("Explore trees, bushes, and grass coverage across Dutch postcodes.")

# 🔍 Postcode selection
selected_postcode = st.selectbox("Select a Postcode", sorted(df['postcode'].unique()))

# 🔢 Display raw values for selected postcode
row = df[df['postcode'] == selected_postcode].iloc[0]
st.subheader(f"Green Composition for Postcode {selected_postcode}")

col1, col2 = st.columns(2)

with col1:
    st.metric("🌳 Trees (%)", f"{row['percentagetrees']:.2f}%")
    st.metric("🌿 Bushes (%)", f"{row['percentagebushes']:.2f}%")
    st.metric("🍀 Grass (%)", f"{row['percentagegrass']:.2f}%")
    st.metric("🟩 Total Green", f"{row['total_green']:.2f}%")
    st.metric("⚖️ Green Std Dev (Imbalance)", f"{row.get('green_std', 0):.2f}")  # Optional if green_std missing

with col2:
    fig = px.bar(
        x=["Trees", "Bushes", "Grass"],
        y=[row['percentagetrees'], row['percentagebushes'], row['percentagegrass']],
        labels={"x": "Green Type", "y": "Percentage"},
        title="🌱 Green Type Distribution",
        color_discrete_sequence=["darkgreen"]
    )
    st.plotly_chart(fig, use_container_width=True)

# 🎨 RGB Color Visual
st.subheader("🖼️ Visual Green Fingerprint (RGB Color)")
st.markdown("Each postcode's green mix is mapped to a color. This gives a **quick visual identity** for its green composition.")

# 🌈 Explanation
st.markdown(
    """
    **What does this color mean?**  
    - Each green type is assigned to a primary light color:  
      🌳 Trees → **Red**, 🌿 Bushes → **Green**, 🍀 Grass → **Blue**  
    - The more of one type, the more that color is dominant.  
    - So a **purplish tone** means trees and grass dominate but bushes are low! You can see postcode 1011 as a nice example!
    """
)

# 🌟 Color block and HEX code
st.markdown(f"""
<div style='
    background-color:{row["color"]};
    width:200px;
    height:100px;
    border:2px solid #444;
    border-radius:8px;
    display:inline-block;
    margin-bottom:0.5em;'>
</div>
<p style='font-size:18px;'>Hex Code: <code>{row["color"].upper()}</code></p>
""", unsafe_allow_html=True)

# 📊 Extra plot: Total Green vs Std Dev
if 'green_std' in df.columns:
    st.subheader("📉 Compare All Postcodes")

    scatter = px.scatter(
        df,
        x="green_std",
        y="total_green",
        hover_name="postcode",
        color="color" if "color" in df.columns else None,
        color_discrete_map="identity",
        title="Green Imbalance vs Total Green by Postcode",
        labels={"green_std": "Standard Deviation (Imbalance)", "total_green": "Total Green (%)"}
    )
    scatter.update_traces(marker=dict(size=8, line=dict(width=0.5, color='DarkSlateGrey')))
    st.plotly_chart(scatter, use_container_width=True)

st.markdown("---")
st.markdown("📌 *Note: RGB color is calculated from the proportion of trees (R), bushes (G), and grass (B).*")
