from streamlit.testing.v1 import AppTest

app = "./src/frontend/app.py"

def test_has_no_text_input():
    at = AppTest.from_file(app).run()
    print(len(at.text_input))
    assert len(at.text_input) <= 0

def test_has_no_number_input():
    at = AppTest.from_file(app).run()
    print(len(at.number_input))
    assert len(at.number_input) <= 0

def test_has_no_text_area():
    at = AppTest.from_file(app).run()
    print(len(at.text_area))
    assert len(at.text_area) <= 0
