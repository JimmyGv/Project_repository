from fastapi import FastAPI
import uvicorn
from dao import Connect
from models import UsuarioInsert, PersonajeInsertar, PersonajeActualizar, Compra, Partida, Participantes

app = FastAPI()

@app.on_event('startup')
def startup():
    app.conn=Connect()
    print("Connecting BD")
@app.on_event('shutdown')
def shutdown():
    app.conn.cerrar()
    print("Disconnecting BD")

@app.get("/")
def inicio():
    return {"message": "Welcome to GameREST services :)"}

@app.post('/usuarios/crear')
def agregarUsuario(usuar: UsuarioInsert):
    salida = app.conn.crearUsuario(usuar)
    return salida

@app.delete('/usuarios/eliminar/{idUsuario}')
def eliminarUsuario(idUsuario:str):
    salida = app.conn.eliminarUser(idUsuario)
    return salida

@app.put('/usuarios/actualizar/{idUsuario}')
def actualizarUsuario(idUsuario:str, nombre:str, contrasena:str):
    salida = app.conn.actualizarUser(idUsuario,nombre,contrasena)
    return salida

@app.get('/usuarios/autenticar')
def autenticarUsuario(correo:str, contrasena:str):
    salida = app.conn.Login(correo,contrasena)
    return salida

@app.get('/usuarios/consultar')
def consultarUsuarios():
    salida = app.conn.consultaGeneralUsers()
    return salida

@app.get('/usuarios/consultar/{idUsuario}')
def consultarUsuarioId(idUsuario:str):
    salida = app.conn.constultaUserById(idUsuario)
    return salida

@app.post('/personajes/crear')
def agregarPersonaje(personaje: PersonajeInsertar):
    salida = app.conn.crearPersonaje(personaje)
    return salida

@app.put('/personajes/actualizar/{idPersonaje}')
def actualizarPersonaje(idPersonaje:str, personaje: PersonajeActualizar):
    salida = app.conn.actualizarPersonaje(idPersonaje,personaje)
    return salida

@app.delete('/personajes/eliminar/{idPersonaje}')
def eliminarPersonaje(idPersonaje:str):
    salida = app.conn.eliminarPersonaje(idPersonaje)
    return salida

@app.get('/personajes/consultar')
def consultarPersonajes():
    salida = app.conn.consultarPersonajes()
    return salida

@app.get('/personajes/consultar/{idPersonaje}')
def consultarPersonajeById(idPersonaje:str):
    salida = app.conn.consultarPersonajeById(idPersonaje)
    return salida

@app.post('/compras/realizar_compra')
def realizarCompra(compra: Compra):
    salida = app.conn.realizarCompra(compra)
    return salida

@app.get('/compras/consultar')
def consultaCompras():
    salida = app.conn.consultarCompras()
    return salida

@app.get('/compras/consultar/{idCompra}')
def consultarCompraId(idCompra:str):
    salida = app.conn.consultarCompraById(idCompra)
    return salida

@app.post('/partida/crearPartida')
def realizarPartida(partida: Partida):
    salida = app.conn.crearPartida(partida)
    return salida

@app.put('/partida/{idPartida}/finalizarPartida')
def finalizar_partida(idPartida:str, idGanador: str):
    salida = app.conn.finalizarPartida(idPartida,idGanador)
    return salida

@app.put('/partida/agregarParticipante/{idPartida}')
def finalizar_partida(idPartida:str, participante: Participantes):
    salida = app.conn.agregarParticipante(idPartida,participante)
    return salida

@app.get('/partidas/consultar')
def consultar_Partidas():
    salida = app.conn.consultarPartidas()
    return salida

@app.get('/partida/consultar/{idPartida}')
def consultarPartidaId(idPartida:str):
    salida = app.conn.consultarPartidaById(idPartida)
    return salida