# Título principal
# Subtítulo
**Negrita**
* Lista
` ` `python (código) ` ` `


## 🛠️ Arquitectura del proyecto

* ** Separación de Responsabilidades: "Se utilizaron modelos de SQLAlchemy para la persistencia de datos y esquemas de Pydantic para la validación de entrada/salida, garantizando que los datos sensibles no sean expuestos".

* **Gestión de Concurrencia: "Implementación de bloqueos pesimistas (with_for_update) en las transacciones de stock para asegurar la integridad de los datos en entornos multiusuario".