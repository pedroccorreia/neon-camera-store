import streamlit as st
from streamlit_image_comparison import image_comparison




# set page config
st.set_page_config(page_title="Image-Comparison Example", layout="centered")

st.write('Functionality being developed')


if visible:
    with st.container():
        # render image-comparison
        image_comparison(
            img1="images/bread_1.jpg",
            label1="09.30",
            img2="images/bread_2.jpg",
            label2="09.45",
            width=900,
            starting_position=90,
        )

        cols = st.columns(4)
        cols[1].text('First Run')
        cols[2].text('Second Run')
        cols[3].text('Difference')

        cols = st.columns(4)
        cols[0].text('Product Facings')
        cols[1].text( "180")
        cols[2].text("140")
        cols[3].text("-80")


        cols = st.columns(4)
        cols[0].text('Unique Products')
        cols[1].text("20")
        cols[2].text("18")
        cols[3].text("-2")


        cols = st.columns(4)
        cols[0].text('Unidentified Products')
        cols[1].text("2")
        cols[2].text("2")
        cols[3].text("0")

        cols = st.columns(4)
        cols[0].text('Pushbacks Detected')
        cols[1].text("5")
        cols[2].text("8")
        cols[3].text("+3")