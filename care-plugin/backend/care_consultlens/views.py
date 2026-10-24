"""Thin authenticated proxy: Care browser -> (this Django plugin) -> ConsultLens FastAPI service.

Why a proxy? (1) the ConsultLens/Claude/AWS credentials never reach the browser, (2) Care's own JWT login protects
the endpoints, (3) only a small allow-list of ConsultLens routes is reachable.
Same pattern as care_filly, which keeps its service secret server-side and reuses Care's JWT auth.

NOT VERIFIED against a running Care instance. Before relying on it: confirm (a) how Care mounts plugin URLs
(docs say /api/<plugin-name>/), (b) the permission/facility check care_filly uses (`can_use_filly`) and mirror it,
(c) that `requests` is available in the Care image."""
import os
import re

import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

# Only these ConsultLens routes may be reached through the proxy.
ALLOWED = [
    ("GET", re.compile(r"^integrations/external/[^/]+/briefing$")),
    ("POST", re.compile(r"^patients$")),
    ("PATCH", re.compile(r"^patients/\d+$")),
    ("POST", re.compile(r"^patients/\d+/documents$")),
    ("GET", re.compile(r"^documents/\d+/file$")),
]


def _cfg(name: str, default: str = "") -> str:
    plugin_cfg = getattr(settings, "PLUGIN_CONFIGS", {}).get("care_consultlens", {})
    return plugin_cfg.get(name) or os.environ.get(name, default)


@api_view(["GET", "POST", "PATCH"])
@permission_classes([IsAuthenticated])  # TODO: add the facility-level permission check, as care_filly does
@parser_classes([JSONParser, MultiPartParser, FormParser])
def proxy(request, subpath: str):
    if not any(request.method == m and rx.match(subpath) for m, rx in ALLOWED):
        return JsonResponse({"detail": "Route not allowed"}, status=403)

    base = _cfg("CONSULTLENS_API_URL", "http://localhost:8000").rstrip("/")
    kwargs: dict = {"params": request.query_params.dict(), "timeout": 120}
    if request.method == "POST" and request.FILES:
        f = request.FILES["file"]
        kwargs["files"] = {"file": (f.name, f.read(), f.content_type)}
    elif request.method in ("POST", "PATCH"):
        kwargs["json"] = request.data

    try:
        r = requests.request(request.method, f"{base}/{subpath}", **kwargs)
    except requests.RequestException as exc:
        return JsonResponse({"detail": f"ConsultLens service unreachable: {exc}"}, status=502)
    return HttpResponse(r.content, status=r.status_code, content_type=r.headers.get("content-type", "application/json"))
