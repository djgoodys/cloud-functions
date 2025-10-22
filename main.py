from flask import Request, Response
from firebase_admin import initialize_app
from google.ads.googleads.client import GoogleAdsClient
import json

initialize_app()

def deleteasset(request: Request) -> Response:
    origin = request.headers.get("Origin", "")
    allowed_origin = "https://localhost:5173"

    cors_headers = {
        "Access-Control-Allow-Origin": allowed_origin if origin == allowed_origin else origin,
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "3600",
        "Vary": "Origin"
    }

    if request.method == "OPTIONS":
        return Response("", status=204, headers=cors_headers)

    try:
        data = request.get_json(force=True)
        customer_id = data.get("customerId")
        resource_name = data.get("campaign_asset_resource_name")
        refresh_token = data.get("refresh_token")

        if not all([customer_id, resource_name, refresh_token]):
            raise ValueError("Missing required fields")

        credentials = {
            "developer_token": "ysenaUzfvUoxtU-bz_BDrQ",
            "client_id": "316570583917-qqb4qba9v88asc500sdlc84v7gnbeg79.apps.googleusercontent.com",
            "client_secret": "5cfcsvUmp842qhX-EZerCD7s",
            "refresh_token": refresh_token,
            "use_proto_plus": True,
        }

        client = GoogleAdsClient.load_from_dict(credentials)
        result = remove_campaign_asset(client, customer_id, resource_name)

        return Response(
            json.dumps(result),
            status=200,
            headers=cors_headers,
            mimetype="application/json"
        )

    except Exception as e:
        return Response(
            json.dumps({"success": False, "error": str(e)}),
            status=500,
            headers=cors_headers,
            mimetype="application/json"
        )

# Keep your remove_campaign_asset function unchanged