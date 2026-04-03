## Estoy terminando el proyecto 

Mi camino en programación no fue lineal. Durante varios años exploré distintas tecnologías como HTML, CSS, JavaScript y SQL, enfrentándome a desafíos como la búsqueda de perfección y la falta de enfoque en proyectos completos.
Este proceso me permitió entender no solo cómo escribir código, sino también cómo pensar sistemas, organizar ideas y priorizar la construcción de soluciones reales.
Este proyecto representa un punto de inflexión, donde logré consolidar esos aprendizajes en una aplicación backend con una arquitectura más clara y orientada a problemas reales.
Antes de incorporar formalmente conceptos como testing o manejo de edge cases, ya había desarrollado una base lógica trabajando con SQL y resolviendo problemas en plataformas como Codewars.
El uso de SQL me permitió entender escenarios como validaciones, integridad de datos y manejo de errores a nivel de consultas (joins, constraints, transacciones).
Por otro lado, la práctica en Codewars me ayudó a desarrollar pensamiento lógico y a considerar distintos escenarios posibles para un mismo problema.
Con el tiempo entendí que estos mismos principios se aplican directamente en el desarrollo backend, especialmente en testing y en la anticipación de edge cases.


## 🧠 Decisiones y aprendizaje

Durante el desarrollo de esta API me encontré con varios desafíos que me ayudaron a entender mejor cómo construir backend real.
No les puedo explicar la alegria y satisfacción que da el saber que sos capaz de resolver problemas de la manera correcta
en esta API Rest aprendi.

### 🔹 Arquitectura y dependencias

Uno de los principales desafíos fue la integración de autenticación mediante dependencias (OAuth2 + PasswordBearer).

Al intentar inyectar el usuario autenticado utilizando `Depends(get_current_user)`, noté que mi código comenzaba a volverse difícil de mantener y escalar.

Esto me obligó a reorganizar la estructura del proyecto, separando responsabilidades en distintos módulos (routes, services, etc.).

A partir de ese punto entendí que la arquitectura no se define al final, sino que evoluciona junto con el sistema.

---

### 🔹 SQL vs ORM 

Después de practicar SQL (joins, índices, transacciones), sentía que aprender un ORM era empezar de cero.

Con el tiempo entendí que un ORM no reemplaza SQL, sino que lo abstrae, permitiéndome trabajar con el mismo conocimiento desde otro nivel.

---

### 🔹 Flujos y naming

Otro punto clave fue comprender los flujos del sistema.

No solo es importante separar correctamente las capas, sino también usar nombres claros en funciones y estructuras, lo que hace que el código sea más entendible y mantenible.

---

### 🔹 Rol del framework

Al principio veía el framework como algo complejo, pero entendí que es una herramienta que abstrae problemas comunes.

Esto me permitió enfocarme en la lógica del negocio y dejar de verlo como una herramienta fija.

---

### 🔹 Testing

Implementé tests para validar:

Autenticación de usuarios
Reglas de negocio (ej: evitar stock negativo)
Manejo de errores ante inputs inválidos

---

### 🔹 Seguridad

Uso de Argon2 para hashing de contraseñas por su resistencia a ataques con GPU hice proyectos con Bcrypt pero queria probar Argon2 
Tokens JWT con expiración para evitar sesiones indefinidas 
Validación de datos con Pydantic (te amo pydantic) para prevenir inputs inválidos

### 🔹 Manejo de errores y edge cases

Validación de tokens inválidos o expirados
Manejo de usuarios inexistentes o desactivados
Prevención de errores por datos corruptos en el token
Control de fallos en base de datos


