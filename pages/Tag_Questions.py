# Tag_Questions.py

import os
import json
from datetime import datetime

import streamlit as st
import pandas as pd
import pymupdf as ppdf
import test_process as tp
from streamlit_gsheets import GSheetsConnection

# page configuration
st.set_page_config(
    page_title="Tag Questions",
    initial_sidebar_state="auto",
    page_icon="_data/ams_logo.jpg"
)

conn = st.connection(
	name="gsheets", 
	type=GSheetsConnection, 
	ttl="5m",
)


DUMMY_CONTEXT = {
	"course_code": "MATH 00", 
	"lt_number": "Finals",
	"lt_schedule": "01 January 2025",
	"num_probs": "1",
	"professors": "Unknown",
}

with open(os.path.join("_data", "tags.json"), "r") as tags_file:
	tags_dict = json.loads(tags_file.read())
TAGS = pd.DataFrame(data=tags_dict)


def get_num_prob(test_id, df):
	num_prob = 1
	if (test_id != "0000000000"):
		num_ser = df.loc[df['test_id'] == test_id, 'num_probs']
		num_prob = int(num_ser.iloc[0])
	return num_prob
	
def create_df(num_probs):
	index = [f"P{item}" for item in range(1, num_probs+1)]
	data = {
		'sub_items': [0 for _ in range(num_probs)],
		'tags': ['' for _ in range(num_probs)],
		'notes': ['' for _ in range(num_probs)],
	}
	df = pd.DataFrame(data=data, index=index)
	df = df.rename_axis('item')
	return df
	
def log_row(test_id, num_probs, content, name):
	data = pd.DataFrame(
		[[test_id, num_probs, content, name, datetime.now()]],
		columns=['test_id', 'num_probs', 'tag_json', 'tagger', 'time']
	)
	return data


st.title("Tag Questions")

with st.container():
	name = st.text_input(
		label="your_name",
		value="anonymous",
		help="If you do not want to include your name, you will be credited as 'anomynous'."
	)
	inp2, btn = st.columns([0.85, 0.15])
	with inp2: 
		sources = st.file_uploader(
			label="test_source",
			type=['pdf', 'png', 'jpg', 'jpeg'],
			accept_multiple_files=True,
			help="Please input a .pdf file of the test, ideally the formatted one. Multiple files are accepted."
		)
	with btn:
		btn1 = st.button("Try an example")

with st.expander(label="tagging guide:", expanded=False, icon=":material/developer_guide:"):
	st.write("Please tag the items based on the topic/s of the problems. Click `Try an example` above for an example test. You may also refer to the video tutorial in the Welcome page.")
	st.write("Below are the recommended tags for each course. They are taken from the syllabi of the new curriculum. Note that you may add more tags, just make sure that the **sufficiently describe** the topic of the problem.")
	st.write("For any concerns, contact the people at the Welcome page.")
	st.dataframe(
		data=TAGS,
		hide_index=True,
		use_container_width=True,
		column_config={
			'tags': st.column_config.ListColumn(
				label="tag",
				width="large",
			)
		}
	)
	
with st.expander(label="open tests:", expanded=True, icon=":material/inventory_2:"):
	df = conn.read(worksheet="tag_problems")
	st.dataframe(
		data=df,
		use_container_width=True,
		hide_index=True,
	)


test = tp.Test(DUMMY_CONTEXT)
for source in sources:
	imgs = test.get_img(source)
	filename = source.name
		
	with st.expander(label=f"file: {filename}", expanded=False, icon=":material/description:"):
		with st.container(height=300):
			for page in imgs:
				st.image(page)
		with st.container(height=300):
			inp3, btn = st.columns([0.85, 0.15])
			with inp3:
				test_id = st.text_input(
					label="test_id",
					value="0000000000",
					help="Input the test_id of this particular test. Refer to `open test` for the complete list."
				)
			with btn:
				btn2 = st.button("Submit Tags", type="primary")
			num_probs = get_num_prob(test_id, df)
			content = st.data_editor(
				data=create_df(num_probs),
				num_rows="static",
				hide_index=False,
				column_config={
					"sub_items": st.column_config.NumberColumn(
						label="sub_items",
						min_value=0,
						step=1,
						width="small",
						help="Indicate the number of sub-items for this particilar item. Usually, these are enumerated using letter labels."
					),
					"tags": st.column_config.TextColumn(
						label="tags",
						width="medium",
						help="Please separate multiple tags with a comma (`,`). For items with sub-items, please put all tags on the same cell. Refer to the tagging guide for an example.",
					),
					"notes": st.column_config.TextColumn(
						label="notes",
						width="medium",
					)
				},
				use_container_width=True,
			)
		
		if (btn2):
			content_dict = content.to_dict('index')
			new_row = log_row(test_id, num_probs, content_dict, name)
			
			curr_df = conn.read(worksheet="tag_review")
			new_df = pd.concat([curr_df, new_row])
			
			conn.update(worksheet="tag_review", data=new_df)

