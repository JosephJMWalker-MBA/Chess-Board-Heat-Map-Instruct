import pytest
import chess
import chess.engine
import os
import hashlib
from unittest.mock import patch, MagicMock

import src.chessheat.cp_instrument as cpi
from src.chessheat.experiment import ExperimentSpec
from src.chessheat.semantics import SufficientPosition

class FakeOption(chess.engine.Option):
    def __init__(self, name, type, default, min, max, var, managed):
        super().__init__(name, type, default, min, max, var)
        self._managed = managed
    def is_managed(self):
        return self._managed

def create_fake_options():
    opts = {}
    for k in cpi.STATIC_UCI_CONFIG:
        opts[k] = FakeOption(k, "string", "", None, None, [], False)
    opts["Threads"].type = "spin"
    opts["Hash"].type = "spin"
    opts["Skill Level"].type = "spin"
    opts["UCI_LimitStrength"].type = "check"
    opts["UCI_ShowWDL"].type = "check"
    opts["SyzygyProbeLimit"].type = "spin"
    
    for k in cpi.MANAGED_OPTIONS:
        opts[k] = FakeOption(k, "check", False, None, None, [], True)
        
    opts["EvalFile"] = FakeOption("EvalFile", "string", "default.nnue", None, None, [], False)
    opts["EvalFileSmall"] = FakeOption("EvalFileSmall", "string", "default_small.nnue", None, None, [], False)
    return opts

def test_source_role():
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    assert session.nodes == cpi.SOURCE_NODES
    assert session.instrument_id == cpi.SOURCE_INSTRUMENT_ID

