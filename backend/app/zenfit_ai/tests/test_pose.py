import pytest
from app.zenfit_ai.pose.angles import joint_angle
from app.zenfit_ai.pose.rep_counter import RepCounter
from app.zenfit_ai.pose.analyzer import PoseAnalyzer

def test_joint_angle(): assert round(joint_angle((1,0),(0,0),(0,1)))==90
def test_rep_transition():
    counter=RepCounter(100,160); counter.update(90); assert counter.update(170)==1
def test_unsupported():
    with pytest.raises(ValueError): PoseAnalyzer().analyze("curl",[])
def test_missing_landmarks():
    with pytest.raises(ValueError): PoseAnalyzer().analyze("squat",[])
def test_low_visibility_does_not_count_rep():
    result=PoseAnalyzer().analyze("squat",[{"name":"hip","x":0,"y":0,"visibility":.3},{"name":"knee","x":0,"y":1},{"name":"ankle","x":1,"y":1}])
    assert result["body_visible"] is False and result["reps"]==0
