import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.response_model import ApiResponse
from app.models.vehicle_model import VinDecodeSummary, VinDecodeFullResult

router = APIRouter(prefix="/api/v1/vehicles", tags=["Vehicles"])

_bearer = HTTPBearer(auto_error=False)

NHTSA_BASE = "https://vpic.nhtsa.dot.gov/api/vehicles"


# ── helpers ───────────────────────────────────────────────────────────────────

def _s(result: dict, key: str) -> str:
    """Safe string getter — returns empty string instead of None."""
    return (result.get(key) or "").strip()


async def _fetch_nhtsa(vin: str) -> dict:
    """Call NHTSA vpic API and return the first result dict."""
    url = f"{NHTSA_BASE}/decodevinvalues/{vin.upper()}?format=json"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="NHTSA API timed out")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"NHTSA API returned {exc.response.status_code}",
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"NHTSA API error: {str(exc)}")

    body = resp.json()
    results = body.get("Results", [])
    if not results:
        raise HTTPException(status_code=404, detail=f"No data found for VIN {vin}")
    return results[0]


# ── endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/decode/{vin}",
    response_model=ApiResponse[VinDecodeFullResult],
    summary="Decode VIN — full result",
    description=(
        "Decode a 17-character VIN using the **NHTSA vPIC API** and return "
        "all available fields plus the raw NHTSA result payload."
    ),
)
async def decode_vin_full(
    vin: str = Path(
        ...,
        min_length=17,
        max_length=17,
        openapi_examples={"default": {"value": "JTDKB20U793534173"}},
        description="17-character Vehicle Identification Number",
    ),
    _token: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """Decode a VIN and return all available fields plus the raw NHTSA result payload."""
    r = await _fetch_nhtsa(vin)
    error_code = _s(r, "ErrorCode")

    full = VinDecodeFullResult(
        vin=_s(r, "VIN"),
        make=_s(r, "Make"),
        make_id=_s(r, "MakeID"),
        model=_s(r, "Model"),
        model_id=_s(r, "ModelID"),
        model_year=_s(r, "ModelYear"),
        vehicle_type=_s(r, "VehicleType"),
        body_class=_s(r, "BodyClass"),
        drive_type=_s(r, "DriveType"),
        doors=_s(r, "Doors"),
        fuel_type_primary=_s(r, "FuelTypePrimary"),
        fuel_type_secondary=_s(r, "FuelTypeSecondary"),
        electrification_level=_s(r, "ElectrificationLevel"),
        engine_cylinders=_s(r, "EngineCylinders"),
        engine_configuration=_s(r, "EngineConfiguration"),
        engine_displacement_cc=_s(r, "DisplacementCC"),
        engine_displacement_l=_s(r, "DisplacementL"),
        engine_displacement_ci=_s(r, "DisplacementCI"),
        engine_hp=_s(r, "EngineHP"),
        engine_model=_s(r, "EngineModel"),
        manufacturer=_s(r, "Manufacturer"),
        manufacturer_id=_s(r, "ManufacturerId"),
        plant_city=_s(r, "PlantCity"),
        plant_company_name=_s(r, "PlantCompanyName"),
        plant_country=_s(r, "PlantCountry"),
        plant_state=_s(r, "PlantState"),
        series=_s(r, "Series"),
        gvwr=_s(r, "GVWR"),
        gvwr_to=_s(r, "GVWR_to"),
        seat_belts_all=_s(r, "SeatBeltsAll"),
        tpms=_s(r, "TPMS"),
        air_bag_loc_front=_s(r, "AirBagLocFront"),
        air_bag_loc_side=_s(r, "AirBagLocSide"),
        air_bag_loc_curtain=_s(r, "AirBagLocCurtain"),
        vehicle_descriptor=_s(r, "VehicleDescriptor"),
        error_code=error_code,
        error_text=_s(r, "ErrorText"),
        raw=r,
    )

    msg = (
        "VIN decoded successfully"
        if error_code == "0"
        else f"VIN decoded with warnings (error code {error_code})"
    )
    return ApiResponse.ok(data=full, message=msg)


@router.get(
    "/decode/{vin}/summary",
    response_model=ApiResponse[VinDecodeSummary],
    summary="Decode VIN — summary (key fields only)",
    description=(
        "Decode a VIN and return only the **essential vehicle identity fields** "
        "(make, model, year, engine, fuel type, etc.)."
    ),
)
async def decode_vin_summary(
    vin: str = Path(
        ...,
        min_length=17,
        max_length=17,
        openapi_examples={"default": {"value": "JTDKB20U793534173"}},
        description="17-character Vehicle Identification Number",
    ),
    _token: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """Decode a VIN and return only the essential vehicle identity fields."""
    r = await _fetch_nhtsa(vin)
    error_code = _s(r, "ErrorCode")

    summary = VinDecodeSummary(
        vin=_s(r, "VIN"),
        make=_s(r, "Make"),
        model=_s(r, "Model"),
        model_year=_s(r, "ModelYear"),
        vehicle_type=_s(r, "VehicleType"),
        body_class=_s(r, "BodyClass"),
        drive_type=_s(r, "DriveType"),
        doors=_s(r, "Doors"),
        fuel_type_primary=_s(r, "FuelTypePrimary"),
        fuel_type_secondary=_s(r, "FuelTypeSecondary"),
        electrification_level=_s(r, "ElectrificationLevel"),
        engine_cylinders=_s(r, "EngineCylinders"),
        engine_displacement_l=_s(r, "DisplacementL"),
        engine_hp=_s(r, "EngineHP"),
        engine_model=_s(r, "EngineModel"),
        manufacturer=_s(r, "Manufacturer"),
        plant_country=_s(r, "PlantCountry"),
        plant_city=_s(r, "PlantCity"),
        series=_s(r, "Series"),
        gvwr=_s(r, "GVWR"),
        error_code=error_code,
        error_text=_s(r, "ErrorText"),
    )

    msg = (
        "VIN decoded successfully"
        if error_code == "0"
        else f"VIN decoded with warnings (error code {error_code})"
    )
    return ApiResponse.ok(data=summary, message=msg)


@router.get(
    "/makes",
    response_model=ApiResponse[list],
    summary="Get all vehicle makes",
    description="Fetch all vehicle makes from the NHTSA API.",
)
async def get_all_makes(
    _token: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """Return every vehicle make known to NHTSA."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{NHTSA_BASE}/getallmakes?format=json")
            resp.raise_for_status()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"NHTSA API error: {str(exc)}")

    body = resp.json()
    results = body.get("Results", [])
    return ApiResponse.ok(
        data=results,
        message=f"Retrieved {len(results)} vehicle makes",
    )


@router.get(
    "/makes/{make}/models",
    response_model=ApiResponse[list],
    summary="Get models for a make",
    description="Fetch all models for a given vehicle make from the NHTSA API.",
)
async def get_models_for_make(
    make: str = Path(
        ...,
        openapi_examples={"default": {"value": "toyota"}},
        description="Vehicle make name (e.g. toyota, ford, honda)",
    ),
    _token: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """Return all models for the specified vehicle make."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{NHTSA_BASE}/getmodelsformake/{make}?format=json"
            )
            resp.raise_for_status()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"NHTSA API error: {str(exc)}")

    body = resp.json()
    results = body.get("Results", [])
    if not results:
        raise HTTPException(
            status_code=404, detail=f"No models found for make '{make}'"
        )
    return ApiResponse.ok(
        data=results,
        message=f"Retrieved {len(results)} models for make '{make.upper()}'",
    )
