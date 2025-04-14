# 🧪 Actividad 11 (2.4) - Productor-Consumidor

**Materia:** Seminario de Uso, Adaptación y Explotación de Sistemas Operativos  
**Docente:** Violeta del Rocío Becerra Velázquez  
**Integrantes:**  
- Said Omar Hernández Grande  
- Tania Joseline Reséndiz Díaz  

---

## 📌 Descripción

Este programa simula el problema clásico del **Productor-Consumidor** mediante una **interfaz gráfica desarrollada con Tkinter**. Utiliza un **buffer circular de 25 espacios** y sincronización con **semáforos** para representar cómo un proceso productor genera elementos y un proceso consumidor los retira, todo en tiempo real y de forma concurrente.

---

## ⚙️ Requisitos

Antes de ejecutar el programa, asegúrate de tener Python instalado y ejecuta los siguientes comandos para instalar las librerías necesarias:

```bash
pip install tk
pip install messagebox
pip install colorama
pip install keyboard
pip install thread

```bash
⚠️ Nota: En algunas versiones de Python, tk y messagebox ya vienen incluidos con tkinter. Si ves errores, intenta instalar solo tkinter con:
pip install tkinter

```bash
##🚀 Ejecución
Puedes ejecutar el archivo principal del programa desde tu terminal o entorno de desarrollo favorito:
python productor_consumidor.py

```bash
##📚 Conclusión
Este proyecto permitió comprender y aplicar conceptos clave de la concurrencia en sistemas operativos, como la sincronización mediante semáforos, evitando condiciones de carrera, interbloqueos e inanición. Además, se desarrolló una interfaz gráfica intuitiva para visualizar en tiempo real el comportamiento del productor y el consumidor.