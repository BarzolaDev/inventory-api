### 🔐 Autenticación y dependencias

Uno de los principales desafíos fue implementar autenticación usando OAuth2 con PasswordBearer.

Al trabajar con dependencias como `Depends(get_current_user)`, el código comenzó a volverse difícil de escalar. Esto me llevó a refactorizar y mejorar:

* Separación de responsabilidades
* Organización en módulos (routes, services, etc.)
* Naming claro de funciones

---

### 🗄️ SQL vs ORM

Al principio sentía que usar un ORM era empezar desde cero, después de haber trabajado tanto con SQL.

Sin embargo, entendí que:

> Un ORM no reemplaza SQL, lo abstrae.

Este fue uno de los mayores puntos de aprendizaje del proyecto, ya que pude aplicar mis conocimientos desde un nivel más alto.

---

### 🔄 Flujos y naming

Comprendí la importancia de:

* Diseñar correctamente los flujos del sistema
* Nombrar funciones y estructuras de forma clara

Esto impacta directamente en la mantenibilidad y escalabilidad del código.

---

### 🧩 Rol del framework

Inicialmente veía el framework como una limitación.

Con el tiempo entendí que:

> Un framework abstrae problemas comunes para que puedas enfocarte en la lógica de negocio.

Hoy sé que puedo adaptarme a cualquier framework porque las bases son las mismas.

---

## 💡 Conclusión

Este proyecto no solo representa una API funcional, sino un cambio en mi forma de pensar el desarrollo:

* Pasar de escribir código a diseñar soluciones
* Entender abstracciones (ORMs, frameworks)
* Construir con foco en escalabilidad y claridad

Y, sobre todo, comprobar que puedo resolver problemas de manera correcta.




