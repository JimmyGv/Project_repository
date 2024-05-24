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
            try:
                self.bd.usuario.insert_one(usuario.dict())
                answer["Estatus"]="OK"
                answer["Message"]="Usuario creado exitosamente"
            except Exception as e:
                answer["Estatus"]="ERROR"
                answer["Message"]= f"Error al crear el usuario {str(e)}"
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
        if len(idUser) != 24:
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido, no contiene los 24 caracteres requeridos"
        elif not self.esHexadecimal(idUser):
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido, no es hexadecimal"
            #------------------comprobar si el usuario existe-----------------------
        elif self.comprobarUserById(idUser)>0:
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
        print(nombre_usuario)
        if (nombre_usuario != None):
            #------------------Obtener el usuario-----------------------
            usuario = self.bd.usuario.find_one({"correo":correo,"contrasena":contrasena},projection={"nombre":True,"correo":True,"estatus":True,"_id":False})
            if usuario['estatus']=="I":
                answer["Estatus"]="Error"
                answer["Message"]="El usuario esta inactivo, pida ayuda a soporte tecnico al correo tmp_jgonzalez@accitesz.com para volver a activar su cuenta"
            else:
                answer["Estatus"]= "OK"
                answer["Message"]="Usuario encontrado"
                #------------------Se puede agregar mas datos al diccionario no importa la cantidad o si son objetos, solo cambia cuando es una lista de objetos-----------------------
                answer["nombre_usuario"] = "Bienvenido: " + str(nombre_usuario['nombre'])
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
        if len(idUser) != 24:
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido, no contiene los 24 caracteres requeridos"
        elif not self.esHexadecimal(idUser):
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido, no es hexadecimal"
        elif self.comprobarUserById( ObjectId(idUser))>0:
            us = self.constultaUserById(idUser)
            if us['estatus']=="I":
                answer["Estatus"]="Error"
                answer["Message"]="El usuario no puede ser eliminado ya que esta inactivo"
            else:
                state = {"estatus":"I"}
                #------------------Se actualiza el estado del usuario con el metodo update_one----------------------
                try:
                    self.bd.usuario.update_one({"_id":ObjectId(idUser)},{"$set":state})
                    answer["Estatus"]="OK"
                    answer["Message"]="Usuario eliminado exitosamente"
                except Exception as e:
                    answer["Estatus"]="Error"
                    answer["Message"]= f"Error al eliminar el usuario: {str(e)}"
        else:
            answer["Estatus"]= "Error"
            answer["Message"]="El Usuario que se intenta eliminar no existe"
        return answer
    def consultaGeneralUsers(self):
        answer={"Estatus":"" , "Message":""}
        #------------------Se utiliza el metodo find para obtener todos los documentos que cumplen con la condicion----------------------
        #------------------En este caso se obtienen los documentos que tienen un estatus de activo-----------------------
        result=self.bd.consultarUsuarios.find()
        if result:
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
        else:
            answer["Estatus"]="Error"
            answer["Message"]="No se encontraron usuarios"
        return answer
    def constultaUserById(self, idUser):
        answer={"Estatus":"","Message":""}
        if len(idUser) != 24:
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido, no contiene los 24 caracteres requeridos"
            return answer
        if not self.esHexadecimal(idUser):
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido, no es hexadecimal"
            return answer
        if self.comprobarUserById( ObjectId(idUser))>0:
            #------------------Se utiliza el metodo find_one para obtener un documento que cumpla con la condicion----------------------
            #------------------En este caso se obtiene el documento que tiene el id que se le pasa como parametro-----------------------
            user=self.bd.usuario.find_one({"_id":ObjectId(idUser)},projection={"nombre":True,"correo":True,"estatus":True,"_id":False})
            return user
        else:
            answer["Estatus"]="Error"
            answer["Message"]="El Usuario que se intenta consultar no existe"
            return answer
    def crearPersonaje(self,personaje:PersonajeInsertar):
        answer= {"Estatus":"" , "Message":""} 
        if self.comprobarExistencia(personaje.nombre)>0:
            answer["Estatus"]="Error"
            answer["Message"]="Un personaje con este nombre ya existe"
        elif personaje.precio <0:
            answer["Estatus"]="Error"
            answer["Message"]="El precio del personaje no puede ser negativo"
        else:
            #------------------Se utiliza el metodo insert_one para insertar un documento en la coleccion----------------------
            #------------------En este caso se inserta el personaje que se le pasa como parametro------------------------
            #------------------Se utiliza el metodo dict para convertir el objeto en un diccionario digerible para mongo----------------------
            try:
                self.bd.personaje.insert_one(personaje.dict())
                answer["Estatus"]="OK"
                answer["Message"]="Personaje creado exitosamente"
            except Exception as e:
                answer["Estatus"]="Error"
                answer["Message"]= f"Error al crear el personaje: {str(e)}"
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
        if len(idPersonaje) != 24:
            answer["Estatus"]="Error"
            answer["Message"]="El id del personaje no es valido, no contiene los 24 caracteres requeridos"
        elif not self.esHexadecimal(idPersonaje):
            answer["Estatus"]="Error"
            answer["Message"]="El id del personaje no es valido, no es hexadecimal la cadena"
        elif self.comprobarExistenciaById(idPersonaje)>0:
            prnj = self.consultarPersonajeById(idPersonaje)

            #--------------------comprueba si el nombre al de la base de datos---------------- 
            if prnj['nombre'] != personaje.nombre:
                answer["Estatus"]="Error"
                answer["Message"]="No puedes actualizar el nombre del personaje"
            else:

                #------------------Se utiliza el metodo update_one para actualizar un documento en la coleccion----------------------
                #------------------En este caso se actualiza el personaje que se le pasa como parametro------------------------
                #------------------Se utiliza el metodo dict para convertir el objeto en un diccionario digerible para mongo----------------------
                
                try:
                    self.bd.personaje.update_one({"_id":ObjectId(idPersonaje)},{"$set":personaje.dict()})
                    resul=self.bd.personaje.find_one({"_id":ObjectId(idPersonaje)},projection={"_id":False})
                    answer["Estatus"]="OK"
                    answer["Message"]="El personaje se ha modificado correctamente"
                    answer['Personaje']=resul
                except Exception as e:
                    answer["Estatus"]="Error"
                    answer["Message"]= f"Error al actualizar el personaje: {str(e)}"

        else:
            answer["Estatus"]="Error"
            answer["Message"]="El personaje que se intenta modificar no existe"
        return answer
    def eliminarPersonaje(self,idPersonaje):
        answer= {"Estatus":"" , "Message":""}
        if len(idPersonaje) != 24:
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido porque no contiene los 24 caracteres requeridos"
        elif not self.esHexadecimal(idPersonaje):
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido porque no es hexadecimal"
        elif self.comprobarExistenciaById(idPersonaje)>0:
            ps = self.consultarPersonajeById(idPersonaje)
            if ps['estatus'] == "I":
                answer["Estatus"]="Error"
                answer["Message"]="No puedes eliminar un personaje ya previamente eliminado"
                return answer
            state={"estatus":"I"}
            try:
                self.bd.personaje.update_one({"_id":ObjectId(idPersonaje)},{"$set":state})
                answer["Estatus"]="OK"
                answer["Message"]="El personaje se ha eliminado correctamente"
            except Exception as e:
                answer["Estatus"]="Error"
                answer["Message"]= f"Error al eliminar el personaje: {str(e)}"
        else:
            answer["Estatus"]="Error"
            answer["Message"]="El personaje que se intenta eliminar no existe"
        return answer
    def consultarPersonajes(self):
        personajes=self.bd.personaje.find()
        answer={"personajes":""}
        if personajes:
            listilla=[]
            for i in personajes:
                i["_id"]=str(i["_id"])
                listilla.append(i)
            answer={"personajes":""}
            answer["personajes"]=listilla
        else:
            answer["personajes"]="No hay registro de personajes en la bd"
        return answer
    def consultarPersonajeById(self,idPersonaje):
        if len(idPersonaje) != 24:
            answer={"Estatus":"" , "Message":""}
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido porque no contiene los caracteres requeridos"
            return answer
        if not self.esHexadecimal(idPersonaje):
            answer={"Estatus":"" , "Message":""}
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido porque no es hexadecimal"
            return answer
        if self.comprobarExistenciaById(idPersonaje)>0:

            personaje=self.bd.personaje.find_one({"_id":ObjectId(idPersonaje)})

            personaje["_id"]=str(personaje["_id"])
            return personaje
        else:
            answer={"Estatus":"" , "Message":""}
            answer["Estatus"]="Error"
            answer["Message"]="El personaje que se intenta consultar no existe"
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
        if 'almacen' in user:
            for i in user["almacen"]:
                
                if i['idPersonaje'] == idPersonaje:
                    return True
        return False
    def realizarCompra(self,compra:Compra):
        answer= {"Estatus":"" , "Message":""}
        if len(compra.idUsuario) != 24 :
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido porque no contiene los caracteres requeridos"
            return answer
        if not self.esHexadecimal(compra.idUsuario):
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido porque no es hexadecimal"
            return answer
        if compra.total <0:
            answer["Estatus"]="Error"
            answer["Message"]="El total de la compra no puede ser menor a 0"
            return answer
        #-----------------se establece como referencia importante una vaiable de tipo booleano en falso---------------
        band = True
        #------------------Se comprueba si existe el usuario que quiere realizar la compra------------------------
        if self.comprobarUserById(compra.idUsuario)>0:
            us = self.constultaUserById(compra.idUsuario)
            if us['estatus'] == "I":
                answer["Estatus"]="Error"
                answer["Message"]="El usuario no existe o esta inactivo"
                return answer
            detail=compra.detalleCompra
            
            #-----------------Se utiliza set que funciona como un validador para detectar duplicados-----------
            seen_personajes = set()
            #------------------Se recorre cada elemento que contiene detail-----------------------
            for character in detail:
                id_personaje = character.idPersonaje
                #------------------Se verifica si la cadena contiene los caracteres necesarios para ser considerado un ObjectId
                if len(id_personaje) != 24 :
                    answer["Estatus"]="Error"
                    answer["Message"]="El id del personaje no es valido porque no contiene los caracteres requeridos"
                    band = False
                    break
                if not self.esHexadecimal(id_personaje):
                    answer["Estatus"]="Error"
                    answer["Message"]="El id del personaje no es valido porque no es hexadecimal"
                    band = False
                    break
                # Verificar que no haya personajes duplicados en la compra
                if id_personaje in seen_personajes:
                    answer["Estatus"] = "Error"
                    answer["Message"] = "No puede comprar personajes duplicados en una misma compra"
                    return answer
                seen_personajes.add(id_personaje)
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
                    if personaje['estatus']=="I":
                        answer["Estatus"]="Error"
                        answer["Message"]="No puede comprar este personaje ya que esta inactivo"
                        band=False
                        break
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
                if compra.total == round(compra.subtotal,2) or compra.total > round(compra.subtotal,2):
                    #------------------Se inserta la compra en la base de datos y se trae el resultado------------------
                    try:
                        result = self.bd.compra.insert_one(compra.dict())
                    except Exception as e:
                        answer["Estatus"]="Error"
                        answer["Message"]= f"Error al insertar la compra en la base de datos {str(e)}"
                        return answer

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
        self.bd.usuario.update_one({"_id":ObjectId(idUsuario)},{"$push":{"almacen":state}})
        #pass
    def consultarCompras(self):
        answer= {"Estatus":"" , "Message":""}
        #------------------Se consultan las compras------------------
        res=self.bd.compra.find()
        if res:
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
        else:
            answer["Estatus"]="Error"
            answer["Message"]="No hay compras registradas"
        return answer
    def consultarNombrePersonaje(self,idPersonaje):
        res=self.bd.personaje.find_one({"_id":ObjectId(idPersonaje)},projection={"_id":False})
        #print(res)
        return res
    def consultarCompraById(self,idCompra):
        #answer={"Estatus":"" , "Message":""}
        if len(idCompra) != 24:
            return "Error: El id de la compra no es valido, no contiene 24 caracteres"
        if not self.esHexadecimal(idCompra):
            return "Error: El id de la compra no es valido, no es hexadecimal"
        res=self.bd.compra.find_one({"_id":ObjectId(idCompra)})
        if res:
            print(res['_id'])
            res["_id"]=str(res['_id'])
            user = self.constultaUserById(res["idUsuario"])
            res['usuario']=user["nombre"]
            detail=res["detalleCompra"]

            for obj in detail:
                #-----------------Se consulta el usuario con el metodo de consultarNombrePersonaje-------------------
                nmb = self.consultarNombrePersonaje(obj["idPersonaje"])
                obj["nombrePersonaje"]=nmb['nombre']
            return res
        else:
            return "Error: No se encontro la compra"
    def crearPartida(self,partida:Partida):
        answer={"Estatus":"" , "Message":""}
        #print(partida)
        contador = 0
        participantes=partida.participantes
        flag=True
        for participant in participantes:
            if participant.ganador != False:
                flag=False
                answer["Estatus"]="Error"
                answer["Message"]="No se puede crear la partida, hay un participante que ya es ganador"
                break
            if len(participant.usuario.idUsuario) != 24:
                flag=False
                answer["Estatus"]="Error"
                answer["Message"]="El id del usuario no es valido porque no contiene los caracteres requeridos"
                break
            elif not self.esHexadecimal(participant.usuario.idUsuario):
                flag=False
                answer["Estatus"]="Error"
                answer["Message"]="El id del usuario no es valido porque no es hexadecimal"
                break
            elif len(participant.usuario.idPersonaje) != 24:
                flag=False
                answer["Estatus"]="Error"
                answer["Message"]="El id del personaje no es valido porque no contiene los caracteres requeridos"
                break
            elif not self.esHexadecimal(participant.usuario.idPersonaje):
                flag=False
                answer["Estatus"]="Error"
                answer["Message"]="El id del personaje no es valido porque no es hexadecimal"
                break
                #------------------Comprobar si existe el usuario que se desea agregar a la partida------------------------
            elif self.comprobarUserById(participant.usuario.idUsuario)>0:
                us = self.constultaUserById(participant.usuario.idUsuario)
                if us["estatus"] == "I":
                    flag=False
                    answer["Estatus"]="Error"
                    answer["Message"]="El usuario "+us["nombre"]+" esta inactivo"
                    break
                if us["estatus"] == "P":
                    flag=False
                    answer["Estatus"]="Error"
                    answer["Message"]="No se puede crear la partida ya que el usuario " + us["nombre"]+" esta en otra partida"
                    break
                if self.comprobarExistenciaById(participant.usuario.idPersonaje)>0:
                    if self.existeEnAlmacen(participant.usuario.idUsuario,participant.usuario.idPersonaje):
                        #------------------Comprobar si el personaje existe en el almacen del usuario-----------------------
                        contador+=1
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
            #-----------------------------Se actualiza el estatus de cada participante para hacerles saber que esta en una partida jugando---------------
            if contador <partida.cupoMinimo :
                answer["Estatus"]="Error"
                answer["Message"]="No se han agregado los participantes necesarios para crear la partida"
            else:
                if contador > partida.cupoMaximo:
                    answer["Estatus"]="Error"
                    answer["Message"]="Se han agregado mas participantes de los establecidos"
                    return answer
                if  self.verificarParticipantes(participantes) == False:
                    #------------------Se inserta una partida en la base de datos------------------
                    try:
                        self.bd.partida.insert_one(partida.dict())
                        for participant in participantes:
                            estate={"estatus":"P"}
                            try:
                                self.bd.usuario.update_one({"_id":ObjectId(participant.usuario.idUsuario)},{"$set":estate})
                            except Exception as e:
                                answer["Estatus"]="Error"
                                answer["Message"]="No se pudo actualizar el estatus del usuario"
                                return answer
                        answer["Estatus"]="OK"
                        answer["Message"]="Partida creada"
                    except Exception as e:
                        answer["Estatus"]="Error"
                        answer["Message"]= f"Error al crear la partida {str(e)}"
                else:
                    answer["Estatus"]="Error"
                    answer["Message"]="No se pueden agregar dos usuarios iguales a la misma partida"
        return answer
    
    def verificarParticipantes(self,ticipants):
        ids_usuario = set()
        
        for participte in ticipants:
            #print (participte.usuario.idUsuario)
            id_usuario = participte.usuario.idUsuario

            if id_usuario in ids_usuario:
                return True

            ids_usuario.add(id_usuario)
        return False
    def encontrarPartida(self,idPartida):
        count=self.bd.partida.count_documents({"_id":ObjectId(idPartida)})
        return count
    def finalizarPartida(self, idPartida, idUsuarioGanador):
        answer={"Estatus":"" , "Message":""}
        if len(idPartida) != 24:
            answer["Estatus"]="Error"
            answer["Message"]="El id de la partida no es valido porque no contiene los caracteres requeridos"
        elif len(idUsuarioGanador) != 24:
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario ganador no es valido porque no contiene los caracteres requeridos"
        elif not self.esHexadecimal(idPartida):
            answer["Estatus"]="Error"
            answer["Message"]="El id de la partida no es valido porque no esta en un formato hexadecimal"
        elif not self.esHexadecimal(idUsuarioGanador):
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario ganador no es valido porque no esta en un formato hexadecimal"
            #------------------Comprobar si la partida existe------------------------
        elif self.encontrarPartida(idPartida)>0:
            if self.comprobarUserById(idUsuarioGanador)>0:
                part=self.bd.partida.find_one({"_id":ObjectId(idPartida)})
                
                if part['estatus'] == "T":
                    answer["Estatus"]="Error"
                    answer["Message"]="La partida ya ha sido finalizada"
                else:

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
        contador =0
        flag =False
        if len(idPartida) != 24:
            answer["Estatus"]="Error"
            answer["Message"]="El id de la partida no es valido porque no contiene los caracteres requeridos para ser objectid"
        elif len(participant.usuario.idUsuario) !=24:
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido porque no contiene los caracteres requeridos para ser objectid"
        elif len(participant.usuario.idPersonaje) !=24:
            answer["Estatus"]="Error"
            answer["Message"]="El id del personaje no es valido porque no contiene los caracteres requeridos para ser objectid"
        elif not self.esHexadecimal(idPartida):
            answer["Estatus"]="Error"
            answer["Message"]="El id de la partida no es valido porque no esta en un formato hexadecimal"
        elif not self.esHexadecimal(participant.usuario.idUsuario):
            answer["Estatus"]="Error"
            answer["Message"]="El id del usuario no es valido porque no esta en un formato hexadecimal"
        elif not self.esHexadecimal(participant.usuario.idPersonaje):
            answer["Estatus"]="Error"
            answer["Message"]="El id del personaje no es valido porque no esta en un formato hexadecimal"
        else:
            if self.encontrarPartida(idPartida)>0:
                if self.comprobarUserById(participant.usuario.idUsuario)>0:
                    if self.comprobarExistenciaById(participant.usuario.idPersonaje)>0:
                        user = self.bd.usuario.find_one({"_id":ObjectId(participant.usuario.idUsuario)})
                        if user['estatus'] == "I" or user['estatus']== "P":
                            answer["Estatus"]="Error"
                            answer["Message"]="El usuario no esta activo o esta jugando"
                            return answer
                        
                        if not 'almacen' in user:
                            answer["Estatus"]="Error"
                            answer["Message"]="El usuario no se puede agregar ya que no tiene un almacen"
                            return answer
                        almacn=[]
                        almacn=user['almacen']
                        #print(almacn)
                        for obj in almacn:
                            if obj['idPersonaje']==participant.usuario.idPersonaje:
                                part=self.bd.partida.find_one({"_id":ObjectId(idPartida)})
                                particpants = part['participantes']
                                
                                for objson in particpants:
                                    contador +=1
                                    if objson['usuario']['idUsuario']==participant.usuario.idUsuario:
                                        answer["Estatus"]="Error"
                                        answer['Message']="No puedes agregar a otro usuario identico"
                                        return answer
                                if contador == part['cupoMaximo']:
                                    answer['Estatus']="Error"
                                    answer['Message']="No puedes agregar mas participantes"
                                    return answer

                                if part['estatus']=='A':
                                    estate={"estatus":"P"}
                                    self.bd.partida.update_one({"_id":ObjectId(idPartida)},{"$push":{"participantes":participant.dict()}})
                                    self.bd.usuario.update_one({"_id":ObjectId(participant.usuario.idUsuario)},{"$set":estate})
                                    answer["Estatus"]='OK'
                                    answer["Message"]="Participante agregado con exito"
                                    flag=True
                                    break
                                else:
                                    answer["Estatus"]='Error'
                                    answer["Message"]="La partida no esta activa"
                            if not flag:
                                answer["Estatus"]='Error'
                                answer["Message"]="El personaje no esta en el almacen del usuario"
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
        if len(idPartida) != 24:
            answer["Estatus"]="Error"
            answer["Message"]="El id de la partida no es valido porque no contiene los caracteres requeridos"
        elif not self.esHexadecimal(idPartida):
            answer["Estatus"]="Error"
            answer["Message"]="El id de la partida no es valido porque no esta en un formato hexadecimal"
        else:
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
    def esHexadecimal(self, cadena):
        try:
            int(cadena, 16)
        except ValueError:
            return False
        return True