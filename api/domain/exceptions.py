

# Excepciones de dominio
class ProductNotFoundError(Exception):
    pass


class InsufficientStockError(Exception):
    pass

class InvalidPriceError(Exception):
    pass