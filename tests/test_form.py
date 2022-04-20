def test_answer_check_fill(form):
    ans = form.questions[0].answers[20]
    assert ans.is_filled(form.img) ==True
    
def test_answer_check_fill_perc(form):
    ans = form.questions[1].answers[268]
    fill_perc = ans.calc_filled_perc(form.img)
    assert round(fill_perc,2) == 0.81

