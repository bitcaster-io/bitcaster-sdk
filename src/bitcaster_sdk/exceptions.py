class EventNotFound(Exception):
    pass


class SDKError(Exception):
    pass


class ConfigurationError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


class ValidationError(Exception):
    pass


class RemoteValidationError(Exception):
    message = "Error %(status_code)s on remote server: %(detail)s"
