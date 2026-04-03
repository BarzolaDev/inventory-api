## Estoy terminando el proyecto 

Mi camino en programación no fue lineal. Durante varios años exploré distintas tecnologías como HTML, CSS, JavaScript y JQuery enfrentándome a desafíos como la búsqueda de perfección y la falta de enfoque en proyectos completos.
Después de varias idas y vueltas este proceso me permitió entender no solo cómo escribir código, sino también cómo pensar sistemas, organizar ideas y priorizar la construcción de soluciones reales.
Este proyecto representa un punto de inflexión, donde logré consolidar esos aprendizajes en una aplicación backend con una arquitectura más clara y orientada a problemas reales.
Antes de incorporar formalmente conceptos como testing o manejo de edge cases mientras iba desarrollando la api yo ya pensaba en esos casos por la lógica que venia plantando en
SQL y resolviendo problemas en plataformas como Codewars (Pyhthon y JS).
El uso de SQL me permitió entender escenarios como validaciones, integridad de datos y manejo de errores a nivel de consultas (joins, constraints, transacciones).
Por otro lado, la práctica en Codewars me ayudó a desarrollar pensamiento lógico y a considerar distintos escenarios posibles para un mismo problema.
Con el tiempo entendí que estos mismos principios se aplican directamente en el desarrollo backend, especialmente en testing y en la anticipación de edge cases.

### 🔹 Cosas a implementar (qué tenian significado y yo ya implementaba por conocimiento puro):

Testing Manejo de errores y edge cases

## 🧠 Decisiones y aprendizaje

Durante el desarrollo de esta API me encontré con varios desafíos que me ayudaron a entender mejor cómo construir backend real.
No les puedo explicar la alegria y satisfacción que da el saber que sos capaz de resolver problemas de la manera correcta
en esta API Rest aprendi.

### 🔹 Arquitectura, dependencias y Flujos...

Uno de los principales desafíos fue la integración de autenticación mediante dependencias (OAuth2 + PasswordBearer).

Al intentar inyectar el usuario autenticado utilizando `Depends(get_current_user)`, noté que mi código comenzaba a volverse difícil de mantener y escalar.

Yo ya tenia mi código organizado en módulos (routes, services, etc.) pero el no poder implementar la dependencia del get_current_user me hizo pensar

en refactorizar el código (yo aca pensaba que tenia que refactorizar al final) y adémas gracias a esto entendi, que también viene bien el dividir 

ficheros y NOMBRAR BIEN LAS FUNCIONES.

---

### 🔹 SQL vs ORM 

Después de practicar SQL (joins, índices, transacciones), sentía que aprender un ORM era empezar de cero.

Con el tiempo en esta API entendí que un ORM no reemplaza SQL, sino que lo abstrae, permitiéndome trabajar con el mismo conocimiento desde otro nivel.

de los mejores CLICKS que tuve y agradeci haberme ejercitado tanto en SQL Workbench.

---

### 🔹 Flujos y naming

(Intento explicarlo mejor)

Otro punto clave fue comprender los flujos del sistema.

No solo es importante separar correctamente las capas, sino también usar nombres claros en funciones y estructuras, lo que hace que el código sea más entendible y mantenible.

---

### 🔹 Rol del framework (Igual al del orm)

Al principio veía el framework como algo que me limitaba, pero entendí que es una herramienta que abstrae problemas comunes.

Esto me permitió enfocarme en la lógica del negocio y dejar de verlo como una herramienta fija.

Ahora se que puedo manejar cualquier framework de mi lenguaje las bases son las mismas.






