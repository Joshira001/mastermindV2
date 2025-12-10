import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk, ImageSequence  #esto es por motivos estéticos y requiere instalación
import random
import datetime
from reportlab.pdfgen import canvas
import os
import cv2 #esto es para la celebración
import pygame #esto también es para la celebración

class Marca:
    """CLASE: REPRESENTA UNA MARCA REGISTRADA EN EL HISTORIAL  
    ATRIBUTOS: NOMBRE DEL JUGADOR, TIEMPO TOTAL, COMBINACIÓN, FECHA, HORA Y NIVEL.  
    MÉTODOS:  
        - desplegar_marca_resumen(): Devuelve un resumen simple de la marca.  
        - desplegar_marca_detalle(): Devuelve información detallada y completa de la marca.  
    """

    def __init__(self, jugador, tiempo_total, combinacion, fecha, hora, nivel):
        self.jugador = jugador
        self.tiempo_total = tiempo_total
        self.combinacion = combinacion
        self.fecha = fecha
        self.hora = hora
        self.nivel = nivel

    def desplegar_marca_resumen(self):
        return f"{self.jugador} - {self.tiempo_total} seg"

    def desplegar_marca_detalle(self):
        return f"{self.jugador} | {self.combinacion} | {self.fecha} {self.hora} | {self.tiempo_total} seg"


class NodoABB:
    """CLASE: NODO PARA EL ÁRBOL BINARIO DE BÚSQUEDA (ABB)  
    ATRIBUTOS:  
        - marca: Objeto de la clase Marca almacenado en el nodo.  
        - izquierdo: Referencia al nodo hijo izquierdo.  
        - derecho: Referencia al nodo hijo derecho.  
    """

    def __init__(self, marca):
        self.marca = marca
        self.izquierdo = None
        self.derecho = None

class ABB:
    """CLASE: IMPLEMENTA UN ÁRBOL BINARIO DE BÚSQUEDA (ABB) PARA ORDENAR MARCAS POR TIEMPO  
    MÉTODOS:  
        - insertar_nodo(marca): Inserta una nueva marca en el árbol manteniendo el orden.  
        - recorrer_arbol(): Retorna todas las marcas en orden ascendente (recorrido in-orden).  
        - _insertar_recursivo(): Lógica interna recursiva de inserción.  
        - _inorden(): Método recursivo del recorrido in-orden.  
    """

    def __init__(self):
        self.raiz = None

    def insertar_nodo(self, marca):
        self.raiz = self._insertar_recursivo(self.raiz, marca)

    def _insertar_recursivo(self, nodo, marca):
        if nodo is None:
            return NodoABB(marca)

        if marca.tiempo_total < nodo.marca.tiempo_total:
            nodo.izquierdo = self._insertar_recursivo(nodo.izquierdo, marca)
        else:
            nodo.derecho = self._insertar_recursivo(nodo.derecho, marca)

        return nodo

    def recorrer_arbol(self):
        marcas = []
        self._inorden(self.raiz, marcas)
        return marcas

    def _inorden(self, nodo, marcas):
        if nodo:
            self._inorden(nodo.izquierdo, marcas)
            marcas.append(nodo.marca)
            self._inorden(nodo.derecho, marcas)

abb_facil = ABB()
abb_medio = ABB()
abb_dificil = ABB()

datos_configuracion = []
colores = {"azul": "#1F23F3", "mostaza": "#ECB731", "rojo": "#F31F1F", "verde": "#2CF325", "naranja": "#FC7A00", "amarillo": "#EEFF00"}
numeros = (1, 2, 3, 4, 5, 6)
letras= ("a", "b", "c", "d", "e", "f")
elementos = {"colores": colores,"numeros": numeros,"letras": letras,"simbolos": [] }
cantidad_jugadas = 8

def obtener_elementos_segun_dificultad(tipo, dificultad):
    """FUNCIÓN: OBTENER ELEMENTOS FILTRADOS SEGÚN LA DIFICULTAD  
    ENTRADAS:  
        - tipo: Tipo de elementos ("colores", "numeros", "letras" o "simbolos").  
        - dificultad: Nivel del juego ("Fácil", "Normal", "Difícil").  
    SALIDAS:  
        Lista o diccionario con los elementos permitidos para esa dificultad.  
    """

    limites = {"Fácil": 4, "Normal": 5, "Difícil": 6}
    limite = limites.get(dificultad, 6)

    if tipo == "colores":
        return dict(list(colores.items())[:limite])
    elif tipo == "numeros":
        return numeros[:limite]
    elif tipo == "letras":
        return letras[:limite]
    elif tipo == "simbolos":
        return elementos["simbolos"][:limite]
    return []

dificultad = ("Fácil", "Normal", "Difícil")
segundos = 0

mastermind = tk.Tk()
mastermind.title("MasterMindV2")
mastermind.geometry("650x356")
mastermind.config(background = "black")

base_path = os.path.dirname(os.path.abspath(__file__))
archivo_configuracion = os.path.join(base_path, "mastermind2025configuración.dat")
archivo_top10 = os.path.join(base_path, "mastermind2025top10.dat")

def cargar_configuracion():
    """FUNCIÓN: CARGAR CONFIGURACIÓN DESDE ARCHIVO  
    ENTRADAS: NINGUNA (LEE EL ARCHIVO mastermind2025configuración.dat SI EXISTE).  
    SALIDAS:  
        - Actualiza la lista datos_configuracion.  
        - Carga símbolos personalizados si aplica.  
        - Restaura valores por defecto si el archivo no existe o está incompleto.  
    """

    if os.path.exists(archivo_configuracion):
        with open(archivo_configuracion, "r", encoding="utf-8") as archivo:
            lineas = archivo.read().splitlines()

        if len(lineas) < 4:
            datos_configuracion.clear()
            datos_configuracion.extend(["Difícil", "colores", "No", "Derecha", "No", ""])
        else:
            if len(lineas) == 4:
                lineas.append("No")
                lineas.append("")
            elif len(lineas) == 5:
                lineas.append("")

            datos_configuracion.clear()
            datos_configuracion.extend(lineas[:6])

        if len(datos_configuracion) >= 6 and datos_configuracion[5].strip():
            simbolos_guardados = datos_configuracion[5].strip()
            elementos["simbolos"] = [
                s.strip() for s in simbolos_guardados.split(",") if s.strip()
            ]
        else:
            elementos["simbolos"] = []

    else:
        datos_configuracion.clear()
        datos_configuracion.extend(["Difícil", "colores", "No", "Derecha", "No", ""])
        elementos["simbolos"] = []

ruta_gif = os.path.join(base_path, "fondo.gif")  
gif = Image.open(ruta_gif)

frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif)]

label_fondo = tk.Label(mastermind)
label_fondo.place(x=0, y=0, relwidth=1, relheight=1)

def animar(ventana, label, frames, delay=100, ind=0):
    frame = frames[ind]
    ind = (ind + 1) % len(frames)
    label.configure(image=frame)
    label.lower()
    ventana.after(delay, animar, ventana, label, frames, delay, ind)
animar(mastermind, label_fondo, frames)

ruta_titulo = os.path.join(base_path, "mastermind_titulo.jpg")
imagen = Image.open(ruta_titulo)
imagen = imagen.resize((220, 40))
titulo_tk = ImageTk.PhotoImage(imagen)

label_titulo = tk.Label(mastermind, image=titulo_tk, bg="black", borderwidth=0)
label_titulo.place(x=210,y=20)

def video_victoria():
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_video = os.path.join(ruta_base, "victoria.mp4")
    ruta_audio = os.path.join(ruta_base, "victoria.mp3")

    if os.path.exists(ruta_audio):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(ruta_audio)
            pygame.mixer.music.play()
        except:
            pass

    captura = cv2.VideoCapture(ruta_video)
    if not captura.isOpened():
        messagebox.showerror("ERROR", "No se puede abrir victoria.mp4")
        return

    ventana_video = tk.Toplevel(mastermind)
    ventana_video.title("¡FELICITACIONES!")
    ventana_video.geometry("848x480")
    ventana_video.config(bg="black")

    etiqueta_video = tk.Label(ventana_video, bg="black")
    etiqueta_video.pack(expand=True, fill="both")

    exito, frame = captura.read()
    if not exito:
        captura.release()
        ventana_video.destroy()
        return

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    imagen = ImageTk.PhotoImage(Image.fromarray(frame))
    etiqueta_video.config(image=imagen)
    etiqueta_video.image = imagen

    def reproducir_frame():
        exito, frame = captura.read()

        if not exito:
            captura.release()
            try:
                pygame.mixer.music.stop()
            except:
                pass
            ventana_video.destroy()
            messagebox.showinfo("JUEGO TERMINADO", "¡FELICITACIONES, USTED HA GANADO!")
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagen = ImageTk.PhotoImage(Image.fromarray(frame))

        etiqueta_video.config(image=imagen)
        etiqueta_video.image = imagen

        ventana_video.after(30, reproducir_frame)

    ventana_video.after_idle(reproducir_frame)

def jugar():
    """FUNCIÓN: ABRE LA INTERFAZ GRÁFICA PARA INICIAR EL JUEGO  
    ENTRADAS: NINGUNA (SE ACTIVA DESDE EL MENÚ PRINCIPAL O EL BOTÓN “JUGAR”).  
    SALIDAS: CREA UNA NUEVA VENTANA CON EL TABLERO, PANEL DE ELEMENTOS, BOTONES DE CONTROL E INICIA LA LÓGICA DEL JUEGO. """
    jugadas_realizadas = []
    jugadas_deshechas = []

    juego = tk.Toplevel(mastermind)
    juego.title("MasterMindV2: JUGAR")
    juego.geometry("1000x600")
    juego.config(background="black")
    ruta_gif_juego = os.path.join(base_path, "fondo_juego.gif")
    gif_juego = Image.open(ruta_gif_juego)
    frames_juego = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif_juego)] 

    label_fondo_juego = tk.Label(juego)
    label_fondo_juego.place(x=0, y=0, relwidth=1, relheight=1)

    animar(juego, label_fondo_juego, frames_juego)
    
    ruta_titulo = os.path.join(base_path, "mastermind_titulo.jpg")
    imagen = Image.open(ruta_titulo)
    imagen = imagen.resize((220, 40))
    titulo_tk = ImageTk.PhotoImage(imagen)
    label_titulo = tk.Label(juego, image=titulo_tk, background = "black", borderwidth=0)
    label_titulo.image = titulo_tk
    label_titulo.place(x=400, y=20)

    tk.Label(juego, text="JUGADOR:", font=("Impact", 12), fg="white", bg="black").place(x=710, y=550)
    nombre_entry = tk.Entry(juego, width=20, font=("Impact", 12))
    nombre_entry.place(x=780, y=550)

    if not datos_configuracion:
        datos_configuracion.append(dificultad[2]) 
    tk.Label(juego, text=f"NIVEL: {datos_configuracion[0]}", font=("Impact", 12), fg="white", bg="black").place(x=430, y=550)

    ruta_borrador = os.path.join(base_path, "borrador.png")
    borr = Image.open(ruta_borrador)
    borr = borr.resize((60, 60))
    borrador_tk = ImageTk.PhotoImage(borr)
    ruta_iniciar = os.path.join(base_path, "iniciar.jpg")
    inic = Image.open(ruta_iniciar)
    inic = inic.resize((80, 80))
    iniciar_tk = ImageTk.PhotoImage(inic)
    iniciar = tk.Button(juego, image=iniciar_tk, bg="black", cursor="hand2")
    iniciar.image = iniciar_tk
    iniciar.place(x=250, y=450)
    ruta_cargar = os.path.join(base_path, "cargar.jpg")
    carg = Image.open(ruta_cargar)
    carg = carg.resize((80, 80))
    cargar_tk = ImageTk.PhotoImage(carg)
    ruta_calificar = os.path.join(base_path, "calificar.jpg")
    cali = Image.open(ruta_calificar)
    cali = cali.resize((80, 80))
    calificar_tk = ImageTk.PhotoImage(cali)
    ruta_cancelar = os.path.join(base_path, "cancelar.jpg")
    canc = Image.open(ruta_cancelar)
    canc = canc.resize((80, 80))
    cancelar_tk = ImageTk.PhotoImage(canc)
    ruta_guardar = os.path.join(base_path, "guardar.jpg")
    save = Image.open(ruta_guardar)
    save = save.resize((80, 80))
    guardar_tk = ImageTk.PhotoImage(save)
    ruta_deshacer = os.path.join(base_path, "deshacer.jpg")
    deshacer = Image.open(ruta_deshacer)
    deshacer = deshacer.resize((80, 80))
    deshacer_tk = ImageTk.PhotoImage(deshacer)
    ruta_rehacer = os.path.join(base_path, "rehacer.jpg")
    rehacer = Image.open(ruta_rehacer)
    rehacer = rehacer.resize((80, 80))
    rehacer_tk = ImageTk.PhotoImage(rehacer)

    if not datos_configuracion:
        datos_configuracion[:] = ["Difícil", "colores", "No", "Derecha"]

    dificultad_actual = datos_configuracion[0]
    tipo_de_elementos = datos_configuracion[1]
    tipo_reloj = datos_configuracion[2]
    
    if datos_configuracion[0] == "Multinivel":
        if hasattr(juego, "nivel_actual"):
            dificultad_actual = juego.nivel_actual
        else:
            dificultad_actual = "Fácil"
    else:
        dificultad_actual = datos_configuracion[0]

    juego.nivel_actual = dificultad_actual

    
    if len(datos_configuracion) >= 4:
        posicion_panel = datos_configuracion[3]
    else:
        posicion_panel = "Derecha"

    if len(datos_configuracion) >= 5:
        permitir_repetidos = datos_configuracion[4]
    else:
        permitir_repetidos = "No"

    combinacion_local = {"Fácil": 4, "Normal": 5, "Difícil": 6}.get(dificultad_actual, 6)

    juego.combinacion_local_secreta = None
    jugada_actual = [0]

    alto_tablero = cantidad_jugadas * 45
    area_jugadas = tk.Frame(juego, bg="black", width=550, height=alto_tablero)
    area_jugadas.place(x=220, y=100)

    label_fondo_juego.lower()
    area_jugadas.lift(label_fondo_juego)

    separacion_y = 45
    separacion_x = 60

    lista_jugadas = []

    def crear_jugada(numero_jugada):
        posicion_y = (cantidad_jugadas - numero_jugada - 1) * separacion_y
        fila_widgets = []

        for posicion_columna in range(combinacion_local):
            casilla = tk.Canvas(area_jugadas, width=30, height=30, bg="white", highlightthickness=0)
            casilla.create_oval(4, 4, 26, 26, fill="white", outline="black", width=1)
            posicion_x = 50 + posicion_columna * separacion_x
            casilla.place(x=posicion_x, y=posicion_y)
            fila_widgets.append(casilla)

        cantidad_circulos_calificacion = combinacion_local
        for posicion_calificacion in range(cantidad_circulos_calificacion):
            calif = tk.Canvas(area_jugadas, width=20, height=20, bg="white", highlightthickness=0)
            calif.create_oval(3, 3, 17, 17, fill="white", outline="black", width=1)
            posicion_x_calificacion = 40 + combinacion_local * separacion_x + (posicion_calificacion * 25)
            calif.place(x=posicion_x_calificacion, y=posicion_y + 10)
            fila_widgets.append(calif)


        lista_jugadas.append(fila_widgets)

    for numero_jugada in range(cantidad_jugadas):
        crear_jugada(numero_jugada)

    def colocar_en_casilla(evento):
        tipo_elemento = elemento_seleccionado.get("tipo")
        valor_elemento = elemento_seleccionado.get("valor")

        fila_activa = lista_jugadas[jugada_actual[0]][:combinacion_local]
        if evento.widget not in fila_activa:
            return

        if tipo_elemento is None or valor_elemento is None:
            messagebox.showwarning("ADVERTENCIA", "Debe seleccionar un elemento antes de colocar.")
            return

        casilla_canvas = evento.widget
        elementos_previos = casilla_canvas.find_all()
        if elementos_previos:
            tipo_prev = casilla_canvas.type(elementos_previos[0])
            if tipo_prev == "oval":
                color_detectado = casilla_canvas.itemcget(elementos_previos[0], "fill")

                if color_detectado == "white":
                    valor_previo = None
                else:
                    valor_previo = color_detectado

            else:
                texto_detectado = casilla_canvas.itemcget(elementos_previos[0], "text")

                if texto_detectado:
                    valor_previo = texto_detectado
                else:
                    valor_previo = None

        else:
            valor_previo = None
        jugadas_realizadas.append((casilla_canvas, valor_previo))
        casilla_canvas.delete("all")

        if tipo_elemento == "colores":
            casilla_canvas.create_oval(5, 5, 25, 25, fill=valor_elemento, outline="black")

        elif tipo_elemento in ["numeros", "letras", "simbolos"]:
            casilla_canvas.create_text(15, 15, text=str(valor_elemento), font=("Impact", 12), fill="black")

        elif tipo_elemento == "borrador":
            casilla_canvas.create_oval(5, 5, 25, 25, fill="white", outline="black")

    if datos_configuracion[3] == "Izquierda":
        panel_elementos = tk.Frame(juego, bg="black", width=130, height=350)
        panel_elementos.place(x=100, y=110)
    else:
        panel_elementos = tk.Frame(juego, bg="black", width=130, height=350)
        panel_elementos.place(x=950, y=110)

    elementos_visibles = []
    elemento_seleccionado = {"tipo": None, "valor": None}

    elementos_restringidos = obtener_elementos_segun_dificultad(tipo_de_elementos, dificultad_actual)

    if tipo_de_elementos == "colores":
        for nombre_color, codigo_hex in elementos_restringidos.items():
            boton_color = tk.Button(panel_elementos,bg=codigo_hex,width=6,height=2,relief="raised",cursor="hand2",activebackground="light grey",borderwidth=2)

            def seleccionar_color(color=codigo_hex, nombre=nombre_color):
                elemento_seleccionado["tipo"] = "colores"
                elemento_seleccionado["valor"] = color

            boton_color.config(command=seleccionar_color)
            boton_color.pack(pady=4, padx=10)
            elementos_visibles.append((boton_color, codigo_hex))

    else:
        lista_de_elementos = list(elementos_restringidos)
        for valor_mostrado in lista_de_elementos:
            boton_valor = tk.Button(panel_elementos,text=str(valor_mostrado),width=6,height=2,font=("Impact", 12),bg="white",fg="black",relief="raised",cursor="hand2",activebackground="light grey",borderwidth=2)

            def seleccionar_valor(valor=valor_mostrado):
                elemento_seleccionado["tipo"] = tipo_de_elementos
                elemento_seleccionado["valor"] = valor

            boton_valor.config(command=seleccionar_valor)
            boton_valor.pack(pady=6, padx=10)
            elementos_visibles.append((boton_valor, str(valor_mostrado)))

    def calificar():
        mensaje = tk.Label(juego, text="CALIFICAR PRESIONADO",font=("Impact", 14), fg="white", bg="black")
        mensaje.place(x=400, y=520)
        juego.after(1500, mensaje.destroy)

        if juego.combinacion_local_secreta is None:
            messagebox.showwarning("ADVERTENCIA", "DEBE INICIAR EL JUEGO ANTES DE CALIFICAR.")
            return

        numero_de_jugada = jugada_actual[0]
        if numero_de_jugada >= len(lista_jugadas):
            messagebox.showinfo("FIN DEL JUEGO", "YA NO QUEDAN JUGADAS DISPONIBLES.")
            juego.destroy()
            return

        fila_de_jugada = lista_jugadas[numero_de_jugada]
        valores_ingresados = []

        for casilla in fila_de_jugada[:combinacion_local]:
            elementos_en_casilla = casilla.find_all()
            if not elementos_en_casilla:
                valores_ingresados.append(None)
                continue
            tipo_elemento_dibujado = casilla.type(elementos_en_casilla[0])
            if tipo_elemento_dibujado == "oval":
                color_detectado = casilla.itemcget(elementos_en_casilla[0], "fill").strip()
                if color_detectado == "white":
                    valores_ingresados.append(None)
                else:
                    valores_ingresados.append(color_detectado)
            else:
                texto_detectado = casilla.itemcget(elementos_en_casilla[0], "text").strip()
                valores_ingresados.append(texto_detectado if texto_detectado else None)

        if any(valor is None for valor in valores_ingresados):
            messagebox.showwarning("ADVERTENCIA", "DEBE LLENAR TODA LA FILA ANTES DE CALIFICAR.")
            return

        combinacion_secreta = juego.combinacion_local_secreta
        cantidad_exactos = 0

        for posicion in range(combinacion_local):
            valor_jugador = str(valores_ingresados[posicion]).strip()
            valor_secreto = str(combinacion_secreta[posicion]).strip()

            if valor_jugador == valor_secreto:
                cantidad_exactos += 1

        total_casillas_calificacion = combinacion_local
        inicio_calificacion = combinacion_local

        for posicion_calificacion in range(total_casillas_calificacion):
            casilla_calificacion = fila_de_jugada[inicio_calificacion + posicion_calificacion]
            casilla_calificacion.delete("all")

        colores_calificacion = []

        exactos_marcados = [False] * combinacion_local
        secreto_usado = [False] * combinacion_local

        for pos in range(combinacion_local):
            if str(valores_ingresados[pos]) == str(combinacion_secreta[pos]):
                colores_calificacion.append("black")
                exactos_marcados[pos] = True
                secreto_usado[pos] = True

        for pos_jugada in range(combinacion_local):
            if exactos_marcados[pos_jugada]:
                continue

            for pos_secreta in range(combinacion_local):
                if secreto_usado[pos_secreta]:
                    continue
                if str(valores_ingresados[pos_jugada]) == str(combinacion_secreta[pos_secreta]):
                    colores_calificacion.append("#6E6E6E")
                    secreto_usado[pos_secreta] = True
                    break

        while len(colores_calificacion) < combinacion_local:
            colores_calificacion.append("white")

        random.shuffle(colores_calificacion)

        for posicion_calificacion, color_final in enumerate(colores_calificacion):
            casilla_calificacion = fila_de_jugada[inicio_calificacion + posicion_calificacion]
            casilla_calificacion.create_oval(3, 3, 17, 17, fill=color_final, outline="black", width=1)

        if cantidad_exactos == combinacion_local:
            nombre_jugador = nombre_entry.get().strip()
            if len(nombre_jugador) < 2 or len(nombre_jugador) > 30:
                messagebox.showwarning("ADVERTENCIA", "DEBE INDICAR UN NOMBRE VÁLIDO.")
                messagebox.showinfo("JUEGO TERMINADO", "¡FELICITACIONES! USTED HA GANADO.")
                juego.destroy()
                return

            if tipo_reloj == "Cronómetro":
                tiempo_total_segundos = tiempo_transcurrido

            else:
                tiempo_total_segundos = tiempo_transcurrido

            horas, resto = divmod(int(tiempo_total_segundos), 3600)
            minutos, segundos = divmod(resto, 60)
            tiempo_formateado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

            fecha_juego = datetime.datetime.now().strftime("%d/%m/%Y")

            combinacion_en_texto = []
            for elemento in combinacion_secreta:
                if tipo_de_elementos == "colores":
                    nombre_color = None
                    for nombre, codigo in colores.items():
                        if codigo == elemento:
                            nombre_color = nombre
                            break
                    if nombre_color is not None:
                        combinacion_en_texto.append(nombre_color)
                    else:
                        combinacion_en_texto.append(str(elemento))
                else:
                    combinacion_en_texto.append(str(elemento))

            combinacion_final = " ".join(combinacion_en_texto)

            if dificultad_actual == "Fácil":
                tiempos_por_jugada = ["00:00:00", "00:00:00", "00:00:00", "00:00:00", 
                                    "00:00:00", "00:00:00", "00:00:00", "00:00:00"]
            elif dificultad_actual == "Normal":
                tiempos_por_jugada = ["00:00:00", "00:00:00", "00:00:00", "00:00:00", 
                                    "00:00:00", "00:00:00", "00:00:00"]
            else:
                tiempos_por_jugada = ["00:00:00", "00:00:00", "00:00:00", 
                                    "00:00:00", "00:00:00", "00:00:00"]

            ruta_top10 = os.path.join(base_path, "mastermind2025top10.dat")

            if os.path.exists(ruta_top10):
                with open(ruta_top10, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read().strip()
                    if contenido:
                        try:
                            top10_general = eval(contenido)
                        except Exception:
                            top10_general = {"Fácil": [], "Medio": [], "Difícil": []}
                    else:
                        top10_general = {"Fácil": [], "Medio": [], "Difícil": []}
            else:
                top10_general = {"Fácil": [], "Medio": [], "Difícil": []}

            if dificultad_actual == "Normal":
                nivel_juego = "Medio"
            else:
                nivel_juego = dificultad_actual

            nueva_partida = [nombre_jugador, combinacion_final, fecha_juego, tiempos_por_jugada]

            if nivel_juego not in top10_general:
                top10_general[nivel_juego] = []

            top10_general[nivel_juego].append(nueva_partida)

            if len(top10_general[nivel_juego]) > 10:
                top10_general[nivel_juego] = top10_general[nivel_juego][:10]

            with open(ruta_top10, "w", encoding="utf-8") as archivo:
                archivo.write(str(top10_general))

            fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y")
            hora_actual = datetime.datetime.now().strftime("%I:%M %p")

            nueva_marca = Marca(
                jugador=nombre_jugador,
                tiempo_total=int(tiempo_total_segundos),
                combinacion=combinacion_final,
                fecha=fecha_actual,
                hora=hora_actual,
                nivel=dificultad_actual
            )
            if dificultad_actual == "Fácil":
                abb_facil.insertar_nodo(nueva_marca)
            elif dificultad_actual == "Normal":
                abb_medio.insertar_nodo(nueva_marca)
            else:
                abb_dificil.insertar_nodo(nueva_marca)

            combinacion_texto_lista = []
            for elemento_en_combinacion in combinacion_secreta:
                if tipo_de_elementos == "colores":
                    nombre_encontrado = None
                    for nombre_color, codigo_hex in colores.items():
                        if codigo_hex == elemento_en_combinacion:
                            nombre_encontrado = nombre_color
                            break
                    if nombre_encontrado:
                        combinacion_texto_lista.append(nombre_encontrado)
                    else:
                        combinacion_texto_lista.append(str(elemento_en_combinacion))
                else:
                    combinacion_texto_lista.append(str(elemento_en_combinacion))
            combinacion_texto = " ".join(combinacion_texto_lista)
            tiempos_por_jugada = []
            top10 = {"Fácil": [], "Medio": [], "Difícil": []}
            if os.path.exists(archivo_top10):
                with open(archivo_top10, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read().strip()
                    if contenido:
                        try:
                            top10 = eval(contenido)
                        except Exception:
                            top10 = {"Fácil": [], "Medio": [], "Difícil": []}

            if dificultad_actual == "Normal":
                nivel_actual = "Medio"
            else:
                nivel_actual = dificultad_actual
            nueva_entrada = [nombre_jugador, combinacion_texto, fecha_actual, hora_actual, tiempos_por_jugada]

            jugadores_nivel = top10.get(nivel_actual, [])
            jugadores_nivel.append(nueva_entrada)
            if len(jugadores_nivel) > 10:
                jugadores_nivel = jugadores_nivel[:10]

            top10[nivel_actual] = jugadores_nivel

            with open(archivo_top10, "w", encoding="utf-8") as archivo:
                archivo.write(str(top10))

            if datos_configuracion[0] == "Multinivel":
                niveles = ["Fácil", "Normal", "Difícil"]
                nivel_actual = juego.nivel_actual.replace("Medio", "Normal")
                indice = niveles.index(nivel_actual)

                if indice < 2:
                    siguiente = niveles[indice + 1]
                    messagebox.showinfo("AVANCE DE NIVEL", f"¡Has pasado al nivel {siguiente}!")

                    datos_configuracion[0] = "Multinivel"

                    juego.destroy()
                    jugar_multinivel(siguiente)
                    return
                video_victoria()
                juego.destroy()
                return

            video_victoria()
            return

        jugadas_realizadas.clear()
        jugadas_deshechas.clear()

        jugada_actual[0] += 1
        if jugada_actual[0] >= cantidad_jugadas:
            combinacion_texto_lista = []

            for elemento_en_combinacion in juego.combinacion_local_secreta:
                if tipo_de_elementos == "colores":
                    nombre_encontrado = None
                    for nombre_color, codigo_hex in colores.items():
                        if codigo_hex == elemento_en_combinacion:
                            nombre_encontrado = nombre_color
                            break
                    if nombre_encontrado:
                        combinacion_texto_lista.append(nombre_encontrado)
                    else:
                        combinacion_texto_lista.append(str(elemento_en_combinacion))
                else:
                    combinacion_texto_lista.append(str(elemento_en_combinacion))

            combinacion_texto = " ".join(combinacion_texto_lista)
            messagebox.showinfo("GAME OVER", f"SE HAN ACABADO LOS INTENTOS.\n\nLA COMBINACIÓN CORRECTA ERA:\n{combinacion_texto.upper()}")
            juego.destroy()
            return

        habilitar_fila(jugada_actual[0])


    boton_calificar = tk.Button(juego, image=calificar_tk, command=calificar, bg="black", cursor="hand2")
    boton_calificar.image = calificar_tk
    boton_calificar.place(x=370, y=450)
    ruta_reloj = os.path.join(base_path, "reloj.jpg")
    imagen_reloj = Image.open(ruta_reloj).resize((180, 110))
    imagen_reloj_tk = ImageTk.PhotoImage(imagen_reloj)

    frame_reloj = tk.Frame(juego, bg="black")
    frame_reloj.place(x=0, y=0)

    label_img_reloj = tk.Label(frame_reloj, image=imagen_reloj_tk, bg="black", borderwidth=0)
    label_img_reloj.image = imagen_reloj_tk
    label_img_reloj.pack()

    label_tiempo = tk.Label(frame_reloj, text="00:00:00", font=("Consolas", 10, "bold"), fg="white", bg="black")
    label_tiempo.place(x=55, y=45)

    tiempo_transcurrido = 0
    tiempo_restante = 0
    cronometro_activo = False

    def formatear_tiempo(segundos_totales):
        horas, resto = divmod(segundos_totales, 3600)
        minutos, segundos = divmod(resto, 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    def actualizar_tiempo():
        nonlocal tipo_reloj, tiempo_transcurrido, tiempo_restante, cronometro_activo

        if tipo_reloj == "Temporizador":
            if tiempo_restante > 0:
                tiempo_restante -= 1
                label_tiempo.config(text=formatear_tiempo(tiempo_restante))
                juego.after(1000, actualizar_tiempo)
            else:
                respuesta = messagebox.askyesno("TIEMPO EXPIRADO", "¿QUIERE CONTINUAR EL JUEGO?")
                if respuesta:
                    tipo_reloj = "Cronómetro"
                    cronometro_activo = True
                    actualizar_tiempo()
                else:
                    messagebox.showinfo("GAME OVER", "SE ACABÓ EL TIEMPO")
                    juego.destroy()

        elif tipo_reloj == "Cronómetro" and cronometro_activo:
            tiempo_transcurrido += 1
            label_tiempo.config(text=formatear_tiempo(tiempo_transcurrido))
            juego.after(1000, actualizar_tiempo)

    def iniciar_tiempo():
        nonlocal tiempo_restante, cronometro_activo, tipo_reloj

        if tipo_reloj == "Cronómetro":
            cronometro_activo = True
            actualizar_tiempo()

        elif tipo_reloj == "Temporizador":
            tiempo_usuario = simpledialog.askinteger("Temporizador","Ingrese el tiempo en segundos:",minvalue=1,parent=juego)

            if tiempo_usuario is None:
                tipo_reloj = "No"
                frame_reloj.place_forget()
                return

            tiempo_restante = int(tiempo_usuario)
            label_tiempo.config(text=formatear_tiempo(tiempo_restante))
            actualizar_tiempo()

        else:
            frame_reloj.place_forget()

    def cancelar():
        mensaje = tk.Label(juego, text="CANCELAR PRESIONADO",font=("Impact", 14), fg="red", bg="black")
        mensaje.place(x=400, y=520)
        juego.after(1500, mensaje.destroy)

        if iniciar["state"] == "disabled":
            respuesta = messagebox.askyesno("CANCELAR", "¿ESTÁ SEGURO DE CANCELAR EL JUEGO?")
            if respuesta:
                juego.destroy()
        else:
            return
    cancelar = tk.Button(juego, image=cancelar_tk, command= cancelar, bg ="black", cursor = "hand2")
    cancelar.image = cancelar_tk
    cancelar.place(x=490, y=450)

    def guardar():
        mensaje = tk.Label(juego, text="GUARDAR PRESIONADO",font=("Impact", 14), fg="pink", bg="black")
        mensaje.place(x=400, y=520)
        juego.after(1500, mensaje.destroy)

        if iniciar["state"] != "disabled":
            messagebox.showwarning("ADVERTENCIA", "DEBE INICIAR EL JUEGO ANTES DE GUARDAR.")
            return
        nombre_jugador = nombre_entry.get().strip()
        if not nombre_jugador:
            messagebox.showwarning("ADVERTENCIA", "DEBE INDICAR EL NOMBRE DEL JUGADOR.")
            return

        ruta_archivo_guardado = os.path.join(base_path, "mastermind2025juegoactual.dat")
        informacion_partida = {"jugador": nombre_jugador,"dificultad": dificultad_actual,"elementos": tipo_de_elementos,"reloj": tipo_reloj,"combinacion_secreta": juego.combinacion_local_secreta,"numero_jugada_actual": jugada_actual[0],"lista_jugadas_guardadas": []}

        for fila_jugada in lista_jugadas:
            fila_registrada = []
            for casilla_canvas in fila_jugada[:combinacion_local]:
                elementos_en_casilla = casilla_canvas.find_all()
                if not elementos_en_casilla:
                    fila_registrada.append(None)
                    continue
                tipo_en_casilla = casilla_canvas.type(elementos_en_casilla[0])
                if tipo_en_casilla == "oval":
                    fila_registrada.append(casilla_canvas.itemcget(elementos_en_casilla[0], "fill"))
                elif tipo_en_casilla == "text":
                    fila_registrada.append(casilla_canvas.itemcget(elementos_en_casilla[0], "text"))
                else:
                    fila_registrada.append(None)
            informacion_partida["lista_jugadas_guardadas"].append(fila_registrada)

        contenido_existente = []
        if os.path.exists(ruta_archivo_guardado):
            with open(ruta_archivo_guardado, "r", encoding="utf-8") as archivo:
                contenido_existente = archivo.read().split("\n---\n")

        partidas_sin_repetir = []
        for bloque_guardado in contenido_existente:
            if not bloque_guardado.strip():
                continue
            lineas_bloque = bloque_guardado.split("\n")
            if not lineas_bloque:
                continue
            if lineas_bloque[0].startswith("jugador:"):
                nombre_en_archivo = lineas_bloque[0].split(":", 1)[1].strip()
                if nombre_en_archivo.lower() == nombre_jugador.lower():
                    continue
            partidas_sin_repetir.append(bloque_guardado)

        datos_a_guardar = [
            f"jugador: {informacion_partida['jugador']}",
            f"dificultad: {informacion_partida['dificultad']}",
            f"elementos: {informacion_partida['elementos']}",
            f"reloj: {informacion_partida['reloj']}",
            f"combinacion_secreta: {','.join(map(str, informacion_partida['combinacion_secreta']))}",
            f"jugada_actual: {informacion_partida['numero_jugada_actual']}"
        ]

        numero_jugada_guardada = 0
        for jugada_guardada in informacion_partida["lista_jugadas_guardadas"]:
            valores_convertidos = []
            for valor in jugada_guardada:
                if valor:
                    valores_convertidos.append(str(valor))
                else:
                    valores_convertidos.append("None")

            datos_a_guardar.append(f"jugada_{numero_jugada_guardada}: {','.join(valores_convertidos)}")
            numero_jugada_guardada += 1

        bloque_final = "\n".join(datos_a_guardar)
        partidas_sin_repetir.append(bloque_final)

        with open(ruta_archivo_guardado, "w", encoding="utf-8") as archivo:
            archivo.write("\n---\n".join(partidas_sin_repetir))

        messagebox.showinfo("GUARDAR JUEGO", "PARTIDA GUARDADA CORRECTAMENTE.")
    guardar = tk.Button(juego, image=guardar_tk, command= guardar, bg ="black", cursor = "hand2")
    guardar.image = guardar_tk
    guardar.place(x=610, y=450)

    def cargar():
        mensaje = tk.Label(juego, text="CARGAR PRESIONADO",font=("Impact", 14), fg="green", bg="black")
        mensaje.place(x=400, y=520)
        juego.after(1500, mensaje.destroy)

        if iniciar["state"] == "disabled":
            messagebox.showwarning("ADVERTENCIA", "NO PUEDE CARGAR UNA PARTIDA MIENTRAS EL JUEGO ESTÁ EN CURSO.")
            return

        nombre_jugador = nombre_entry.get().strip()
        if not nombre_jugador:
            messagebox.showwarning("ADVERTENCIA", "DEBE INDICAR EL NOMBRE DEL JUGADOR ANTES DE CARGAR.")
            return

        ruta_archivo_guardado = os.path.join(base_path, "mastermind2025juegoactual.dat")
        if not os.path.exists(ruta_archivo_guardado):
            messagebox.showwarning("ADVERTENCIA", "NO EXISTE NINGÚN JUEGO GUARDADO.")
            return

        with open(ruta_archivo_guardado, "r", encoding="utf-8") as archivo:
            contenido_archivo = archivo.read().split("\n---\n")

        partida_encontrada = None
        for bloque_guardado in contenido_archivo:
            if not bloque_guardado.strip():
                continue
            lineas_bloque = bloque_guardado.split("\n")
            if not lineas_bloque:
                continue
            if not lineas_bloque[0].startswith("jugador:"):
                continue
            nombre_en_archivo = lineas_bloque[0].split(":", 1)[1].strip()
            if nombre_en_archivo.lower() == nombre_jugador.lower():
                partida_encontrada = lineas_bloque
                break

        if partida_encontrada is None:
            messagebox.showwarning("ADVERTENCIA", "NO SE ENCONTRÓ NINGUNA PARTIDA PARA ESE JUGADOR.")
            return

        valores_restaurados = {}
        for linea_guardada in partida_encontrada:
            if ":" not in linea_guardada:
                continue
            partes_linea = linea_guardada.split(":", 1)
            clave = partes_linea[0].strip()
            valor = partes_linea[1].strip()
            valores_restaurados[clave] = valor

        dificultad_restaurada = valores_restaurados.get("dificultad", "Normal")
        elementos_restaurados = valores_restaurados.get("elementos", "colores")
        reloj_restaurado = valores_restaurados.get("reloj", "No")
        texto_combinacion = valores_restaurados.get("combinacion_secreta", "")
        texto_jugada_actual = valores_restaurados.get("jugada_actual", "0")

        combinacion_restaurada = []
        for valor_en_texto in texto_combinacion.split(","):
            valor_limpio = valor_en_texto.strip()
            if valor_limpio:
                combinacion_restaurada.append(valor_limpio)

        try:
            numero_jugada_restaurada = int(texto_jugada_actual)
        except ValueError:
            numero_jugada_restaurada = 0

        juego.combinacion_local_secreta = combinacion_restaurada
        datos_configuracion[:] = [dificultad_restaurada, elementos_restaurados, reloj_restaurado, posicion_panel]

        jugadas_restauradas = []
        for clave, texto in valores_restaurados.items():

            if not clave.startswith("jugada_"):
                continue

            sufijo = clave.replace("jugada_", "").strip()
            if not sufijo.isdigit():
                continue

            numero_jugada = int(sufijo)
            valores_crudos = texto.split(",")

            fila_convertida = []
            for valor in valores_crudos:
                valor_limpio = valor.strip().lower()

                if valor_limpio in ("none", "white", ""):
                    fila_convertida.append(None)
                else:
                    fila_convertida.append(valor)

            jugadas_restauradas.append((numero_jugada, fila_convertida))

        jugadas_restauradas.sort(key=lambda par: par[0])

        for indice, (num_fila, fila_valores) in enumerate(jugadas_restauradas):
            if indice >= len(lista_jugadas):
                break

            fila_canvas = lista_jugadas[indice]
            for columna, valor_guardado in enumerate(fila_valores[:combinacion_local]):

                casilla = fila_canvas[columna]
                casilla.delete("all")

                if valor_guardado is None:
                    continue

                if tipo_de_elementos == "colores":
                    casilla.create_oval(5, 5, 25, 25, fill=valor_guardado, outline="black")
                else:
                    casilla.create_text(15, 15, text=valor_guardado, font=("Impact", 12), fill="black")

        jugada_actual[0] = numero_jugada_restaurada
        messagebox.showinfo("CARGAR JUEGO", f"PARTIDA DE {nombre_jugador.upper()} CARGADA CORRECTAMENTE.\n\nNIVEL: {dificultad_restaurada.upper()}\nELEMENTOS: {elementos_restaurados.upper()}\nRELOJ: {reloj_restaurado.upper()}")
        
        habilitar_fila(jugada_actual[0])

    cargar = tk.Button(juego, image=cargar_tk, command= cargar, bg ="black", cursor = "hand2")
    cargar.image = cargar_tk
    cargar.place(x=730, y=450)

    def usar_borrador():
        elemento_seleccionado["tipo"] = "borrador"
        elemento_seleccionado["valor"] = "white"
    borrador = tk.Button(juego, image=borrador_tk, command=usar_borrador, bg="black", cursor="hand2")
    borrador.image = borrador_tk
    borrador.place(x=900, y=20)


    def habilitar_fila(numero_fila_activa):
        if not juego.winfo_exists():
            return

        for indice_fila, fila_jugada in enumerate(lista_jugadas):
            for casilla_canvas in fila_jugada[:combinacion_local]:
                if indice_fila == numero_fila_activa:
                    casilla_canvas.bind("<Button-1>", colocar_en_casilla)
                else:
                    casilla_canvas.unbind("<Button-1>")

    def deshacer_movimiento():

        mensaje = tk.Label(juego, text="DESHACER PRESIONADO", font=("Impact", 14), fg="yellow", bg="black")
        mensaje.place(x=400, y=520)
        juego.after(1500, mensaje.destroy)

        if not jugadas_realizadas:
            return

        casilla_canvas, valor_previo = jugadas_realizadas.pop()
        elementos_actuales = casilla_canvas.find_all()

        if not elementos_actuales:
            estado_actual = None
        else:
            tipo_elemento = casilla_canvas.type(elementos_actuales[0])
            if tipo_elemento == "oval":
                color = casilla_canvas.itemcget(elementos_actuales[0], "fill")
                estado_actual = None if color == "white" else color
            else:
                texto = casilla_canvas.itemcget(elementos_actuales[0], "text")
                estado_actual = texto if texto else None

        jugadas_deshechas.append((casilla_canvas, estado_actual))

        casilla_canvas.delete("all")

        if valor_previo is None:
            casilla_canvas.create_oval(5, 5, 25, 25, fill="white", outline="black")
        elif isinstance(valor_previo, str) and valor_previo.startswith("#"):
            casilla_canvas.create_oval(5, 5, 25, 25, fill=valor_previo, outline="black")
        else:
            casilla_canvas.create_text(15, 15, text=str(valor_previo), font=("Impact", 12), fill="black")

    boton_deshacer = tk.Button(juego, image=deshacer_tk,command=deshacer_movimiento,bg="black", cursor="hand2", bd=0)
    boton_deshacer.image = deshacer_tk
    boton_deshacer.place(x=830, y=150)

    def rehacer_movimiento():

        mensaje = tk.Label(juego, text="REHACER PRESIONADO", font=("Impact", 14), fg="cyan", bg="black")
        mensaje.place(x=400, y=520)
        juego.after(1500, mensaje.destroy)

        if not jugadas_deshechas:
            return

        casilla_canvas, valor_rehacer = jugadas_deshechas.pop()

        elementos_actuales = casilla_canvas.find_all()
        if not elementos_actuales:
            estado_actual = None
        else:
            tipo = casilla_canvas.type(elementos_actuales[0])
            if tipo == "oval":
                color = casilla_canvas.itemcget(elementos_actuales[0], "fill")
                estado_actual = None if color == "white" else color
            else:
                txt = casilla_canvas.itemcget(elementos_actuales[0], "text")
                estado_actual = txt if txt else None

        jugadas_realizadas.append((casilla_canvas, estado_actual))

        casilla_canvas.delete("all")

        if valor_rehacer is None:
            casilla_canvas.create_oval(5, 5, 25, 25, fill="white", outline="black")
        elif isinstance(valor_rehacer, str) and valor_rehacer.startswith("#"):
            casilla_canvas.create_oval(5, 5, 25, 25, fill=valor_rehacer, outline="black")
        else:
            casilla_canvas.create_text(15, 15, text=str(valor_rehacer), font=("Impact", 12), fill="black")

    boton_rehacer = tk.Button(juego, image=rehacer_tk,command=rehacer_movimiento,bg="black", cursor="hand2", bd=0)
    boton_rehacer.image = rehacer_tk
    boton_rehacer.place(x=830, y=300)

    def iniciar_juego():
        mensaje = tk.Label(juego, text="A JUGAR",font=("Impact", 16), fg="yellow", bg="black")
        mensaje.place(x=500, y=520)
        juego.after(3000, mensaje.destroy)

        nombre_jugador = nombre_entry.get().strip()
        if len(nombre_jugador) < 2 or len(nombre_jugador) > 30:
            messagebox.showerror("ERROR", "EL NOMBRE DEBE ESTAR ENTRE 2 Y 30 CARACTERES")
            return
        iniciar.config(state="disabled")
        nombre_entry.config(state="readonly")

        elementos_restringidos = obtener_elementos_segun_dificultad(tipo_de_elementos, dificultad_actual)

        if tipo_de_elementos == "colores":
            conjunto_elementos = list(elementos_restringidos.values())
        else:
            conjunto_elementos = list(elementos_restringidos)

        combinacion_local_secreta = []
        repetidos_permitidos = (permitir_repetidos == "Sí")

        for posicion_actual in range(combinacion_local):
            elemento_aleatorio = random.choice(conjunto_elementos)

            if not repetidos_permitidos:
                while elemento_aleatorio in combinacion_local_secreta:
                    elemento_aleatorio = random.choice(conjunto_elementos)

            combinacion_local_secreta.append(elemento_aleatorio)

        juego.combinacion_local_secreta = combinacion_local_secreta

        if tipo_reloj != "No":
            iniciar_tiempo()

        habilitar_fila(0)
    iniciar.config(command=iniciar_juego)

def jugar_multinivel(nivel_siguiente):
    """
    FUNCIÓN: Inicia el siguiente nivel en modo Multinivel.
    ENTRADAS: nivel_siguiente -> "Fácil", "Normal" o "Difícil".
    SALIDAS: Abre una nueva ventana de juego con la dificultad ajustada.
    """
    datos_configuracion[0] = nivel_siguiente  
    jugar()

def configurar():
    """FUNCIÓN: CONFIGURAR PARÁMETROS DEL JUEGO  
    ENTRADAS:  
        Opciones seleccionadas por el usuario (dificultad, elementos, reloj, posición, repetidos).  
    SALIDAS:  
        - Guarda las opciones en el archivo mastermind2025configuración.dat.  
        - Actualiza la estructura datos_configuracion.  
        - Permite definir símbolos personalizados.  
    """
    configuracion = tk.Toplevel(mastermind)
    configuracion.title("MasterMindV2: Configurar")
    configuracion.geometry("650x356")

    base_path = os.path.dirname(__file__)  
    ruta_gif = os.path.join(base_path, "fondo.gif")  
    gif = Image.open(ruta_gif)

    frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif)]

    label_fondo = tk.Label(configuracion)
    label_fondo.place(x=0, y=0, relwidth=1, relheight=1)

    animar(configuracion, label_fondo, frames)

    tk.Label(configuracion, text="CONFIGURACIÓN DE MASTERMIND",font=("Impact", 16), fg="white", bg="black").pack(pady=10)
    tk.Label(configuracion, text="Dificultad:", font=("Impact", 12), fg="white", bg="black").pack()
    opcion_nivel = tk.StringVar(value="Difícil")
    niveles_disponibles = ["Fácil", "Normal", "Difícil", "Multinivel"]
    for nivel in niveles_disponibles:
        tk.Radiobutton(configuracion, text=nivel, variable=opcion_nivel, value=nivel,font=("Impact", 12), fg="white", bg="black",selectcolor="black").pack()
    tk.Label(configuracion, text="Tipo de elementos:", font=("Impact", 12), fg="white", bg="black").pack(pady=(10, 0))
    opciones = tk.StringVar(value="colores")
    for tipo in ["colores", "numeros", "letras", "simbolos"]:
        tk.Radiobutton(configuracion, text=tipo.capitalize(), variable=opciones, value=tipo, font=("Impact", 12), fg="white", bg="black", selectcolor="black").pack()
    tk.Label(configuracion,text="Tipo de reloj:",font=("Impact", 12),fg="white",bg="black").place(x=30, y=0)
    valor_tipo_reloj = tk.StringVar(value="No")
    opciones_reloj = [("Cronómetro", 20), ("Temporizador", 50), ("No", 80)]
    for nombre_opcion_reloj, posicion_y in opciones_reloj:
        tk.Radiobutton(configuracion,text=nombre_opcion_reloj,variable=valor_tipo_reloj,value=nombre_opcion_reloj,font=("Impact", 12),fg="white",bg="black",selectcolor="black").place(x=30, y=posicion_y)
    tk.Label(configuracion, text="Posición:", font=("Impact", 12),fg="white", bg="black").place(x=520, y=0)
    valor_posicion = tk.StringVar(value="Derecha")
    opciones_posicion = [("Derecha", 30), ("Izquierda", 60)]
    for nombre_opcion, y in opciones_posicion:
        tk.Radiobutton(configuracion, text=nombre_opcion,variable=valor_posicion, value=nombre_opcion,font=("Impact", 12), fg="white", bg="black",selectcolor="black").place(x=520, y=y)
    tk.Label(configuracion, text="Repetidos:", font=("Impact", 12), fg="white", bg="black").place(x=520, y=120)
    opcion_repetidos = tk.StringVar(value="No")
    tk.Radiobutton(configuracion, text="No", variable=opcion_repetidos, value="No",
                font=("Impact", 12), fg="white", bg="black", selectcolor="black").place(x=520, y=140)
    tk.Radiobutton(configuracion, text="Sí", variable=opcion_repetidos, value="Sí",
                font=("Impact", 12), fg="white", bg="black", selectcolor="black").place(x=520, y=170)

    def guardar_configuracion_en_archivo():
        with open(archivo_configuracion, "w", encoding="utf-8") as archivo:
            for dato in datos_configuracion:
                archivo.write(str(dato) + "\n")



    def confirmar_guardado():
        datos_configuracion.clear()
        datos_configuracion.append(opcion_nivel.get())        
        datos_configuracion.append(opciones.get())               
        datos_configuracion.append(valor_tipo_reloj.get())      
        datos_configuracion.append(valor_posicion.get())       
        datos_configuracion.append(opcion_repetidos.get()) 
        if opciones.get() == "simbolos":
            entrada_simbolos = simpledialog.askstring("Símbolos personalizados","Ingrese símbolos separados por comas:")
            if entrada_simbolos:
                simbolos_procesados = [s.strip() for s in entrada_simbolos.split(",") if s.strip()]
                elementos["simbolos"] = simbolos_procesados
                datos_configuracion.append(",".join(simbolos_procesados))
            else:
                datos_configuracion.append("")
        else:
            datos_configuracion.append("")

        guardar_configuracion_en_archivo()
        messagebox.showinfo("Configuración", "Opciones guardadas correctamente <3")
        configuracion.destroy()

    tk.Button(configuracion,text="Guardar",font=("Impact", 12),fg="black",bg="light blue",command=confirmar_guardado).place(x=100, y=200)

def resumen_de_marcas():
    """FUNCIÓN: MOSTRAR LISTA RESUMIDA DE TODAS LAS MARCAS REGISTRADAS  
    ENTRADAS: NINGUNA.  
    SALIDAS:  
        - Abre una ventana con todas las marcas ordenadas por tiempo (ABB).  
        - Se muestran únicamente nombre del jugador y tiempo total.  
    """

    ventana = tk.Toplevel(mastermind)
    ventana.title("Resumen de Marcas")
    ventana.geometry("450x500")
    ventana.config(bg="black")

    tk.Label(ventana, text="RESUMEN DE MARCAS", font=("Impact", 16), fg="white", bg="black").pack(pady=10)

    def mostrar(nivel, abb):
        tk.Label(ventana, text=f"--- NIVEL {nivel.upper()} ---", fg="yellow", bg="black", font=("Impact", 12)).pack()
        marcas = abb.recorrer_arbol()
        if not marcas:
            tk.Label(ventana, text="Sin marcas registradas", fg="white", bg="black").pack()
        for marca in marcas:
            tk.Label(ventana, text=marca.desplegar_marca_resumen(), fg="white", bg="black").pack()

    mostrar("Fácil", abb_facil)
    mostrar("Normal", abb_medio)
    mostrar("Difícil", abb_dificil)

def detalle_de_marcas():
    """FUNCIÓN: MOSTRAR DETALLE COMPLETO DE MARCAS REGISTRADAS  
    ENTRADAS: NINGUNA.  
    SALIDAS:  
        - Abre una ventana con información detallada: jugador, combinación, fecha, hora y tiempo.  
        - Extrae datos ordenados desde el ABB correspondiente.  
    """
    ventana = tk.Toplevel(mastermind)
    ventana.title("Detalle de Marcas")
    ventana.geometry("700x500")
    ventana.config(bg="black")

    tk.Label(ventana, text="DETALLE DE MARCAS", font=("Impact", 16), fg="white", bg="black").pack(pady=10)

    def mostrar(nivel, abb):
        tk.Label(ventana, text=f"--- NIVEL {nivel.upper()} ---", fg="cyan", bg="black", font=("Impact", 12)).pack()
        marcas = abb.recorrer_arbol()
        if not marcas:
            tk.Label(ventana, text="Sin marcas registradas", fg="white", bg="black").pack()
        for marca in marcas:
            tk.Label(ventana, text=marca.desplegar_marca_detalle(), fg="white", bg="black").pack()

    mostrar("Fácil", abb_facil)
    mostrar("Normal", abb_medio)
    mostrar("Difícil", abb_dificil)

def ayuda():
    """FUNCIÓN: MOSTRAR AYUDA AL USUARIO  
    ENTRADAS: EVENTO DEL MENÚ O BOTÓN “AYUDA”.  
    SALIDAS: ABRE EL ARCHIVO ‘manual_de_usuario_mastermindV2.PDF’ QUE EXPLICA CÓMO USAR EL PROGRAMA."""

    messagebox.showinfo("AYUDA", "Ejecutando el manual del usuario...")
    base_path = os.path.dirname(os.path.abspath(__file__))
    manual = os.path.join(base_path, "manual_de_usuario_mastermindV2.PDF")
    os.startfile(manual)

def acerca_de():
    messagebox.showinfo(
        "ACERCA DE",
        "NOMBRE DEL PROGRAMA: MASTERMINDV2  \n"
        "VERSIÓN DE PYTHON: 3.13.3  \n" 
        "FECHA DE CREACIÓN: 01/12/2025  \n"
        "AUTOR: JOSHUA BRENES HERNÁNDEZ")

def salir():
    """FUNCIÓN: SALIR DEL PROGRAMA  
    ENTRADAS: CONFIRMACIÓN DEL USUARIO DESDE UN CUADRO EMERGENTE.  
    SALIDAS: CIERRA LA VENTANA PRINCIPAL Y FINALIZA LA EJECUCIÓN DEL SOFTWARE."""

    confirmacion = messagebox.askyesno("Salir", "¿Desea salir del programa?")
    if confirmacion:
        mastermind.destroy()

menu = tk.Menu(mastermind)
menu.add_command(label="Jugar", command=jugar)
menu.add_command(label="Configurar", command=configurar)
menu.add_command(label="Resumen de Marcas ", command=resumen_de_marcas)
menu.add_command(label="Detalle de marcas ", command=detalle_de_marcas)
menu.add_command(label="Ayuda", command=ayuda)
menu.add_command(label="Acerca de", command=acerca_de)
menu.add_command(label="Salir", command=salir)

mastermind.config(menu=menu)
cargar_configuracion()
mastermind.mainloop()
