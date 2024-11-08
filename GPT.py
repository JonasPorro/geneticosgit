import csv
import requests
import json

def get_summary(summary):
  simulationData = ""
  with open('creaturestmp.csv', newline='') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    for row in lines:
      simulationData += ','.join(row) + ';'
    
  response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
      "Authorization": "Bearer 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",
    },
    data=json.dumps({
      "model": "meta-llama/llama-3.1-70b-instruct:free", # Optional
      "messages": [
        {
          "role": "user",
          "content": f"""Analiza la siguiente información separada por "," y donde cada fila está finalizada con ";" obtenida luego de realizar una simulación de algoritmos 
          genéticos de criaturas que deben comer para reproducirse y sobrevivir. Existen criaturas carnivoras y hervivoras. El tiempo de vida está medido en segundos.
          las hervivoras intentan huir de las carnivoras. También tienen personalidades que influyen en su forma de actuar.
          Saltea la introducción, ve directo al análisis. Tu respuesta debe narrar lo que sucedió en la simulación. 
          Al final de la narración genera una conclusión. Evita comenzar con "en el principio eran x criaturas" o cosas por el estilo.
          Por favor haz un salto de línea cada aproximadamente 50 caracteres en tu respuesta. 
          Datos: {simulationData}"""
        }
      ]   
    })
  )
  
  cleanResponse = json.loads(response.content)
  print(cleanResponse['choices'][0]['message']['content'])
  summary.append(cleanResponse['choices'][0]['message']['content'])