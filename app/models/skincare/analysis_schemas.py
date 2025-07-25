from typing import Optional, Dict, List
from pydantic import BaseModel


class AcneBreakouts(BaseModel):
    severity: str
    count_estimate: int
    location: List[str]


class BlackheadsWhiteheads(BaseModel):
    presence: bool
    location: List[str]


class OilinessShine(BaseModel):
    level: str
    location: List[str]


class DrynessFlaking(BaseModel):
    presence: bool
    location: List[str]


class DarkSpotsScars(BaseModel):
    presence: bool
    description: str


class PoresSize(BaseModel):
    level: str
    location: List[str]


class FineLinesWrinkles(BaseModel):
    presence: bool
    areas: List[str]


class SkinAnalysis(BaseModel):
    redness_irritation: Optional[str]
    acne_breakouts: Optional[AcneBreakouts]
    blackheads_whiteheads: Optional[BlackheadsWhiteheads]
    oiliness_shine: Optional[OilinessShine]
    dryness_flaking: Optional[DrynessFlaking]
    uneven_skin_tone: Optional[str]
    dark_spots_scars: Optional[DarkSpotsScars]
    pores_size: Optional[PoresSize]
    hormonal_acne_signs: Optional[str]
    stress_related_flareups: Optional[str]
    dehydrated_skin_signs: Optional[str]
    fine_lines_wrinkles: Optional[FineLinesWrinkles]
    skin_elasticity: Optional[str]


class RoutineStep(BaseModel):
    name: str
    tag: str
    description: str
    instructions: List[str]
    duration: int
    waiting_time: int
    days: Dict[str, bool]
    time: List[str]


class SkincareRoutineResponse(BaseModel):
    product_type: str
    routine: List[RoutineStep]


class FaceAnalysisResponse(BaseModel):
    message: str
    ai_output: SkinAnalysis
