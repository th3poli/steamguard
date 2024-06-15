
class UnknownException(Exception): pass

class RefreshTokenEmpty(Exception): pass
class RefreshTokenExpired(Exception): pass

class InvalidCredentials(Exception): pass
class InvalidSteamGuardCode(Exception): pass

class NoAccountName(Exception): pass
class AlreadyHasAPhoneNumber(Exception): pass # Your account already has a phone number attached to it.

# Adding Phone Number Exceptions
class EmailNotVerified(Exception): pass
class InvalidSMSCode(Exception): pass

# Adding Steam Guard Exceptions
class AlreadyHasMobileSteamGuard(Exception): pass
class UnableToGenerateCorrectCodes(Exception): pass