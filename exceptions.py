class NoSuchEntityException(Exception):
    """Exception zum Anzeigen, dass die angefragte Entität in der Datenbank nicht existiert."""

    def __init__(self, message='No such entity existing in the database'):
        super().__init__(message)


class NoSuchEntityTypeException(Exception):
    """Exception zum Anzeigen, dass der angegebene Entitätstyp nicht existiert."""

    def __init__(self, message='No such entity type exisiting in the database'):
        super().__init__(message)


class EntityAlreadyExistsException(Exception):
    """Exception zum Anzeigen, dass die angegebene Entität bereits in der Datenbank existiert."""

    def __init__(self, message='Such Entity already exists in the database'):
        super().__init__(message)


class IllegalEntityTypeException(Exception):
    """Exception zum Anzeigen, dass die angegebene Entität bereits in der Datenbank existiert."""

    def __init__(self, message='The given Entity type is not allowed'):
        super().__init__(message)
