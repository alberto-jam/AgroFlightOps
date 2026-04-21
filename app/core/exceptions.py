"""Custom application exceptions mapped to HTTP status codes."""


class EntityNotFoundError(Exception):
    """Entity not found — maps to HTTP 404."""

    def __init__(self, message: str = "Recurso não encontrado"):
        self.message = message
        super().__init__(self.message)


class DuplicateEntityError(Exception):
    """Uniqueness violation — maps to HTTP 409."""

    def __init__(self, message: str = "Registro duplicado"):
        self.message = message
        super().__init__(self.message)


class InvalidStateTransitionError(Exception):
    """Invalid status transition — maps to HTTP 409."""

    def __init__(self, message: str = "Transição de status inválida"):
        self.message = message
        super().__init__(self.message)


class BusinessRuleViolationError(Exception):
    """Business rule violation — maps to HTTP 422."""

    def __init__(self, message: str = "Violação de regra de negócio", errors: list | None = None):
        self.message = message
        self.errors = errors or []
        super().__init__(self.message)


class InsufficientStockError(Exception):
    """Insufficient stock — maps to HTTP 422."""

    def __init__(self, message: str = "Saldo insuficiente"):
        self.message = message
        super().__init__(self.message)


class DependencyActiveError(Exception):
    """Cannot deactivate entity with active dependencies — maps to HTTP 409."""

    def __init__(self, message: str = "Entidade possui dependências ativas"):
        self.message = message
        super().__init__(self.message)
