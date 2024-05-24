from pydantic import BaseModel, Field
from datetime import date, time, datetime

class UsuarioInsert(BaseModel):
    nombre: str
    correo: str
    estatus: str= Field(default="A")
    contrasena:str
class Almacen(BaseModel):
    idPersonaje:int
    fecha_agregado:date
class PurchaseDetail(BaseModel):
    idPersonaje:str
    precio:float=Field(...,gt=0)
class Compra (BaseModel):
    numTarjeta:str
    cvc:str
    anioExpiracion:int=Field(...,gt=2024)
    mesExpiracion:int=Field(...,gt=0)
    subtotal:float=Field(...,ge=0)
    total:float=Field(...,gt=0)
    fechaCompra:datetime=Field(default=datetime.today())
    idUsuario:str
    detalleCompra:list [PurchaseDetail]
class Particioner(BaseModel):
    idUsuario:str
    idPersonaje:str
class Participantes (BaseModel):
    estatus:str=Field(default="Game")
    ganador:bool=Field(default=False)
    usuario:Particioner
class Partida (BaseModel):
    duracion:float=Field(default=0.00)
    fechaInicio:str=Field(default=str(date.today()))
    fechaTerminacion:str=Field(default=str(date.today()))
    horaInicio:str=Field(default=str(datetime.now().time()))
    horaFin:str=Field(default=str(datetime.now().time()))
    estatus:str=Field(default="A")
    cupoMinimo:int=Field(default=3)
    cupoMaximo:int=Field(default=6)
    participantes:list[Participantes]
class PersonajeInsertar (BaseModel):
    nombre:str
    precio: float=Field(...,gt=0)
    imagen:str
    estatus:str=Field(default="A")
class PersonajeActualizar (BaseModel):
    nombre:str
    precio: float=Field(...,gt=0)
    imagen:str
    estatus:str=Field(default="A")


