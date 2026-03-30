Anotaciones de los proyectos

    Modularidad/SoC (Separation of concerns) -> Para que un error en un lado no rompa todo.

    patch vs post (lo entendi mejor) -> SEMANTICA REST
    patch -> Se usa para modificar datos existentes del recurso. 
    post -> Se usa para crear un nuevo recurso o registrar un suceso.

    pydantic/Field
    class config:
	from_attributes = true

    with_for_update: Lo que nos ayuda a cerrar la puerta si dos personas quieren el mismo producto.

    Atomicidad: El db.commit() se hace al final de todo. O se guarda el movimiento y se acutaliza el stock o no
    se guarda nada.
    db.rollback(): Si falla el commit o el add en el try deshace cualqueir cambio pendiente para que la base de datos quede limpia
 
	Schema:
    MovementBase(BaseModel) -> Es el molde
    MovementCreate(MovementBase) -> Es el filtro de entrada (Solo el usuario lo toca)
    MovementResponse(MovementBase)-> Es el filtro de salida 

    "Inyección de dependencias" Depends(get_db) -> Depends siempre se ejecuta antes de la función y si todo va bien te devuelve lo pedido. (Cierra la db automaticamente)
     "Validación automática"/response_model=schemas.Product

     
    response_model=Product -> es pydantic no SQLAlchemy

    # Llamamos a tu service blindado
    return update_stock(product_id=product_id, movement_data=movement, db=db)
    Qué hace: Agarra lo que sale de la base de datos (que a veces tiene datos mugrientos o secretos) y lo pasa por el colador del Schema.

    Por qué importa: Si tu tabla de User tiene el campo password, pero tu response_model es UserPublic (que no tiene ese campo), FastAPI garantiza que la contraseña nunca salga a internet.

    Magia: Gracias al from_attributes = True, convierte el objeto raro de la base de datos en un JSON perfecto que entiende el navegador.

    from services import products_services -> best practice -> products_services.method

    Como enfrentar un error de back 3 capas
    ruido (stack trace largo) -> No importa al principio
    Tú código (Aca empezas a prestar atención) -> products_services.py, line 10

    3 -> El error REAL (la joya)
    ValidationError: Product
    id -> Field required
    owner_id -> Field required (ENTRAR SIEMPRE AL LINK A LEER DOC)

    
    Error: ValidationError (Pydantic pide campos que no deberian existir)
    Sintoma: Pydantic pide id, owner_id al crear objeto
    Causa: 
        Name shadowing (choque de nombres) 
        Se importo Product de schemas en vez de models
        Se uso el schema en lugar de modelo de la DB
    La pelotudes:
    Al tener 2 Clases iguales no sabia cual era de cual a partide a hora importar
    from schemas import schemas / from scheme import scheme
    Solución:
        Importe ficheros. Schema.fun Models.fun

        Tu Nueva Regla de Oro (Antiestrés):
     "Si sé cómo evitar el error y sé por qué falló mi lógica, ya sé suficiente para cobrar por mi laburo."