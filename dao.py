from pymongo import MongoClient
from models import UsuarioInsert,PersonajeInsertar, PersonajeActualizar,Compra,Partida, Participantes
from bson import ObjectId
from datetime import datetime, date

class Connect:
    def __init__(self):
        self.cliente=MongoClient()
        #------------------self.bd para relizar la conexion con la bd y realizar las operaciones-------
        self.bd=self.cliente.SurviveGame
    def cerrar(self):
        #-----------------Cerrar la conexion con la base de datos-------------------------
        self.cliente.close()
    def crearUsuario(self, usuario : UsuarioInsert):
        answer= {"Estatus":"" , "Message":""} 
        #------------------comprobar si el usuario ya existe-----------------------
        if self.comprobarUser(usuario.correo) == 0:
            #------------------Insertar el usuario en la base de datos-----------------------
            self.bd.usuario.insert_one(usuario.dict())
            answer["Estatus"]="OK"
            answer["Message"]="Usuario creado exitosamente"
        else:
            answer["Estatus"]= "Error"
            answer["Message"]="El Usuario que se intenta crear ya existe"
        return answer
    def comprobarUser(self, correo):
        #----------------------Comprobar si el usuario existe por el correo--------------------
        count = self.bd.usuario.count_documents({"correo": correo})
        return count
    def actualizarUser(self, idUser ,nombre, contrasena):
        answer= {"Estatus":"" , "Message":""}
        #------------------comprobar si el usuario existe-----------------------
        if self.comprobarUserById(idUser)>0:
            #------------------Crear una variable con un nuevo estatus-----------------------
            state = {"nombre":nombre, "contrasena":contrasena}
            #------------------Actualizar el usuario en la base de datos con su nuevo estatus-----------------------
            #------------------self.bd realiza la parte de la conexion para la acciones despues del punto sigue el nombre de la collecion
            #------------------y por ultimo la accion que se desea realizar, dentro de las llaves se pone porque campo se va a consultar 
            #------------------este debe ser unico para evitar errores, luego si es una actualizacion se debe poner $set, $addToSet, $unSet, etc.
            #------------------El ObjectId es para convertir el id que se recibe en un objeto de mongo
            self.bd.usuario.update_one({"_id":ObjectId(idUser)},{"$set":state})
            #------------------Obtener el usuario actualizado-----------------------
            #------------------projection es para que no se muestren los datos que no se quieren mostrar------------------
            user = self.bd.usuario.find_one({"_id":ObjectId(idUser)},projection={"nombre":True,"correo":True,"estatus":True,"_id":False})
            answer["Estatus"]="OK"
            answer["Message"]="Usuario actualizado exitosamente"
            answer["Usuario"]=user
        else:
            answer["Estatus"]= "Error"
            answer["Message"]="El Usuario que se intenta actualizar no existe"
        return answer

    def Login(self, correo,contrasena):
        answer={"Estatus":"","Message":""}
        #------------------comprobar si el usuario existe-----------------------
        #------------------Cuando es de manera local, es decir que se quiere utilizar una funcion dentro de la misma clase-----------------------
        #------------------se utiliza solamente self. y el nombre de la funcion que se quiere realizar seguido de parentesis-----------------------
        #------------------y se le dan los valores que la funcion requiere para poder realizar la funcion-----------------------
        nombre_usuario = self.comprobarLogin(correo,contrasena)
        if (nombre_usuario != ''):
            #------------------Obtener el usuario-----------------------
            usuario = self.bd.usuario.find_one({"correo":correo,"contrasena":contrasena},projection={"nombre":True,"correo":True,"estatus":True,"_id":False})
            answer["Estatus"]= "OK"
            answer["Message"]="Usuario encontrado"
            #------------------Se puede agregar mas datos al diccionario no importa la cantidad o si son objetos, solo cambia cuando es una lista de objetos-----------------------
            answer["nombre_usuario"] = "Bienvenido: " + str(nombre_usuario)
            answer["Usuario"]=usuario
        else:
            answer["Estatus"]= "Error"
            answer["Message"]="Usuario no encontrado"
        return answer

    def comprobarLogin(self, correo,contrasena):
        username=''
        #------------------Se puede utilizar el metodo find_one para obtener un solo objeto, en este caso se esta obteniendo el nombre del usuario-----------------------
        username = self.bd.usuario.find_one({"correo":correo,"contrasena":contrasena},projection={"nombre":True,"_id":False})
        return username
    def comprobarUserById(self, id):
        #------------------Se puede utilizar el metodo count_documents para obtener la cantidad de documentos que cumplen con la condicion-----------------------
        #------------------En este caso se esta obteniendo la cantidad de documentos que cumplen con la condicion de que el id sea igual al id que se le esta pasando-----------------------
        count = self.bd.usuario.count_documents({"_id": ObjectId(id)})
        return count
    def eliminarUser(self, idUser):
        answer= {"Estatus":"" , "Message":""}
        #------------------Se comprueba si el usuario existe con el metodo o funcion de comprobarUserById----------------------
        if self.comprobarUserById( ObjectId(idUser))>0:
            state = {"estatus":"I"}
            #------------------Se actualiza el estado del usuario con el metodo update_one----------------------
            self.bd.usuario.update_one({"_id":ObjectId(idUser)},{"$set":state})
            answer["Estatus"]="OK"
            answer["Message"]="Usuario eliminado exitosamente"
        else:
            answer["Estatus"]= "Error"
            answer["Message"]="El Usuario que se intenta eliminar no existe"
        return answer
    def consultaGeneralUsers(self):
        answer={"Estatus":"" , "Message":""}
        #------------------Se utiliza el metodo find para obtener todos los documentos que cumplen con la condicion----------------------
        #------------------En este caso se obtienen los documentos que tienen un estatus de activo-----------------------
        result=self.bd.consultarUsuarios.find({"estatus":"A"})
        answer["Estatus"]="OK"
        answer["Message"]="Usuarios encontrados"
        listilla=[]
        #------------------Se recorre el resultado de la consulta y se agregan a una lista----------------------
        for i in result:
            #------------------Se realiza este casteo de indices o id debido a que cuando se quieren mostrar los ObjectId tienen problemas para ser mostrados---------------
            i["ID_Usuario"]=str(i["ID_Usuario"])
            #con este metodo de append se agrega lo que se haya modificado en el objeto i en este caso el id usuario aparecera como string y no como ObjectId------------------
            listilla.append(i)
        answer["Usuarios"]=listilla
        return answer
    def constultaUserById(self, idUser):
        #------------------Se utiliza el metodo find_one para obtener un documento que cumpla con la condicion----------------------
        #------------------En este caso se obtiene el documento que tiene el id que se le pasa como parametro-----------------------
        user=self.bd.usuario.find_one({"_id":ObjectId(idUser)},projection={"nombre":True,"correo":True,"estatus":True,"_id":False})
        return user
    def crearPersonaje(self,personaje:PersonajeInsertar):
        answer= {"Estatus":"" , "Message":""} 
        if self.comprobarExistencia(personaje.nombre)>0:
            answer["Estatus"]="Error"
            answer["Message"]="Un personaje con este nombre ya existe"
        else:
            #------------------Se utiliza el metodo insert_one para insertar un documento en la coleccion----------------------
            #------------------En este caso se inserta el personaje que se le pasa como parametro------------------------
            #------------------Se utiliza el metodo dict para convertir el objeto en un diccionario digerible para mongo----------------------
            self.bd.personaje.insert_one(personaje.dict())
            answer["Estatus"]="OK"
            answer["Message"]="Personaje creado exitosamente"
        return answer
    def comprobarExistencia(self,nombre):
        #------------------Se utiliza el metodo count_documents para contar la cantidad de documentos que cumplen con la condicion----------------------
        #------------------En este caso se cuenta la cantidad de documentos que tienen el nombre que se le pasa como parametro------------------------
        count = self.bd.personaje.count_documents({"nombre":nombre})
        return count
    def comprobarExistenciaById(self,idPers):
        count = self.bd.personaje.count_documents({"_id":ObjectId(idPers)})
        return count
    def actualizarPersonaje(self, idPersonaje, personaje:PersonajeActualizar):
        answer= {"Estatus":"" , "Message":""}
        if self.comprobarExistenciaById(idPersonaje)>0:
            #------------------Se utiliza el metodo update_one para actualizar un documento en la coleccion----------------------
            #------------------En este caso se actualiza el personaje que se le pasa como parametro------------------------
            #------------------Se utiliza el metodo dict para convertir el objeto en un diccionario digerible para mongo----------------------
            self.bd.personaje.update_one({"_id":ObjectId(idPersonaje)},{"$set":personaje.dict()})
            resul=self.bd.personaje.find_one({"_id":ObjectId(idPersonaje)},projection={"_id":False})
            answer["Estatus"]="OK"
            answer["Message"]="El personaje se ha modificado correctamente"
            answer['Personaje']=resul
        else:
            answer["Estatus"]="Error"
            answer["Message"]="El personaje que se intenta modificar no existe"
        return answer
    def eliminarPersonaje(self,idPersonaje):
        answer= {"Estatus":"" , "Message":""}
        if self.comprobarExistenciaById(idPersonaje)>0:
            state={"estatus":"I"}
            self.bd.personaje.update_one({"_id":ObjectId(idPersonaje)},{"$set":state})
            answer["Estatus"]="OK"
            answer["Message"]="El personaje se ha eliminado correctamente"
        else:
            answer["Estatus"]="Error"
            answer["Message"]="El personaje que se intenta eliminar no existe"
        return answer
    def consultarPersonajes(self):
        personajes=self.bd.personaje.find({"estatus":"A"})
        listilla=[]
        for i in personajes:
            i["_id"]=str(i["_id"])
            listilla.append(i)
        answer={"personajes":""}
        answer["personajes"]=listilla
        return answer
    def consultarPersonajeById(self,idPersonaje):
        personaje=self.bd.personaje.find_one({"_id":ObjectId(idPersonaje)})

        personaje["_id"]=str(personaje["_id"])
        return personaje
        #if personaje["estatus"] == "A":
            #personaje["_id"]=str(personaje["_id"])

            #return personaje
        #else:
            #return "El personaje no existe"
    def existeEnAlmacen(self, idUsuario,idPersonaje):
        user = self.bd.usuario.find_one({"_id":ObjectId(idUsuario)})
        #-----------------Aqui se comprueba si el usuario ya consultado tiene el atributo de almacen----------------------
        #-----------------si es asi recorre el almacen y verifica si existe coincidencia con el idPersonaje-------------------
        #-----------------si existe coincidencia retorna true-----------------------------------------------------------------
        #-----------------si no existe coincidencia retorna false-------------------------------------------------------------
        if user["almacen"]:
            for i in user["almacen"]:
                if i["idPersonaje"] == idPersonaje:
                    return True
        return False
    def realizarCompra(self,compra:Compra):
        answer= {"Estatus":"" , "Message":""}
        #-----------------se establece como referencia importante una vaiable de tipo booleano en falso---------------
        band = True
        #------------------Se comprueba si existe el usuario que quiere realizar la compra------------------------
        if self.comprobarUserById(compra.idUsuario)>0:
            detail=compra.detalleCompra
            #------------------Se recorre cada elemento que contiene detail-----------------------
            for character in detail:
                id_personaje = character.idPersonaje
                #------------------Se comprueba si el personaje existe---------------------------------
                if self.comprobarExistenciaById(id_personaje)>0:
                    #------------------Se comprueba si el personaje ya existe en el almacen del usuario------------------
                    if self.existeEnAlmacen(compra.idUsuario,id_personaje):
                        answer["Estatus"]="Error"
                        answer["Message"]="Un usuario no puede comprar un personaje mas de una vez"
                        band=False
                        break
                    #------------------Se comprueba si el precio del personaje coincide con el precio de la compra------------------
                    personaje=self.consultarPersonajeById(id_personaje)
                    if personaje["precio"]!=character.precio:
                        answer["Estatus"]="Error"
                        answer["Message"]="El precio del personaje no coincide con el precio de la compra"
                        band=False
                        break
                    #------------------Se agrega el precio del personaje al subtotal de la compra------------------
                    compra.subtotal+=personaje["precio"]
                    #print(compra.subtotal)
                else:
                    answer["Estatus"]="Error"
                    answer["Message"]="El personaje no existe"
                    band=False
                    break
            if band:
                #------------------Se comprueba si el total de la compra es igual o mayor al subtotal------------------
                if compra.total == compra.subtotal or compra.total > compra.subtotal:
                    #------------------Se inserta la compra en la base de datos y se trae el resultado------------------
                    result = self.bd.compra.insert_one(compra.dict())
                    
                    detallito=compra.detalleCompra
                    for obj in detallito:
                        id_pers = obj.idPersonaje
                        #print(id_pers)
                        #------------------Se agrega el personaje al almacen del usuario------------------
                        self.agregarAlmacen(compra.idUsuario,id_pers)
                    answer["Estatus"]="OK"
                    #------------------Se regresa el id de la compra------------------
                    answer["Message"]="La compra ha sido realizada con exito con un id: " + str(result.inserted_id)
                    #------------------Se regresa la compra como respuesta------------------
                    answer["Compra"]=compra
                else:
                    answer["Estatus"]="Error"
                    answer["Message"]="El total de la compra es menor que el subtotal"
        else:
            answer["Estatus"]="Error"
            answer["Message"]="El usuario no existe"
        
        return answer
    def agregarAlmacen(self, idUsuario, idPersonaje):
        #------------------Se agrega el personaje al almacen del usuario------------------
        #------------------Se establece una variable que se va a enviar al almacen con los datos de id del personaje y la fecha de agregado--------------------
        state={"idPersonaje":idPersonaje,"fecha_agregado":datetime.today()}
        self.bd.usuario.update_one({"_id":ObjectId(idUsuario)},{"$push":{"almacen":[state]}})
        #pass
    def consultarCompras(self):
        answer= {"Estatus":"" , "Message":""}
        #------------------Se consultan las compras------------------
        res=self.bd.compra.find()
        answer["Estatus"]="OK"
        answer["Message"]="Listado de compras"
        listilla=[]
        #------------------Se recorre cada compra y se agrega el nombre del usuario y el nombre del personaje------------------
        for i in res:
            i["_id"]=str(i["_id"])
            user = self.constultaUserById(i["idUsuario"])
            i["nombreUsuario"]=user["nombre"]
            detalle_tmp=[]
            detalles=i["detalleCompra"]
            for j in detalles:
                j["idPersonaje"]=str(j["idPersonaje"])
                #print(j['idPersonaje'])
                nmb = self.consultarNombrePersonaje(j["idPersonaje"])
                #-----------------Se agrega un atributo al objeto tal que asi, para guardar el nombre del personaje-----------------
                #-----------------Lo mismo se hizo en la parte de arriba con el nombre del usuario----------------------
                j["nombrePersonaje"]= nmb['nombre']
                #-----------------El metodo append se usa para agregar, en este caso como se hizo un cambio la variable a guardar es j-----------------------
                #-----------------y donde se va a guardar es detalle_tmp, es decir que lo que tenga detalle_tmp se le va agregar el objeto j--------------------
                detalle_tmp.append(j)
            i["detalleCompra"]=detalle_tmp
            #------------------Aqui se hace lo mismo pero con el objeto i, se va guardando en la lista ya el objeto modificado
            listilla.append(i)
        answer["Compras"]=listilla
        return answer
    def consultarNombrePersonaje(self,idPersonaje):
        res=self.bd.personaje.find_one({"_id":ObjectId(idPersonaje)},projection={"_id":False})
        #print(res)
        return res
    def consultarCompraById(self,idCompra):
        #answer={"Estatus":"" , "Message":""}
        res=self.bd.compra.find_one({"_id":ObjectId(idCompra)})
        res["_id"]=str(res["_id"])
        user = self.constultaUserById(res["idUsuario"])
        res['usuario']=user["nombre"]
        detail=res["detalleCompra"]

        for obj in detail:
            #-----------------Se consulta el usuario con el metodo de consultarNombrePersonaje-------------------
            nmb = self.consultarNombrePersonaje(obj["idPersonaje"])
            obj["nombrePersonaje"]=nmb['nombre']
        return res
    def crearPartida(self,partida:Partida):
        answer={"Estatus":"" , "Message":""}
        #print(partida)
        participantes=partida.participantes
        flag=True
        for participant in participantes:
            #------------------Comprobar si existe el usuario que se desea agregar a la partida------------------------
            if self.comprobarUserById(participant.usuario.idUsuario)>0:
                if self.comprobarExistenciaById(participant.usuario.idPersonaje)>0:
                    user= self.bd.usuario.find_one({"_id":ObjectId(participant.usuario.idUsuario)})
                    almcn=[]
                    almcn=user['almacen']
                    for obj in almcn:
                        #------------------Comprobar si el personaje existe en el almacen del usuario-----------------------
                        if obj['idPersonaje']==participant.usuario.idPersonaje:
                            state={"estatus":"P"}
                            #-----------------------------Se actualiza el estatus de cada participante para hacerles saber que esta en una partida jugando---------------
                            self.bd.usuario.update_one({"_id":ObjectId(participant.usuario.idUsuario)},{"$set":state})
                        else:
                            flag=False
                            answer["Estatus"]="Error"
                            answer["Message"]="El personaje no existe en el almacen del usuario"
                            break
                else:
                    flag=False
                    answer["Estatus"]="Error"
                    answer["Message"]="El personaje no existe"
                    break
            else:
                flag=False
                answer["Estatus"]="Error"
                answer["Message"]="El usuario no existe"
                break
        if flag:
            #------------------Se inserta una partida en la base de datos------------------
            self.bd.partida.insert_one(partida.dict())
            answer["Estatus"]="OK"
            answer["Message"]="Partida creada"
        return answer
    def encontrarPartida(self,idPartida):
        count=self.bd.partida.count_documents({"_id":ObjectId(idPartida)})
        return count
    def finalizarPartida(self, idPartida, idUsuarioGanador):
        answer={"Estatus":"" , "Message":""}
        if self.encontrarPartida(idPartida)>0:
            if self.comprobarUserById(idUsuarioGanador)>0:
                part=self.bd.partida.find_one({"_id":ObjectId(idPartida)})


                for usuario in part['participantes']:
                    usuario['estatus']="Played"
                    newSatate={"estatus":"A"}
                    obj = usuario['usuario']
                    self.bd.usuario.update_one({"_id":ObjectId(obj["idUsuario"])},{"$set":newSatate})
                    obj['idUsuario']=str(obj['idUsuario'])
                    if obj['idUsuario']== idUsuarioGanador:
                        usuario['ganador']=True

                state={"estatus":"T", "horaFin":datetime.now().time()}
                hora=datetime.strptime(part['horaInicio'], '%H:%M:%S.%f')
                state["duracion"]=self.calcularDuracion(state["horaFin"], (hora.time()))
                state["horaFin"]=str(state['horaFin'])
                state['fechaTerminacion']= str(date.today())
                #part['_id']=str(part['_id'])
                #answer['partida_actulizada']=part
                #answer['valores a agregar']=state
                self.bd.partida.update_one({"_id":ObjectId(idPartida)},{"$set":part})
                self.bd.partida.update_one({"_id":ObjectId(idPartida)},{"$set":state})
                answer["Estatus"]='OK'
                answer["Message"]="Partida finalizada con exito"
            else:
                answer["Estatus"]='Error'
                answer["Message"]="El usuario ganador no existe"
        else:
            answer["Estatus"]='Error'
            answer["Message"]="La partida no existe"
        return answer
    def calcularDuracion(self,hora1, hora2):
        duracion_minutos = round(((hora1.hour - hora2.hour) * 60 + \
                   (hora1.minute - hora2.minute) + \
                   (hora1.second - hora2.second) / 60),3)
        return duracion_minutos    
    def agregarParticipante(self, idPartida,participant:Participantes):
        answer={"Estatus":"" , "Message":""}
        if self.encontrarPartida(idPartida)>0:
            if self.comprobarUserById(participant.usuario.idUsuario)>0:
                if self.comprobarExistenciaById(participant.usuario.idPersonaje)>0:
                    user = self.bd.usuario.find_one({"_id":ObjectId(participant.usuario.idUsuario)})
                    almacn=[]
                    almacn=user['almacen']
                    #print(almacn)
                    for obj in almacn:
                        if obj['idPersonaje']==participant.usuario.idPersonaje:
                            part=self.bd.partida.find_one({"_id":ObjectId(idPartida)})
                            if part['estatus']=='A':
                                estate={"estatus":"P"}
                                self.bd.partida.update_one({"_id":ObjectId(idPartida)},{"$push":{"participantes":participant.dict()}})
                                self.bd.usuario.update_one({"_id":ObjectId(participant.usuario.idUsuario)},{"$set":estate})
                                answer["Estatus"]='OK'
                                answer["Message"]="Participante agregado con exito"
                            else:
                                answer["Estatus"]='Error'
                                answer["Message"]="La partida no esta activa"
                        else:
                            answer["Estatus"]='Error'
                            answer["Message"]="El personaje no esta en el almacen"
                else:
                    answer["Estatus"]='Error'
                    answer["Message"]="El personaje no existe"
            else:
                answer["Estatus"]='Error'
                answer["Message"]="El usuario no existe"
        else:
            answer["Estatus"]='Error'
            answer["Message"]="La partida no existe"
        return answer
    def consultarPartidas(self):
        answer= {"Estatus":"" , "Message":""}
        partidas=self.bd.partida.find()
        answer["Estatus"]="OK"
        answer["Message"]="Listado de partidas"
        listilla=[]
        for partida in partidas:
            partida["_id"]=str(partida['_id'])
            participant=[]
            participant=partida['participantes']
            for obj in participant:
                obj['usuario']['idPersonaje']=str(obj['usuario']['idPersonaje'])
                obj['usuario']['idUsuario']=str(obj['usuario']['idUsuario'])
                user = self.constultaUserById(obj['usuario']['idUsuario'])
                obj['usuario']['nombreUsuario']= user['nombre']
                nmb = self.consultarNombrePersonaje(obj['usuario']["idPersonaje"])
                obj["usuario"]['nombrePersonaje']= nmb['nombre']
            partida['participantes']=participant
            listilla.append(partida)
        answer["partidas"]=listilla
        return answer
    def consultarPartidaById(self,idPartida):
        answer={"Estatus":"" , "Message":""}
        if self.encontrarPartida(idPartida)>0:
            partida=self.bd.partida.find_one({"_id":ObjectId(idPartida)})
            answer["Estatus"]="OK"
            answer["Message"]="Partida encontrada"
            #----------------------------------------
            partida["_id"]=str(partida['_id'])
            participant=[]
            participant=partida['participantes']
            for obj in participant:
                obj['usuario']['idPersonaje']=str(obj['usuario']['idPersonaje'])
                obj['usuario']['idUsuario']=str(obj['usuario']['idUsuario'])
                user = self.constultaUserById(obj['usuario']['idUsuario'])
                obj['usuario']['nombreUsuario']= user['nombre']
                nmb = self.consultarNombrePersonaje(obj['usuario']["idPersonaje"])
                obj["usuario"]['nombrePersonaje']= nmb['nombre']
            partida['participantes']=participant
            answer['Partida']= partida
        else:
            answer["Estatus"]="Error"
            answer["Message"]="Partida no encontrada"
        return answer