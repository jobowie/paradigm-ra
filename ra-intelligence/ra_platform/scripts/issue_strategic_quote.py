from ra_platform.billing.models import QuoteStatus
from ra_platform.billing.service import send_quote
from ra_platform.persistence.sqlite import (
    create_connection,
    initialize_database,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteQuoteRepository,
)
from ra_platform.security.tokens import (
    generate_public_token,
    hash_public_token,
)
from ra_platform.scripts.create_strategic_quote import (
    STRATEGIC_ID,
    STRATEGIC_QUOTE_ID,
)


def main():
    connection = create_connection()
    initialize_database(connection)

    repository = SQLiteQuoteRepository(
        connection
    )

    quote = repository.get_for_client(
        quote_id=STRATEGIC_QUOTE_ID,
        client_organization_id=STRATEGIC_ID,
    )

    if quote is None:
        raise RuntimeError(
            "Strategic Crime Prevention quote does not exist."
        )

    if quote.status == QuoteStatus.DRAFT:
        send_quote(quote)
        repository.update(quote)

    token = generate_public_token()

    repository.assign_public_token_hash(
        quote_id=quote.id,
        public_token_hash=hash_public_token(
            token
        ),
    )

    connection.commit()
    connection.close()

    print()
    print("========================================")
    print("PARADIGM RA — QUOTE ISSUED")
    print("========================================")
    print("Client: Strategic Crime Prevention")
    print(f"Quote:  {quote.quote_number}")
    print(f"Status: {quote.status.value}")
    print(f"Total:  ${quote.total}")
    print()
    print("TOKEN:")
    print(token)
    print()
    print("LOCAL URL:")
    print(
        "http://127.0.0.1:8000"
        f"/quotes/public/{token}"
    )
    print("========================================")


if __name__ == "__main__":
    main()
