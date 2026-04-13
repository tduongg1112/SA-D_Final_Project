import json
from decimal import Decimal
from uuid import uuid4

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from apps.payments.models import PaymentRecord


def serialize_payment(payment):
    return {
        "id": payment.id,
        "order_id": payment.order_id,
        "provider": payment.provider,
        "amount": str(payment.amount),
        "status": payment.status,
        "transaction_reference": payment.transaction_reference,
        "created_at": payment.created_at.isoformat(),
    }


@csrf_exempt
def payments_api(request):
    if request.method == "GET":
        payments = PaymentRecord.objects.all()[:20]
        return JsonResponse({"items": [serialize_payment(payment) for payment in payments]})

    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    order_id = payload.get("order_id")
    amount = payload.get("amount")
    if not order_id or amount is None:
        return JsonResponse({"detail": "order_id and amount are required."}, status=400)

    defaults = {
        "provider": payload.get("provider", "MockPay"),
        "amount": Decimal(str(amount)),
        "status": payload.get("status", PaymentRecord.Status.PAID),
        "transaction_reference": payload.get("transaction_reference", f"PAY-{uuid4().hex[:10].upper()}"),
    }
    payment, created = PaymentRecord.objects.update_or_create(order_id=order_id, defaults=defaults)
    return JsonResponse(serialize_payment(payment), status=201 if created else 200)


def payment_detail_api(request, order_id):
    payment = get_object_or_404(PaymentRecord, order_id=order_id)
    return JsonResponse(serialize_payment(payment))
