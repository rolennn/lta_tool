# Generate_Template_(Single).py

import shutil
import os

import streamlit as st
import test_process as tp

# page configuration
st.set_page_config(
    page_title="Generate Template (Single)",
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
	'4', '5', '6', '7', '8', '9', '10'
]


st.title("Generate Template (Single)")

# input container
with st.container():
	inp1, inp2, inp3, inp4 = st.columns(4)
	with inp1: 
		course_code = st.selectbox("course_code", COURSES)
	with inp2:
		lt_num = st.selectbox("lt_number", LTNUMS)
	with inp3: 
		lt_date = st.date_input(
			label="lt_schedule", 
			value="today", 
			help="If you are unsure about the exact date of the test, input January 1 of the year."
		)
	with inp4:
		num_probs = st.number_input(
			label="no. of problems", 
			min_value=1, 
			step=1,
			help="Please include only the highest level of enumeration (i.e. do not count the sub-problems)")
	profs = st.text_input(
		label="professors (last names, comma-separated)",
		value="Unknown",
		help="If the professor is unknown, input 'Unknown' (without the apostrophes)."
	)
	inp5, btn = st.columns([0.80, 0.20])
	with inp5:
		sources = st.file_uploader(
			label="test source",
			type=['png', 'jpg', 'jpeg', 'pdf'],
			accept_multiple_files=True
		)
	with btn:
		generate = st.button("Generate Template Materials", type="primary")
	
if (generate):
	
	# instantiate Test object
	context = {
		'course_code': course_code, 
		'lt_number': lt_num, 
		'lt_schedule': lt_date, 
		'num_probs': num_probs, 
		'professors': profs
	}
	test = tp.Test(context)
	
	# create content with template (to be put in the .tex file)
	template_content = test.get_template()
	
	# if there are sources, create .zip for ocr results
	with_sources = (sources != [])
	if (with_sources):
		contents = test.process_ocr(sources)
		num_content = len(contents)
		
		rootpath = os.path.join("_data", "from_ocr")
		for (pair, i) in zip(contents, range(1, num_content+1)):
			pair[0].save(os.path.join(rootpath, "images", f"page{i}.png"))
			with open(os.path.join(rootpath, "texts", f"page{i}.txt"), "w+") as textfile:
				textfile.write(pair[1])
		shutil.make_archive(rootpath, "zip", rootpath)
	
	# download output container
	with st.container():
		down1, down2, down3 = st.columns(3)
		with down1:
			st.download_button(
				label="Download TEMPLATE",
				data=template_content,
				file_name=f"{test.filename}.tex",
				mime="application/tex",
				help="Download the a template .tex file with the inputted information in the format.",
			)
		with down2:
			if (with_sources):
				with open(os.path.join("_data", "from_ocr.zip"), "rb") as ocr_results:
					st.download_button(
						label="Download OCR RESULTS",
						data=ocr_results,
						file_name="orc_results.zip",
						mime="application/zip",
						help="Download the a .zip file containing the results of the OCR.",
					)
			else:
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

	# show output containers:
	# each page will have a container for the image and text results
	# if there is no source provided, just output the template_content
	if (with_sources):
		for (pair, i) in zip(contents, range(1, num_content+1)):
			with st.container(height=300):
				st.image(pair[0])
			with st.container():
				st.text_area(
					label=f"page{i} (ocr result)",
					value=pair[1],
					height=300,
				)
	else:
		with st.container():
			st.text_area(
				label="template tex file",
				value=template_content,
				height=300,
			)
