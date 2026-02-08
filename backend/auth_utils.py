"""
Authentication utilities including token blacklisting functionality
"""

# In-memory store for blacklisted tokens (in production, use Redis or database)
blacklisted_tokens = set()


def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token is blacklisted
    """
    return token in blacklisted_tokens


def blacklist_token(token: str) -> None:
    """
    Add a token to the blacklist
    """
    blacklisted_tokens.add(token)


def remove_blacklisted_token(token: str) -> None:
    """
    Remove a token from the blacklist (if it exists)
    """
    blacklisted_tokens.discard(token)


def clear_blacklisted_tokens() -> None:
    """
    Clear all blacklisted tokens (for testing purposes)
    """
    blacklisted_tokens.clear()