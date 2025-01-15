# Generate_Template_(Multiple).py

import shutil
import os
import glob

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import test_process as tp


# page configuration
st.set_page_config(
    page_title="Generate Template (Multiple)",
    initial_sidebar_state="auto",
    page_icon="_data/ams_logo.jpg"
)
COURSES = [
	'MATH 31.1', 'MATH 31.2', 'MATH 31.3', 'MATH 31.4', 'MATH 50.1', 
	'MATH 51.1', 'MATH 40.1', 'MATH 61.2', 'MA 21', 'MA 22', 'MA 101',
	'MA 189', 'MA 124', 'MA 122', 'MA 151'
]
LTNUMS = [
	'Midterms', 'Finals', '1', '2', '3', 
	'4', '5', '6', '7', '8', '9', '10', 'Unsure',
]

conn = st.connection(
	name="gsheets", 
	type=GSheetsConnection, 
	ttl="5m",
)

st.title("Generate Template (Multiple)")

with st.container():
	inp1, btn = st.columns([0.8, 0.2])
	with inp1: 
		source = st.file_uploader(
			label="test_context",
			type=['csv', 'tsv'],
			accept_multiple_files=False,
			help="Please ensure that your file has columns for course_code, lt_number, lt_schedule, num_probs, and professors."
		)
	with btn:
		generate = st.button("Generate Template Materials", type="primary")
		
if (source is not None):
	sep = ('\t' if (source.type == "application/octet-stream") else ',')
	upload_df = pd.read_csv(source, sep=sep)
	df = upload_df.assign(gen=[False for _ in range(upload_df.shape[0])])
else:
	st.write("To create a template for a test, please check the corresponding cell under the `gen` column.")
	gsheet_df = conn.read(worksheet="generate_template")
	df = gsheet_df.assign(gen=[False for _ in range(gsheet_df.shape[0])])
	
editable_df = st.data_editor(
	data=df,
	num_rows="static",
	hide_index=True,
	column_config={
		"test_id": st.column_config.Column(
			label="test_id",
			help="Use this to refer to the test.",
			pinned=True,
			disabled=True,
		),
		"gen": st.column_config.CheckboxColumn(
			label="gen",
			help="Please click this to include the test to the .zip file.",
			required=True,
			pinned=True,
		),
		"num_probs": st.column_config.NumberColumn(
			label="num_probs",
			help="Please include only the highest level of enumeration (i.e. do not count the sub-problems).",
			min_value=1,
			step=1,
		),
		"lt_number": st.column_config.SelectboxColumn(
			label="lt_number",
			options = LTNUMS,
		),
		"course_code": st.column_config.SelectboxColumn(
			label="course_code",
			options = COURSES,
		)
	},
	use_container_width=True,
	column_order=["gen", "test_id", "course_code", "lt_number", "lt_schedule", "professors", "num_probs"]
)
	
if (generate):
	df_dict = editable_df.to_dict("records")
	
	# create a .zip containing all template files;
	# first remove all .tex files in the folder, then proceed 
	# with generating the necessary files
	rootpath = os.path.join("_data", "for_overleaf")
	files = glob.glob(os.path.join(rootpath, "*.tex"))
	for texfile in files:
		os.remove(texfile)
	for context in df_dict:
		if (context['gen']):
			test = tp.Test(context)
			with open(os.path.join(rootpath, f"{test.filename}.tex"), "w+") as template_file:
				template_file.write(test.get_template())
	shutil.make_archive(rootpath, "zip", rootpath)
	
	with st.container():
		down1, down2, down3 = st.columns(3)
		with down1:
			with open(os.path.join("_data", "for_overleaf.zip"), "rb") as templates:
				st.download_button(
					label="Download TEMPLATES",
					data=templates,
					file_name="for_overleaf.zip",
					mime="application/zip",
					help="Download the a .zip file containing .tex files with the inputted information in the format.",
				)
		with down2:
			st.download_button(
				label="Download OCR RESULTS",
				data="There is no file",
				file_name="orc_results.txt",
				mime="text/plain",
				help="Download the a .zip file containing the results of the OCR.",
				disabled=True
			)
		with down3: 
			with open(os.path.join("_data", "style_resources.zip"), "rb") as stylesheet:
				st.download_button(
					label="Download STYLESHEET",
					data=stylesheet,
					file_name="style_resources.zip",
					mime="application/zip",
					help="Download the a .zip file containing the stylesheet and template images.",
				)
	
