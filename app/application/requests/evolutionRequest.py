from pydantic import BaseModel


class EvolutionApiTextRequest(BaseModel):
    number: str
    text: str

class Options(BaseModel):
    delay: str
    presence: str

class EvolutionApiImageRequest(BaseModel):
    options: Options
    number:str
    mediatype: str
    fileName: str
    caption: str
    media: str



#     ##{
#   "options": {
#     "delay": 10000,
#     "presence": "composing"
#   },
#   "number": "{{ $('Tratamento').item.json.numCliente }}",
#     "mediatype": "image",
#     "fileName": "{{ $('Retornar item em array').item.json.imageName }}.jpeg",
#     "caption": "{{ $('Retornar item em array').item.json.imageName }}",
#     "media" :"{{ $('Retornar item em array').item.json.imageUrl }}"

# } 
