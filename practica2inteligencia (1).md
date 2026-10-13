# Práctica 2: Análisis de Malware e Inteligencia

## Usar plataformas como any.run para observar análisis de malware en vivo

Para empezar con la tarea, se ha accedido a un análisis público de any.run: [https://app.any.run/tasks/85bdfec2-f33b-49c0-b1ec-0e594de79ced/](https://app.any.run/tasks/85bdfec2-f33b-49c0-b1ec-0e594de79ced/)

Durante la ejecución, se puede observar el procesamiento de un archivo comprimido en formato ZIP. Tras la descompresión usamos el *loader* para realizar la extracción de sus firmas y hashes.

## Identificar IOCs (IPs, dominios, hashes) de campañas activas

A partir de la ejecución y la extracción de artefactos en memoria, se han identificado los siguientes IOCs:

| Tipo de IOC | Valor / Indicador | Descripción / Contexto |
| :--- | :--- | :--- |
| Nombre de archivo | `助记词.zip` | Archivo comprimido (malware). |
| Hash MD5 | `1b672cb1e978431c87d46b36c827cdd8` | Huella digital MD5 del archivo original `助记词.zip`. |
| Hash SHA-1 | `993bf49feb599d60f60309264366324967753ab3` | Huella digital SHA-1 del archivo original. |
| Hash SHA-256 | `336c0ea7f5c6661152e1856b64df3f7ef3720336bb4f78b187f0802e5ffc0210` | Huella digital SHA-256 del archivo original. |
| Proceso malicioso | `+·+¦¦-.exe` | Ejecutable ofuscado que se inicia tras extraer el archivo `.zip`. |
| Proceso Malicioso | `Setp.exe` | Proceso secundario encargado de soltar librerías y modificar archivos de usuario. |
| Proceso Inyectado | `TGFile.exe` | Proceso utilizado para inyectar y ocultar el código malicioso directamente en la memoria. |
| Firma en Memoria | `DonutLoader` | Regla YARA detectada dentro del proceso `TGFile.exe` (PID: 5652) que indica ejecución de shellcode en RAM. |
| Mutex | `VALLEYRAT` | Marca de exclusión mutua creada por `TGFile.exe` para asegurar que el troyano ValleyRAT no infecte la máquina dos veces simultáneas. |

## Subir muestras a VirusTotal para mirar telemetría y detección

Al consultar el hash en VirusTotal, se da una tasa de detección de **6/67**.

### Clasificación del Motor de Antivirus
El malware es identificado bajo la familia `trojan.beog/chinad`. Entre las firmas más destacadas se encuentran:
*   **AliCloud:** `Backdoor:Win/shellcode.api(dyn)`
*   **Kaspersky:** `Trojan.Win32.Shelm.beog`

### Actividad de Red (C2)
El análisis de tráfico reveló comunicaciones dirigidas a la infraestructura de comando y control (C2):
*   **Dirección IP / Puerto:** `202.61.85.76:7865`
*   **Recursos solicitados:** Descarga de archivos secundarios mediante peticiones HTTP, más específicamente `123.jpg`, `1.log` y `1.txt`.

### Dropped Files
Durante la infección, el archivo crea y ejecuta múltiples archivos en el sistema de archivos local:
*   `Setp.exe` (Binario de soporte)
*   `123.bat` (Script de automatización/comandos)
*   `1.zip` y `2.zip` (Contenedores adicionales de componentes/librerías)

---

## Informe Final y Conclusiones 

### Resumen del Análisis Dinámico
*   **Fase de Descompresión y Despliegue:** La cadena de infección comienza con el archivo comprimido `助记词.zip`, del cual se extrae un ejecutable con un nombre muy confuso (`+·+¦¦-.exe`). 
*   **Ejecución de Comandos y Persistencia:** Al ejecutarse, este primer binario invoca intérpretes del sistema como `powershell.exe` y `cmd.exe` para procesar instrucciones en segundo plano y depositar el binario secundario `Setp.exe`.
*   **Inyección en Memoria:** A través del DonutLoader, se realiza la inyección de shellcode en el proceso real `TGFile.exe` (PID: 5652). La carga útil inyectada corresponde al troyano de acceso remoto ValleyRAT, el cual establece un Mutex denominado `VALLEYRAT` para asegurar una única petición activa en el sistema afectado.
*   **Perfilado e Identificación:** Antes de establecer persistencia total o recibir comandos del servidor C2 (`202.61.85.76`), el malware define el entorno comprometido, recopilando la fecha de instalación del SO, el nombre del equipo y la configuración regional de idioma, técnica orientada tanto a esquivar entornos de prueba (sandboxes) como a categorizar a las víctimas. 

### Conclusión 
Los hallazgos recopilados durante el análisis dinámico coinciden plenamente con la telemetría y firmas identificadas en VirusTotal. Se puede observar que corresponde con una campaña activa de distribución de ValleyRAT, utilizando cargadores basados en DonutLoader para evadir la detección estática en disco mediante inyección directa en memoria RAM.

## Referencias
*   [Reporte en ANY.RUN](https://any.run/report/336c0ea7f5c6661152e1856b64df3f7ef3720336bb4f78b187f0802e5ffc0210/85bdfec2-f33b-49c0-b1ec-0e594de79ced)
*   [Relaciones en VirusTotal](https://www.virustotal.com/gui/file/336c0ea7f5c6661152e1856b64df3f7ef3720336bb4f78b187f0802e5ffc0210/relations)
*   [Tarea original interactiva en ANY.RUN](https://app.any.run/tasks/85bdfec2-f33b-49c0-b1ec-0e594de79ced?p=6ace497a8bb3bda8f7fb830c)