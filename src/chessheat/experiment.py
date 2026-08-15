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
    fixtures: Dict[str, str]  # fixture_identity -> fixture_content_digest

    def suite_digest(self) -> str:
        """Deterministic SHA-256 hash of the suite manifest."""
        payload_str = json.dumps(self.model_dump(), sort_keys=True)
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

class ExperimentSpec(BaseModel):
    """
    Defines the rigid inputs and conditions of a single experiment.
    Serves as the deterministic identity of an experiment.
    """
    semantic_signature_version: str
    semantic_signature_digest: str
    suite_identity: str
    suite_digest: str
    fixture_identity: str
    fixture_digest: str
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
    Cannot mutate its source specification or payload.
    """
    model_config = {"frozen": True}

    spec_digest: str
    artifact_digest: str
    data_payload: str

    @property
    def data(self) -> Dict[str, Any]:
        """Returns a throwaway parsed dict of the deeply immutable data payload."""
        return json.loads(self.data_payload)

    @classmethod
    def create(cls, spec_digest: str, data: Dict[str, Any]) -> "ExperimentResult":
        """Mechanically derives artifact_digest from canonical payload and spec digest."""
        payload = json.dumps(data, sort_keys=True)
        combined = f"{spec_digest}:{payload}"
        artifact_digest = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        return cls(spec_digest=spec_digest, artifact_digest=artifact_digest, data_payload=payload)

class ComparisonResult(BaseModel):
    """
    Connects two ExperimentResult digests for a specified hypothesis.
    """
    model_config = {"frozen": True}

    hypothesis_identifier: str
    result_digest_a: str
    result_digest_b: str
    outcome_payload: str
    
    @property
    def outcome(self) -> Dict[str, Any]:
        return json.loads(self.outcome_payload)
