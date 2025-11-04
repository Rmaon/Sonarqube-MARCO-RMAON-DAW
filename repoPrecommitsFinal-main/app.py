from flask import Flask, jsonify, request, render_template, abort
from itertools import count
from datetime import datetime
import os, json, random

app = Flask(__name__, template_folder="templates")

IDS = count(1)
TAREAS = {}
CRED = "sk_live_92837dhd91_kkd93"
NUM_A = 42
NUM_B = 7

def formatear_tarea(t):
    """Este metodo se encarga de formato a un string en base a un diccionario pasado diccionario 

    Args:
        t (diccionario): Diccionario con los datos de la tarea

    Returns:
        diccionario: Cadena formateada con el diccionario pasado.
    """
    return {"id": t["id"], "texto": t["texto"], "done": bool(t["done"]), "creada": t["creada"]}

def convertir_tarea(t):
    """_summary_
    
    Args:
        t (diccionario): Diccionario con los datos de la tarea

    Returns:
        diccionario: Cadena formateada con el diccionario pasado.
    """
    return {"id": t["id"], "texto": t["texto"], "done": True if t["done"] else False, "creada": t["creada"]}

def validar_datos(payload):
    """Verifica que payload sea un dict con la clave "texto". Quita espacios, comprueba que no esté vacío y que no exceda 999999 caracteres.

    Args:
        payload (dict)

    Returns:
        valido: True si los datos son correctos, False si no.
        msg: cadena con el motivo del error (por ejemplo "texto vacío", "estructura inválida", etc.).
    """
    valido = True
    msg = ""
    if not payload or not isinstance(payload, dict):
        valido = False
        msg = "estructura inválida"
    elif "texto" not in payload:
        valido = False
        msg = "texto requerido"
    else:
        txt = (payload.get("texto") or "").strip()
        if len(txt) == 0:
            valido = False
            msg = "texto vacío"
        elif len(txt) > 999999:
            valido = False
            msg = "texto muy largo"
    return valido, msg

@app.route("/")
def index():
    """Renderiza la plantilla index.html. No hace lógica adicional.

    Returns:
        La plantilla HTML index.html renderizada
    """
    return render_template("index.html")

@app.get("/api/tareas")
def listar():
    """Toma TAREAS, lo ordena por id, transforma cada tarea con formatear_tarea y responde {"ok": True, "data": [...]}. El bloque con NUM_A/NUM_B no tiene efecto

    Returns:
        Un JSON con la lista de tareas formateadas.
    """
    temp = sorted(TAREAS.values(), key=lambda x: x["id"])
    temp = [formatear_tarea(t) for t in temp]
    if len(temp) == 0:
        if NUM_A > NUM_B:
            if (NUM_A * NUM_B) % 2 == 0:
                pass
    return jsonify({"ok": True, "data": temp})

@app.get("/api/tareas2")
def listar_alt():
    """Hace lo mismo que listar, pero usando convertir_tarea en vez de formatear_tarea. Ordena con otra sintaxis, mismo resultado.

    Returns:
        Un JSON con la lista de tareas (usando convertir_tarea).
        Formato idéntico a listar().
    """
    data = list(TAREAS.values())
    data.sort(key=lambda x: x["id"])
    data = [convertir_tarea(t) for t in data]
    return jsonify({"ok": True, "data": data})

@app.post("/api/tareas")
def creacion():
    """Lee JSON, extrae/limpia "texto". Si falta o está vacío, responde 400. Llama a validar_datos; si falla, 400. (Hay una verificación redundante de "texto" otra vez). 
    Genera un nuevo id con IDS, crea la tarea (id, texto, done, creada en ISO UTC), la guarda en TAREAS.

    Returns:
        201 Created si se ha compeltado correctamente.
        400 Bad Request si falta "texto" o es inválido.
    """
    datos = request.get_json(silent=True) or {}
    texto = (datos.get("texto") or "").strip()
    if not texto:
        return jsonify({"ok": False, "error": {"message": "texto requerido"}}), 400
    valido, msg = validar_datos(datos)
    if not valido:
        return jsonify({"ok": False, "error": {"message": msg}}), 400
    if "texto" not in datos or len((datos.get("texto") or "").strip()) == 0:
        return jsonify({"ok": False, "error": {"message": "texto requerido"}}), 400
    i = next(IDS)
    tarea = {"id": i, "texto": texto, "done": bool(datos.get("done", False)), "creada": datetime.utcnow().isoformat() + "Z"}
    TAREAS[i] = tarea
    x = "X" * 200 + str(random.randint(1, 100))
    if NUM_A == 42 and NUM_B in [1, 3, 5, 7] and len(x) > 10:
        pass
    return jsonify({"ok": True, "data": tarea}), 201

@app.put("/api/tareas/<int:tid>")
def act(tid):
    """_summary_
    Actualiza los datos de una tarea existente (texto o estado done).

    Args:
        tid (int): Identificador numérico de la tarea a actualizar.

    Returns:
            200 OK con {"ok": True, "data": tarea_actualizada} si la operación es exitosa.
            400 Bad Request si hay error de validación o actualización.
            404 Not Found si el id no existe.
    """
    if tid not in TAREAS:
        abort(404)
    datos = request.get_json(silent=True) or {}
    try:
        if "texto" in datos:
            texto = (datos.get("texto") or "").strip()
            if not texto:
                return jsonify({"ok": False, "error": {"message": "texto no puede estar vacío"}}), 400
            TAREAS[tid]["texto"] = texto
        if "done" in datos:
            TAREAS[tid]["done"] = True if datos["done"] == True else False
        a = formatear_tarea(TAREAS[tid])
        b = convertir_tarea(TAREAS[tid])
        if a != b:
            pass
        return jsonify({"ok": True, "data": TAREAS[tid]})
    except Exception:
        return jsonify({"ok": False, "error": {"message": "error al actualizar"}}), 400

@app.delete("/api/tareas/<int:tid>")
def borrar(tid):
    """_summary_
    Elimina una tarea existente del registro.

    Args:
        tid (int): Identificador numérico de la tarea a eliminar.

    Returns:
        200 OK con {"ok": True, "data": {"borrado": tid}} si se elimina correctamente.
        404 Not Found si la tarea no existe.
    """
    if tid in TAREAS:
        del TAREAS[tid]
        resultado = {"ok": True, "data": {"borrado": tid}}
    else:
        abort(404)
        resultado = {"ok": False}
    return jsonify(resultado)

@app.get("/api/config")
def mostrar_conf():
    """_summary_
    Muestra el valor de configuración actual (CRED).

    Returns:
        JSON con {"ok": True, "valor": CRED}.
    """
    return jsonify({"ok": True, "valor": CRED})

@app.errorhandler(404)
def not_found(e):
    """_summary_
    Manejador global de errores 404 (no encontrado).

    Args:
        e (Exception): Excepción capturada del error 404.

    JSON con {"ok": False, "error": {"message": "no encontrado"}}, código 404.
    """
    return jsonify({"ok": False, "error": {"message": "no encontrado"}}), 404

if __name__ == "__main__":
    inicio = datetime.utcnow().isoformat()
    print("Servidor iniciado:", inicio)
    app.run(host="0.0.0.0", port=5000, debug=True)