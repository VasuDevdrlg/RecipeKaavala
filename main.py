import ast
import requests
from flask import Flask,render_template,request
import os
import google.generativeai as genai
api="AIzaSyBVOpDlIL0s-qWRfRl1QM9LBc9FhmAlmDo"
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api)
model = genai.GenerativeModel('gemini-1.5-flash')
import re

def extract_ingredient_details(ingredients_list):
    ingredient_details = []
    for ingredient in ingredients_list:
        match = re.match(r'(\d+[^ ]*) ([^ ]+) (.+)', ingredient)
        if match:
            quantity = match.group(1)
            unit = match.group(2)
            item = match.group(3)
            ingredient_details.append({"quantity": quantity, "unit": unit, "item": item})
        else:
            ingredient_details.append({"quantity": "", "unit": "", "item": ingredient})
    return ingredient_details

def extract_instructions(instructions):
  match = re.search(r'instructions\s*=\s*(\[[^\]]+\])', instructions)
  if match:
    instructions_str = match.group(1)

    instructions_list = ast.literal_eval(instructions_str)
    
  
    instruction_dicts = [{"step": i + 1, "instruction": step} for i, step in enumerate(instructions_list)]
    return instruction_dicts

def process_recipe(ingredients_part, instructions_list):
    ingredients_list = re.findall(r'\"(.*?)\"', ingredients_part)
    extracted_ingredients = extract_ingredient_details(ingredients_list)
    extracted_instructions = extract_instructions(instructions_list)
    return extracted_ingredients, extracted_instructions

app=Flask(__name__)
@app.route('/')
def index():
  return render_template("index.html")
@app.route('/recipelist',methods=["POST","GET"])
def recipelistt():
  if request.method=='POST':
    namee=request.form["namee"]
    response=requests.get(f"https://api.edamam.com/api/recipes/v2?type=public&q={namee}&app_id=c7976567&app_key=06a4c104e53fcc5e7b57d0f0b217697b")
    data=response.json()
    info=[]
    for i in data['hits']:
      if i['recipe']['source']: #== "BBC Good Food":
        k={
          'title':i['recipe']["label"].title(),
          'type':i['recipe']["mealType"][0].title(),
        'cusine':i['recipe']["cuisineType"][0].title(),
        'cal':i["recipe"]['calories'],
        'img':i['recipe']['image'],
        'items':i['recipe']['ingredientLines'],
        'url':i['recipe']['url']
        }
        info.append(k)
    return render_template('recipelist.html',info=info)
  else:
    return render_template('/recipelist.html',info=None)
@app.route('/recinfo',methods=["POST","GET"])
def foodsteps():
   if request.method=='POST':
      url = request.form.get('rec_url')
      imgu=request.form.get('rec_img')
      title=request.form.get('rec_title')
      typee=request.form.get('rec_type')
      cal=request.form.get('rec_cal')
      cus=request.form.get('rec_cus')
      text=f"Title:{title} Meals Type:{typee}\nCuisine Type:{cus}\n just only give ingredients for this specific recipe as a python list "
      text2=f"Title:{title} Meals Type:{typee}\nCuisine Type:{cus}\n just only give instructions not ingredients for this specific recipe as a python list named instructions give response only in this format no single extra character"
      ingr = model.generate_content(text)
      step=model.generate_content(text2)

      item,matter=process_recipe(ingr.text,step.text)
      return render_template('/recinfo.html',matter=matter,item=item,srcc=imgu,label=title)   
   else:
     return render_template('/recinfo.html',matter=None,item=None,srcc=None,label=None )   
if __name__=='__main__':
  app.run(debug=True)