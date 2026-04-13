import json
from uuid import uuid4

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from apps.shipping.models import Shipment


def serialize_shipment(shipment):
    return {
        "id": shipment.id,
        "order_id": shipment.order_id,
        "recipient_name": shipment.recipient_name,
        "phone": shipment.phone,
        "address": shipment.address,
        "method": shipment.method,
        "status": shipment.status,
        "tracking_code": shipment.tracking_code,
        "created_at": shipment.created_at.isoformat(),
    }


@csrf_exempt
def shipments_api(request):
    if request.method == "GET":
        shipments = Shipment.objects.all()[:20]
        return JsonResponse({"items": [serialize_shipment(shipment) for shipment in shipments]})

    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    required_fields = ["order_id", "recipient_name", "phone", "address"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return JsonResponse({"detail": "Missing required shipment fields.", "missing": missing}, status=400)

    defaults = {
        "recipient_name": payload["recipient_name"],
        "phone": payload["phone"],
        "address": payload["address"],
        "method": payload.get("method", "Standard delivery"),
        "status": payload.get("status", Shipment.Status.PREPARING),
        "tracking_code": payload.get("tracking_code", f"SHP-{uuid4().hex[:10].upper()}"),
    }
    shipment, created = Shipment.objects.update_or_create(order_id=payload["order_id"], defaults=defaults)
    return JsonResponse(serialize_shipment(shipment), status=201 if created else 200)


def shipment_detail_api(request, order_id):
    shipment = get_object_or_404(Shipment, order_id=order_id)
    return JsonResponse(serialize_shipment(shipment))
