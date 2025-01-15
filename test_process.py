# test_process.py

import os
import io
import shutil
import datetime

import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pytesseract as pt
import pymupdf as ppdf
from PIL import Image


# auxilliary functions
def to_datetime(obj):
	is_str = isinstance(obj, str)
	if (is_str):
		res = datetime.datetime.strptime(obj, "%d %B %Y")
	else:
		res = obj
	return res

def format_date(date, purp="header"):
	if (purp == "header"):
		if (date.month == 1 and date.day == 1):
			return date.strftime('%Y')
		else:
			return date.strftime('%d %B %Y')
	elif (purp == "filename"):
		# TODO: find a way to incorporate semesters in this formatting
		return date.strftime('[%Y]')
	
def format_testnum(test_num, purp="header"):
	if (purp == "header"):
		if (test_num in ["Midterms", "Finals", "Unsure"]):
			return f"{test_num} Exam"
		else:
			return f"Long Test {test_num}"
	elif (purp == "filename"):
		return f"LT {test_num}"
		
def format_profs(profs, purp="header"):
	if (purp == "header"):
		return ", ".join(profs)
	elif (purp == "filename"):
		if (len(profs) > 2):
			return "Departmental"
		return ", ".join(profs)
		

class Test: 
	def __init__(self, context):
		self.course_code = str(context['course_code'])
		self.test_num = str(context['lt_number'])
		self.profs = [name.strip() for name in context['professors'].split(',')]
		self.date = to_datetime(context['lt_schedule'])
		self.num_probs = int(context['num_probs'])
		
		self.filename = " ".join([
			format_date(self.date, purp="filename"),
			self.course_code, 
			format_testnum(self.test_num),
			format_profs(self.profs, purp="filename")
		])
		self.for_hash = "_".join([
			self.course_code,
			format_testnum(self.test_num, purp="header"),
			format_date(self.date, purp="header"),
			format_profs(self.profs, purp="header")
		])
		self.probs = ["\t"] + [f"{num}}} Problem {num} \pts{{Unk}}" for num in range(1, self.num_probs + 1)]
		
	def __str__(self):
		return self.filename
		
	def get_template(self):
		env = Environment(loader=FileSystemLoader("_data/"))
		template = env.get_template("template_prob.txt")
		content = template.render(
			course_code = self.course_code,
			test_code = format_testnum(self.test_num),
			professor = format_profs(self.profs, purp="header"),
			exam_date = format_date(self.date, purp="header"),
			problems = self.probs,
			filename = self.filename
		)
		return content
	
	# get the PIL image file from a source file (pdf or image)
	def get_img(self, source):
		images = []
		if (source.type == "application/pdf"):
			with ppdf.open(stream=source.read(), filetype="pdf") as doc:
				for page in doc:
					stream = page.get_pixmap().pil_tobytes(format="png", optimize=True)
					page_img = Image.open(io.BytesIO(stream))
					images.append(page_img)
		else:
			page_img = Image.open(source)
			images.append(page_img)
		return images
	
	# get a pair (img, txt) containing the result of ocr
	def get_ocr(self, images):
		res = []
		for page_img in images:
			page_txt = pt.image_to_string(page_img)
			res.append((page_img, page_txt))
		return res
	
	# wrapper function to be called for multiple sources
	def process_ocr(self, sources):
		contents = []
		for source in sources:
			contents += self.get_ocr(self.get_img(source))
		return contents
