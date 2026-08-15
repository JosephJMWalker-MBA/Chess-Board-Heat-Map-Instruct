import hashlib
import json
from enum import Enum
from typing import Dict, Any, List
from pydantic import BaseModel
from .semantics import SufficientPosition

class SuiteKind(str, Enum):
    NATURAL_REPRESENTATIVE = "natural_representative"
    MECHANISM_STRESS = "mechanism_stress"

class SuiteManifest(BaseModel):
    """
    Groups experiment fixtures.
    """
    suite_id: str
    kind: SuiteKind
    fixtures: List[str]

class ExperimentSpec(BaseModel):
    """
    Defines the rigid inputs and conditions of a single experiment.
    Serves as the deterministic identity of an experiment.
    """
    semantic_signature_version: str
    suite_identity: str
    fixture_identity: str
    sufficient_position: SufficientPosition
    candidate_policy: Dict[str, Any]
    producer_identity: str
    instrument_config: Dict[str, Any]
    budget_config: Dict[str, Any]
    line_source: str
    hypothesis_identifier: str

    def spec_digest(self) -> str:
        """Deterministic SHA-256 hash of the specification."""
        payload_str = json.dumps(self.model_dump(), sort_keys=True)
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

class ExperimentResult(BaseModel):
    """
    The immutable result of an experiment.
    Cannot mutate its source specification.
    """
    model_config = {"frozen": True}

    spec_digest: str
    artifact_digest: str
    data: Dict[str, Any]

class ComparisonResult(BaseModel):
    """
    Connects two ExperimentResult digests for a specified hypothesis.
    """
    hypothesis_identifier: str
    result_digest_a: str
    result_digest_b: str
    outcome: Dict[str, Any]
