import json
from pathlib import Path

import pytest

from app.ai.artifacts import REQUIRED_FILES, package_artifact, verify_artifact
from app.ai.meal_scan.food_detector import UnavailableFoodDetector
from app.ai.meal_scan.open_set import Candidate, OpenSetDecision, OpenSetDecisionEngine, OpenSetInput, OpenSetThresholds, probability_entropy
from training.analyze_open_set_thresholds import recommend
from training.open_set_evaluation import evaluate_rows, threshold_sweep
from training.promote_indian_food import evaluate_gates
from app.ai.meal_scan.artifact_loader import artifact_capability, materialize_verified_artifact
from app.ai.service import ZenFitAIService
from app.ai.meal_scan.classifier import calibrated_softmax


def thresholds(**overrides):
    values=dict(model_version="test",supported_food_min_confidence=.6,unknown_below_confidence=.25,min_top1_top2_margin=.1,max_entropy=1.0,food_detector_threshold=.5)
    values.update(overrides);return OpenSetThresholds(**values)


@pytest.mark.parametrize(("evidence","expected"),[
    (OpenSetInput((Candidate("dosa",.9),Candidate("idli",.05)),.4,.9),OpenSetDecision.SUPPORTED_FOOD),
    (OpenSetInput((Candidate("dosa",.2),Candidate("idli",.18)),1.5,.9),OpenSetDecision.UNKNOWN_FOOD),
    (OpenSetInput((Candidate("dosa",.9),Candidate("idli",.05)),.4,.2),OpenSetDecision.NON_FOOD),
    (OpenSetInput((Candidate("dosa",.59),Candidate("idli",.55)),.5,.9),OpenSetDecision.LOW_CONFIDENCE),
    (OpenSetInput((),model_available=False),OpenSetDecision.MODEL_UNAVAILABLE),
])
def test_open_set_decisions(evidence,expected):
    assert OpenSetDecisionEngine(thresholds()).decide(evidence).decision is expected


def test_entropy_and_missing_detector_behavior():
    assert probability_entropy([.9,.05,.05]) < probability_entropy([.34,.33,.33])
    result=OpenSetDecisionEngine(thresholds()).decide(OpenSetInput((Candidate("dosa",.9),Candidate("idli",.05)),.4,None))
    assert result.decision is OpenSetDecision.SUPPORTED_FOOD
    assert not UnavailableFoodDetector().predict(object()).available


def test_threshold_validation():
    with pytest.raises(ValueError):OpenSetThresholds(model_version="x",unknown_below_confidence=.8,supported_food_min_confidence=.6)


def _fake_candidate(root:Path):
    root.mkdir()
    for name in REQUIRED_FILES:
        (root/name).write_bytes(b"fake-weight-bytes" if name=="model.pt" else b"{}")


def test_artifact_package_checksum_and_environment(tmp_path):
    candidate=tmp_path/"1.2.0";_fake_candidate(candidate);package=tmp_path/"package"
    package_artifact(candidate,package,environment="development")
    assert verify_artifact(package,required_environment="development")["model_version"]=="1.2.0"
    (package/"model.pt").write_bytes(b"corrupt")
    with pytest.raises(ValueError,match="checksum"):verify_artifact(package)
    with pytest.raises(ValueError):verify_artifact(tmp_path/"missing")
    with pytest.raises(ValueError,match="promotion-gate"):package_artifact(candidate,tmp_path/"production",environment="production")


def test_local_developer_beta_artifact_selection_and_corruption(tmp_path):
    candidate=tmp_path/"1.2.0-colab-candidate";_fake_candidate(candidate);storage=tmp_path/"storage";package=storage/"meal-classifier"/"1.2.0-colab-candidate"
    package_artifact(candidate,package,environment="developer-beta")
    settings=type("Settings",(),{"meal_classifier_enabled":True,"meal_classifier_version":"1.2.0-colab-candidate","meal_classifier_environment":"developer-beta","meal_classifier_artifact_prefix":"meal-classifier","artifact_storage_backend":"local","artifact_local_dir":storage,"model_cache_dir":tmp_path/"cache"})()
    root,manifest=materialize_verified_artifact(settings)
    assert root==package and manifest["model_version"]=="1.2.0-colab-candidate"
    assert artifact_capability(settings)["available"] is True
    (package/"model.pt").write_bytes(b"corrupt")
    assert artifact_capability(settings)["available"] is False


def test_missing_developer_beta_artifact_is_unavailable(tmp_path):
    settings=type("Settings",(),{"meal_classifier_enabled":True,"meal_classifier_version":"missing","meal_classifier_environment":"developer-beta","meal_classifier_artifact_prefix":"meal-classifier","artifact_storage_backend":"local","artifact_local_dir":tmp_path,"model_cache_dir":tmp_path/"cache"})()
    capability=artifact_capability(settings)
    assert capability["enabled"] is True and capability["available"] is False


def test_health_exposes_safe_developer_beta_capability(monkeypatch):
    raw={"heavy_models_enabled":False,"bge_embeddings":False,"bge_reranker":False,"adherence_model":False,"readiness_model":False,"recommendation_model":False,"foodsam":False,"foodseg103":False,"indian_food_classifier":True,"usda_configured":False,"mediapipe":False}
    monkeypatch.setattr("app.ai.service.registry.status",lambda:raw)
    monkeypatch.setattr("app.ai.service.qdrant_health",lambda:False)
    monkeypatch.setattr("app.ai.service.artifact_capability",lambda settings:{"enabled":True,"available":True,"model_version":"1.2.0-colab-candidate","environment":"developer-beta","reason":None})
    result=ZenFitAIService().health()["meal_scan"]
    assert result["overall"]=="ready"
    assert result["meal_classifier"]=={"enabled":True,"available":True,"model_version":"1.2.0-colab-candidate","environment":"developer-beta","reason":None}


def test_calibrated_softmax_applies_temperature_before_softmax():
    class FakeLogits:
        temperature=None;dimension=None
        def __truediv__(self,value):self.temperature=value;return self
        def softmax(self,dim):self.dimension=dim;return self
    logits=FakeLogits()
    assert calibrated_softmax(logits,1.0556710958480835) is logits
    assert logits.temperature==1.0556710958480835 and logits.dimension==1
    with pytest.raises(ValueError):calibrated_softmax(logits,0)


def test_open_set_metrics_and_threshold_analysis_use_stored_evidence_only():
    rows=[
        {"truth":"supported_food","expected_label":"dosa","top_candidates":[{"label":"dosa","confidence":.9},{"label":"idli","confidence":.05}],"entropy":.3,"food_probability":.9},
        {"truth":"unknown_food","top_candidates":[{"label":"dosa","confidence":.2},{"label":"idli","confidence":.18}],"entropy":1.5,"food_probability":.9},
        {"truth":"non_food","top_candidates":[{"label":"dosa","confidence":.8},{"label":"idli","confidence":.1}],"entropy":.5,"food_probability":.1},
    ]
    metrics=evaluate_rows(rows,thresholds());assert metrics["overall_open_set_accuracy"]==1
    result=recommend(threshold_sweep(rows,"test",confidence_values=(.6,),margin_values=(.1,),entropy_values=(1.0,)))
    assert result["status"]=="candidate"


def test_promotion_blocks_insufficient_open_set_evidence(tmp_path):
    candidate=tmp_path/"1.1.0";candidate.mkdir()
    for name in ("model.pt","classes.json","config.json","confusion_matrix.json","reproducibility.json","model_card.md","open_set_thresholds.json"):(candidate/name).write_text("{}")
    (candidate/"metrics.json").write_text(json.dumps({"macro_f1":.9,"latency_gate":True,"regression_gate":True}))
    (candidate/"calibration.json").write_text(json.dumps({"ece":.03}))
    (candidate/"dataset_manifest.json").write_text(json.dumps({"commercial_use_allowed":True,"license_review_status":"approved"}))
    (candidate/"release_evidence.json").write_text(json.dumps({"validation_samples":596,"unknown_food":{"sample_count":25,"class_count":5,"rejection_rate":.9},"non_food":{"sample_count":4,"category_count":4,"rejection_rate":.9}}))
    gates=evaluate_gates(candidate)
    assert gates["unknown_food_gate"]["status"]=="PASS"
    assert gates["non_food_gate"]["status"]=="PASS"
    assert gates["open_set_evidence_size_gate"]["status"]=="BLOCKED"
