from pydantic import BaseModel
from typing import Optional


class VinDecodeSummary(BaseModel):
    """Key fields returned from the NHTSA VIN decode — essential vehicle identity."""
    vin: str
    make: str
    model: str
    model_year: str
    vehicle_type: str
    body_class: str
    drive_type: str
    doors: str
    fuel_type_primary: str
    fuel_type_secondary: str
    electrification_level: str
    engine_cylinders: str
    engine_displacement_l: str
    engine_hp: str
    engine_model: str
    manufacturer: str
    plant_country: str
    plant_city: str
    series: str
    gvwr: str
    error_code: str
    error_text: str


class VinDecodeFullResult(BaseModel):
    """All fields returned by the NHTSA API for a VIN decode."""
    vin: str
    make: str
    make_id: str
    model: str
    model_id: str
    model_year: str
    vehicle_type: str
    body_class: str
    drive_type: str
    doors: str
    fuel_type_primary: str
    fuel_type_secondary: str
    electrification_level: str
    engine_cylinders: str
    engine_configuration: str
    engine_displacement_cc: str
    engine_displacement_l: str
    engine_displacement_ci: str
    engine_hp: str
    engine_model: str
    manufacturer: str
    manufacturer_id: str
    plant_city: str
    plant_company_name: str
    plant_country: str
    plant_state: str
    series: str
    gvwr: str
    gvwr_to: str
    seat_belts_all: str
    tpms: str
    air_bag_loc_front: str
    air_bag_loc_side: str
    air_bag_loc_curtain: str
    vehicle_descriptor: str
    error_code: str
    error_text: str
    # Raw NHTSA result for full passthrough
    raw: dict
