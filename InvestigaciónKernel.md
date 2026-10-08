Investigación kernels

08/10/2026 Jorge Menéndez

# Introducción

Para la parte de investigación se pide:

- Buscar información técnica sobre el funcionamiento de los sistemas anti-cheat a nivel kernel.
- Investigación del fallo de CrowdStrike en Julio de 2024

# Anticheats a nivel kernel

Un anticheat a nivel de kernel es un programa de seguridad que se ejecuta con los máximos privilegios posibles en el sistema operativo, normalmente se usa como seguridad en los videojuegos.

## ¿Qué es el kernel?

El kernel o núcleo, es la parte fundamental del sistema operativo que se encarga de conceder los recursos que va solicitando el software, este a su vez decide el orden de prioridad de las peticiones que recibe por importancia que él considera.

Un ejemplo de cómo funciona el kernel al iniciar un dispositivo puede ser el siguiente:

Una persona quiere acceder a su teléfono móvil. Para acceder, se requiere de una contraseña de acceso, esta contraseña se gestiona en el kernel del sistema operativo del dispositivo.

## ¿Qué son los rings?

Son anillos de protección jerárquica, estos sirven para proteger datos y la funcionalidad de la tolerancia a fallos (Failover) y comportamiento malicioso.

Estas jerarquías son impuestas por el hardware. Los anillos siguen la siguiente jerarquía; donde los más privilegiados (mayor confianza), son el número cero a menos privilegiado (menos confianza), con el mayor número de anillo. Usualmente el nivel 0 es quién interactúa directamente con el hardware, como la CPU o memoria controlando todo el sistema operativo.

A su vez, también existen distintas puertas especiales para permitir el acceso entre anillos exteriores y anillos interiores. El correcto uso de las puertas entre anillos nos permite mejorar la seguridad impidiendo que programas maliciosos usen recursos de anillos con mayor privilegio.

## ¿Cómo funciona un anticheat a nivel de kernel?

El anticheat a nivel de kernel comenzó a utilizarse ya que los procesos en modo usuario están por debajo del kernel a nivel de privilegios, por lo tanto, podían ser burlados fácilmente por trampas a nivel de controlador de kernel o hipervisor, por ejemplo, llamaban a ReadProcessMemory y podía falsificarse mediante hooking en kernel.

Al operar en el ring 0, el anticheat tiene acceso desde el inicio del sistema operativo. El funcionamiento es el siguiente:

El anticheat instala un driver firmado digitalmente desde que se arranca el sistema operativo. Se necesitan 3 piezas claves para que funcione un videojuego con el anticheat. En primer lugar, se necesitará un driver de kernel (no es el driver del anticheat), un servicio en el apartado del usuario (un videojuego) y una librería dll dentro de los archivos del videojuego.

El anticheat funciona desde el inicio del sistema operativo teniendo el control total a nivel de SYSTEM en el sistema operativo. El driver, es el encargado de controlar todos los procesos, memoria RAM dentro del sistema. A la hora de querer iniciar el juego el driver se encarga en tiempo real de verificar todos los archivos que están dentro del juego, verifica intentos de inyección, procesos en busca de programas externos para bypassear el anti-cheat.

## Arquitectura de un anticheat en el kernel

Los anticheats suelen tener una arquitectura de tres capas:

- Kernel driver
- Se lleva a cabo en el ring 0, registra callbacks, intercepta las llamadas al sistema, analiza memoria y aplica distintas protecciones. Es el componente que realmente tiene capacidad de realizar alguna acción significativa.
- Usermode service
- Se ejecuta como un servicio de Windows, normalmente con privilegios SYSTEM. Gestiona la comunicación de red con los servidores backend, administra la aplicación de prohibiciones y recopila y transmite telemetría.
- Game-injected DLL
- Se inyecta en el proceso del juego. Realiza comprobaciones en modo usuario, se comunica con el servicio y sirve como punto final para las protecciones aplicadas específicamente al proceso del juego.

## Ejemplos de anticheats

Hay muchos anticheats en el mercado, en este documento veremos dos de los más conocidos:

- Vanguard
- Ricochet

### Vanguard

Vanguard combina un controlador en modo kernel con una validación continua de la cadena de arranque de Windows y la pila de controladores.

**¿Cómo funciona Vanguard?**

Carga vgk.sys al encender el sistema, esto funciona como un controlador de boot-start, lo que quiere decir que windows lo carga antes de que la mayoría del sistema esté inicializado. Utiliza IOMMU, comprobando exactamente qué dispositivo se ha conectado y si la certificación es verdadera. En el caso de que no pueda comprobarlo, y efectivamente concluya que es software para hacer trampas, las protecciones de este sistema harán que los drivers del dispositivo empiecen a fallar.

### Ricochet

No es una única DLL, es una pila: implementa comprobaciones de integridad del cliente, telemetría y análisis de backend.

**¿Cómo funciona Ricochet?**

Es un controlador a nivel de kernel que amplía la visibilidad de los procesos, la memoria y los controladores que intentan alterar el juego.

El servidor concilia las acciones mediante física y tiempo, estudiando, picos de reacción inhumanos, visión imposible y valores atípicos de estadísticas. Monitoriza el sistema operativo en segundo plano y analiza si hay algún software de terceros o aplicaciones sospechosas intentando interactuar con el juego para dar ventajas ilegales.

&nbsp;

&nbsp;

# Fallo de CrowdStrike Julio de 2024

El 19 de julio de 2024, una actualización defectuosa de CrowdStrike provocó una interrupción masiva en más de 8,5 millones de dispositivos que utilizaban el sistema Microsoft.

Esta actualización generó errores de pantalla azul en dispositivos Windows, lo que causó interrupciones importantes en los servicios de Microsoft 365, incluidos Outlook, Teams y OneDrive. A este fenómeno se le conoce como la "pantalla azul de la muerte".

Los responsables de llevar a cabo la actualización informaron, que la interrupción fue causada por un defecto de software en la actualización el cual no fue detectado y provocó un desbordamiento de memoria (Buffer overflow).

La actualización afectó solo a los sistemas Windows que ejecutaban la versión 7.11 o posteriores.

## Origen y Causas

El problema se originó en una actualización del software antivirus Falcon de CrowdStrike, diseñado para proteger los sistemas Windows. Esta actualización iba a ser utilizada para medidas de ciberseguridad frente a ataques y respuesta de endpoints. La actualización contenía un error que, al instalarse, provocaba un fallo crítico en el sistema operativo. Hoy en día, no se ha publicado nada acerca de cuál fue el verdadero fallo dentro de ese archivo que provocó el problema.

## Impactos técnicos

- Confidencialidad: El incidente de CrowdStrike no contribuyó directamente a fallos de confidencialidad. Nadie hizo público ningún caso de exposición de datos.
- Integridad: La interrupción del servicio de CrowdStrike incluyó numerosos casos de recuperaciones fallidas y copias de seguridad dañadas. Para restaurar la funcionalidad, los sistemas afectados requirieron intervención manual, como el arranque en modo seguro para eliminar archivos de configuración específicos. Además, los dispositivos protegidos con cifrado BitLocker requirieron introducir una clave de recuperación BitLocker única de 48 dígitos para cada dispositivo.
- Disponibilidad: La pérdida de disponibilidad fue, sin duda, la lección más importante, reforzada por el sonado caso de Delta Airlines. Mientras que CrowdStrike solucionó el problema en un día, Delta tuvo que lidiar con las consecuencias durante semanas.

## Solución

CrowdStrike emitió una actualización para corregir el error e implementó medidas para evitar que este tipo de fallos vuelvan a ocurrir.

Microsoft recomendó a sus usuarios desinstalar la actualización defectuosa y e instó a CrowdStrike a mejorar sus procesos de desarrollo y pruebas.

Distintos expertos hicieron hablaron de la importancia de mantener los sistemas actualizados y contar con soluciones de seguridad confiables para protegerse contra este tipo de amenazas.

# Referencias

<https://s4dbrd.github.io/posts/how-kernel-anti-cheats-work/#1-introduction>

<https://ivsofte.biz/es/articles/vanguard-guide/>

<https://ciberseguridadtic.es/reportajes/los-principales-detalles-del-incidente-de-crowdstrike-y-microsoft-202407226156.htm>

<https://cloudsecurityalliance.org/blog/2025/07/03/what-we-can-learn-from-the-2024-crowdstrike-outage>

<https://www.congress.gov/crs-product/IF12717>

&nbsp;<https://www.premiercontinuum.com/es/resources/interrupcion-microsoft-julio-2024>

<https://tecnoloia.com/gaming/anti-cheat-a-nivel-de-kernel-que-acceso-real-tiene-en-tu-pc/>

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

[^1]: El **hooking** (o interceptación) es una técnica de programación que permite modificar, supervisar o bloquear el flujo de ejecución de un programa o del sistema operativo, interceptando funciones, mensajes o eventos antes de que lleguen a su destino original
