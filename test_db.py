from database import init_db, save_assessment, get_assessments

def test_db_operations():
    init_db()
    
    save_assessment(
        1,
        "Car",
        20,
        250,
        "Non-Vegetarian",
        2,
        3200,
        65
    )
    
    assessments = get_assessments(1)
    assert len(assessments) >= 1