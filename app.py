import os
import requests
import streamlit as st

# create a .env file in your project directory and add your hugging face token as:
# HF_API_KEY = "hf_your_token"
# after that uncomment below two lines of code to load the hf api token

# from dotenv import load_dotenv
# load_dotenv()

API_KEY = os.getenv('HF_API_KEY')

headers = {"Authorization": f"Bearer {API_KEY}"}



def image_to_text(image_source):
	salesforce_blip = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
	
	API_URL = salesforce_blip

	with open(image_source, "rb") as f:
		data = f.read()

	response = requests.post(API_URL, headers=headers, data=data)
	response =  response.json()
	
	return response[0]["generated_text"]


def generateStory(inputText):
	# gpt2_xl = "https://api-inference.huggingface.co/models/gpt2-xl"

	#using "falcon 7b instruct" as it is working way better than gpt2 for creating stories
	falcon_7b = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"

	API_URL = falcon_7b

	falcon_text_for_story = f"create a positive, real, practical and short story from this context {inputText}"

	payload = {
				"inputs": falcon_text_for_story,
				"parameters": {
								# "max_length": 2,
								"max_new_tokens": 200,
								"do_sample":True,
								# "max_time": 15.00,
								"top_k": 10,		#total words in text
								"temperature": 1,
								# "repetition_penalty": 80,
								"return_full_text": False,
							  },
				"options": {
							"wait_for_model": True
						   }
			  }
	# print(payload["inputs"])
	
	response = requests.post(API_URL, headers=headers, json=payload)
	response = response.json()

	# print(type(response))
	# print(response,"\n\n")

	# {'error': 'Model gpt2-large is currently loading', 'estimated_time': 129.88461303710938} 
	# {'error': 'Internal Server Error'} 

	#  error handling
	if isinstance(response, dict):
		# print(response["error"], "\n\n")
		return response["error"]

	else:
		return response[0]["generated_text"]


def imageToStory():
	st.set_page_config(page_title = "Photo to story", page_icon="👾")
	# emoji shortcut: CTRL + CMD + Space

	#Removing the Menu Button and Streamlit Icon
	hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
	st.markdown(hide_default_format, unsafe_allow_html=True)

	st.title("Photo to story")
	st.header("Turn your photos into a beautiful story")
	st.subheader("Bored of your regular photos...I have a solution for you. Turn your most favourite photos into a \
					beautiful story. Just browse your photo and hit enter and see the magic 🪄")
	st.subheader("Don't worry about your privacy! This app doesn't store anything. Your photo is deleted \
					right after the story is generated🔐")

	# sidebar
	app_tech_stack = "**LLM** :  falcon-7b-instruct"
	how_it_works = "Firstly, it creates a suitable caption for the image uploaded by the user and then \
					it uses a **LLM, falcon-7b,** to create a practical and short story by taking the image caption as context."
	linkedin = "https://www.linkedin.com/in/priyansh-bhardwaj-25964317a"
	about_developer = "Priyansh Bhardwaj"

	with st.sidebar.expander("Tech stack"):
		st.write(app_tech_stack)
	
	with st.sidebar.expander("App Working"):
		st.write(how_it_works)
	
	with st.sidebar.expander("About me"):
		st.write(about_developer)
		st.write("[LinkedIn](%s)" %linkedin)

	uploaded_file = st.file_uploader("choose your photo...", type = ["jpg","png"])

	if uploaded_file is not None:
		bytes_data = uploaded_file.getvalue()
		image_path = "images/"+uploaded_file.name 

		with open(image_path, "wb") as file:
			file.write(bytes_data)
		st.image(uploaded_file, caption="Photo successfully uploaded", use_column_width=True)

		if st.button("Generate Story🪄",
					type="primary",
					help="Click this button to generate a story from your photo"):

			caption = image_to_text(image_path)
			story = generateStory(caption)

			#deleting the images
			for image in os.listdir("images/"):
				file_path = os.path.join("images/", image) 
				os.remove(file_path)

			# with st.expander("Photo caption"):
			# 	st.write(caption)
			with st.expander("Story"):
				st.write(story)
		

if __name__ == "__main__":
	imageToStory()
