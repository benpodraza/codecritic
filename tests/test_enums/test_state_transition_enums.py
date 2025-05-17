import importlib

from app.enums.state_transition_enums import TransitionReason, TransitionTarget


def test_transition_reason_values():
    assert TransitionReason.FIRST_ROUND.value == "first_round"
    assert TransitionReason.SCORE_STAGNATION.value == "score_stagnation"
    assert TransitionReason.MEDIATOR_OVERRIDE.value == "mediator_override"
    assert TransitionReason.NORMAL_SEQUENCE.value == "normal_sequence"
    assert TransitionReason.CUSTOM_RULE.value == "custom_rule"


def test_transition_target_values():
    assert TransitionTarget.START.value == "START"
    assert TransitionTarget.GENERATOR.value == "GENERATE"
    assert TransitionTarget.DISCRIMINATOR.value == "DISCRIMINATE"
    assert TransitionTarget.MEDIATOR.value == "MEDIATE"
    assert TransitionTarget.PATCHOR.value == "PATCHOR"
    assert TransitionTarget.RECOMMENDER.value == "RECOMMENDER"
    assert TransitionTarget.END.value == "END"
