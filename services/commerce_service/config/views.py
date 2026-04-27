import json
import os

import httpx
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")


def health(request):
    return JsonResponse({"status": "ok", "service": "commerce-service"})


@csrf_exempt
@require_POST
def ai_chat(request):
    try:
        body = json.loads(request.body)
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{AI_SERVICE_URL}/api/ai/chat/", json=body)
            resp.raise_for_status()
            return JsonResponse(resp.json())
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=502)
