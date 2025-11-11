"""
FMCSA API integration endpoints.
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from app.schemas import FMCSAVerifyRequest, FMCSAVerifyResponse
from app.config import settings
import httpx

router = APIRouter()


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@router.post(
    "/verify",
    response_model=FMCSAVerifyResponse,
    dependencies=[Depends(verify_api_key)],
)
async def verify_mc_number(request: FMCSAVerifyRequest):
    """
    Verify a motor carrier MC number using FMCSA API.

    Requires FMCSA_API_KEY to be configured in environment variables.
    """
    mc_number = request.mc_number.strip()

    if not settings.FMCSA_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="FMCSA_API_KEY is not configured. Please set it in your .env file.",
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {"webKey": settings.FMCSA_API_KEY}
            url = f"{settings.FMCSA_API_URL}/{mc_number}"

            response = await client.get(url, params=params)

            if settings.APP_DEBUG:
                print(f"FMCSA API Response Status: {response.status_code}")
                print(f"FMCSA API Response Headers: {dict(response.headers)}")

            if response.status_code == 200:
                try:
                    data = response.json()
                except Exception as e:
                    return FMCSAVerifyResponse(
                        mc_number=mc_number,
                        is_valid=False,
                        details={
                            "error": "Failed to parse FMCSA API response",
                            "raw_response": response.text[:500],
                            "parse_error": str(e),
                        },
                    )

                if not isinstance(data, dict):
                    return FMCSAVerifyResponse(
                        mc_number=mc_number,
                        is_valid=False,
                        details={
                            "error": "FMCSA API returned unexpected format",
                            "raw_response": str(data)[:500],
                        },
                    )

                content = data.get("content")

                if content is None:
                    # Content is null - carrier might not exist or API structure is different
                    # Check if there's other data in the response
                    return FMCSAVerifyResponse(
                        mc_number=mc_number,
                        is_valid=False,
                        details={
                            "error": "Carrier not found or invalid MC number",
                            "raw_response": data,
                        },
                    )

                # Content exists, parse carrier info according to FMCSA API documentation
                # See: https://mobile.fmcsa.dot.gov/QCDevsite/docs/apiElements
                if isinstance(content, dict):
                    carrier_info = content
                else:
                    carrier_info = {}

                # Determine operating status from FMCSA fields
                # allowToOperate: Y or N, outOfService: Y or N
                allow_to_operate = carrier_info.get("allowToOperate", "").upper()
                out_of_service = carrier_info.get("outOfService", "").upper()

                if out_of_service == "Y":
                    operating_status = "OUT_OF_SERVICE"
                elif allow_to_operate == "Y":
                    operating_status = "ACTIVE"
                elif allow_to_operate == "N":
                    operating_status = "NOT_ALLOWED"
                else:
                    operating_status = "UNKNOWN"

                return FMCSAVerifyResponse(
                    mc_number=mc_number,
                    is_valid=True,
                    carrier_name=carrier_info.get("legalName")
                    or carrier_info.get("dbaName"),
                    operating_status=operating_status,
                    details=data,
                )
            elif response.status_code == 404:
                return FMCSAVerifyResponse(
                    mc_number=mc_number,
                    is_valid=False,
                    details={"error": "MC number not found in FMCSA database"},
                )
            else:
                # API error, but still return response
                return FMCSAVerifyResponse(
                    mc_number=mc_number,
                    is_valid=False,
                    details={
                        "error": f"FMCSA API returned status {response.status_code}",
                        "message": response.text[:200]
                        if hasattr(response, "text")
                        else "Unknown error",
                    },
                )

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="FMCSA API request timed out")
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502, detail=f"Error connecting to FMCSA API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error verifying MC number: {str(e)}"
        )
