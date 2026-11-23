def v1_create_order(body):
    return {
        "status": "created",
        "version": "v1",
        "account_id": body.get("account_id"),
        "message": "Processed by legacy handler v1",
    }


def v2_create_order(body):
    return {
        "status": "created",
        "version": "v2",
        "account_id": body.get("account_id"),
        "message": "Processed by new handler v2",
    }