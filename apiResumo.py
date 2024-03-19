import PyPDF2
import httpx
from openai import OpenAI
from flask import Flask, Response, abort
import os
import docx2txt
import json
# import tempfile
# import tiktoken
# import requests

# curl -X POST http://10.32.109.36:5000/resumoPGM requisição da api

proxy_url = os.environ.get("OPENAI_PROXY_URL")
print(proxy_url)
client = OpenAI() if proxy_url is None or proxy_url == "" else OpenAI(http_client=httpx.Client(proxy=proxy_url))

app = Flask(__name__)

resumos = {}

# custo_acumulado = [0]

# def num_tokens_from_string(string: str, encoding_name: str) -> int:
#   encoding = tiktoken.get_encoding(encoding_name)
#   num_tokens = len(encoding.encode(string))
#   return num_tokens

def extract_text_from_word(word_file):
  word_text = docx2txt.process(word_file)
  return word_text

def extract_text_from_pdf(pdf_file):
  pdf_text = ""
  pdf_reader = PyPDF2.PdfReader(pdf_file)
  for page in pdf_reader.pages:
    pdf_text += page.extract_text()
  return pdf_text


@app.route('/resumoPGM', methods=['GET'])
def get_resumos():
    resumos_json = json.dumps(resumos, indent=6, ensure_ascii=False)
    return Response(resumos_json, mimetype='application/json')
    


@app.route('/resumoPGM', methods=['POST'])
def resposta():
    
    folder_path = r'C:\Users\3470622\Desktop\Workspace\pdfs'  # Caminho do diretório
        

    caminho_os = os.path.isdir(folder_path)
    caminho_dir = os.listdir(folder_path)
        
    if not caminho_os:
        abort(500, "O diretório de documentos não existe.")

    if caminho_os:
        for arquivo in caminho_dir:         
            caminho_arquivos = os.path.join(folder_path, arquivo)
                
            file_path = caminho_arquivos

            if file_path.endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif file_path.endswith('.docx'):
                text = extract_text_from_word(file_path)
                
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": "Você é especialista em resumir informações de documentos e extrair minuciosamente as informações pedidas."},
                    {"role": "user", "content": "Resuma o arquivo."},
                    {"role": "assistant", "content": text}
                ]
            )
            
            resumos[arquivo] = {"resposta" : completion.choices[0].message.content}
    
    resumos_json = json.dumps(resumos, indent=6, ensure_ascii=False)
    return Response(resumos_json, mimetype='application/json')

    
if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=False)





