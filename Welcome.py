# Welcome.py

import os
import shutil

import streamlit as st

# page configuration
st.set_page_config(
    page_title="Welcome",
    initial_sidebar_state="auto",
    page_icon="_data/ams_logo.jpg"
)
# create a .zip for stylesheet; will be used by other pages
rootpath = os.path.join("_data", "style_resources")
shutil.make_archive(rootpath, "zip", rootpath)

LINKS = {
	'sted': None,
	'kim': None,
	'rolen': None,
	'sample': "https://www.overleaf.com/read/mbmrwxqpvmws#cd2432",
	'tesseract': "https://github.com/tesseract-ocr/tesseract",
	'copilot': "https://copilot.microsoft.com/"
}


st.title("AMS Long Test Archive Webtool")
st.write(f"""
Hello! Welcome, person.

This project aims to simplify the process of generating templates and tagging problems from our long test archive. If this is your first time here, please take the time to **view the materials below before proceeding to the corresponding tool pages**. 

For questions, comments, contributions, and the like regarding the Long Test Archive, please message [Sted Cheng]({LINKS['sted']}), [Kim Veranga]({LINKS['kim']}), or [Rolen Muana]({LINKS['rolen']}). For concerns regarding this webtool, please directly message Rolen Muana.

Thank you!
""")

with st.expander(label="I want to GENERATE TEMPLATES (and typeset LTs)", expanded=False,icon=":material/edit_document:"):
	st.write("There are two ways to generate templates depending on the number of tests you want to process. The following video discusses these options: ")
	st.write("<video on how GENERATE TEMPLATES works here>")
	st.write("To familiarize yourself with the conventions, please view the following: ")
	st.write("<video on MACROS/TYPESETTING REMINDERS here>")
	st.markdown(f"""
	**Miscellaneous Notes**:
	- For reference on how the templates and stylesheets can be used and organized, please [access this Overleaf project]({LINKS['sample']}).
	- This webtool uses [Tesseract]({LINKS['tesseract']}) to recognize the text in the uploaded files. While useful for plain text, it is not ideal for math mode. You are invited to try other options for optical character recognition (OCR) such as [Microsoft Copilot]({LINKS['copilot']}).
	- The tables update **every 5 minutes**, so your changes might not immediately take effect.
	""")

with st.expander(label="I want to TAG PROBLEMS", expanded=False, icon=":material/tag:"):
	st.write("The following video discusses the tagging part of this webtool. Please note that for the sake of organization, you may only tag tests that have **already been typeset and published in the archive**. The list of these available tests can be found in the Tag Questions page.")
	st.write("<video on TAGGING PROBLEM here>")





