import logging

# formato para audit (tiene extra fields)
audit_handler = logging.StreamHandler()
audit_handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s - %(message)s"
))

# formato general para routes/services
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

# aplicar formato especial solo al logger audit
logging.getLogger("audit").handlers.clear()
logging.getLogger("audit").addHandler(audit_handler)
logging.getLogger("audit").propagate = False