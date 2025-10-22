from firebase_functions import https_fn
from firebase_admin import initialize_app
from google.ads.googleads.client import GoogleAdsClient
import json

initialize_app()

@https_fn.on_request()
def deleteasset(req: https_fn.Request) -> https_fn.Response:
    origin = req.headers.get("Origin", "")
    allowed_origin = "https://localhost:5173"

    cors_headers = {
        "Access-Control-Allow-Origin": allowed_origin if origin == allowed_origin else origin,
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "3600",
        "Vary": "Origin"
    }

    if req.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=cors_headers)


    try:
        data = req.get_json(force=True)
        print(f"Request data: {data}", flush=True)

        customer_id = data.get("customerId")
        resource_name = data.get("campaign_asset_resource_name")
        refresh_token = data.get("refresh_token")

        if not all([customer_id, resource_name, refresh_token]):
            raise ValueError("Missing required fields: customerId, campaign_asset_resource_name, or refresh_token")

        credentials = {
            "developer_token": "ysenaUzfvUoxtU-bz_BDrQ",
            "client_id": "316570583917-qqb4qba9v88asc500sdlc84v7gnbeg79.apps.googleusercontent.com",
            "client_secret": "5cfcsvUmp842qhX-EZerCD7s",
            "refresh_token": refresh_token,
            "use_proto_plus": True,
        }

        client = GoogleAdsClient.load_from_dict(credentials)
        result = remove_campaign_asset(client, customer_id, resource_name)

        return https_fn.Response(
            json.dumps(result),
            status=200,
            headers=cors_headers,
            mimetype="application/json"
        )

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", flush=True)
        return https_fn.Response(
            json.dumps({"success": False, "error": str(e)}),
            status=500,
            headers=cors_headers,
            mimetype="application/json"
        )

def remove_campaign_asset(client, customer_id, resource_name):
    print(f"resource_name={resource_name}", flush=True)
    if not customer_id or not resource_name:
        return {"success": False, "error": "Missing customer_id or resource_name"}

    try:
        if "campaignAssets" in resource_name:
            service = client.get_service("CampaignAssetService")
            operation = client.get_type("CampaignAssetOperation")
            operation.remove = resource_name
            response = service.mutate_campaign_assets(
                customer_id=str(customer_id),
                operations=[operation]
            )
        elif "assetGroupAssets" in resource_name:
            service = client.get_service("AssetGroupAssetService")
            operation = client.get_type("AssetGroupAssetOperation")
            operation.remove = resource_name
            response = service.mutate_asset_group_assets(
                customer_id=str(customer_id),
                operations=[operation]
            )
        else:
            return {"success": False, "error": "Unsupported asset type"}

        return {
            "success": True,
            "removed": response.results[0].resource_name
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }