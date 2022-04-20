import cv2


def test_form_answer(form):
    img = cv2.cvtColor(form.img, cv2.COLOR_GRAY2BGR)
    answers = []
    for question in form.questions:
        for ans in question.answers:
            if ans.is_filled(form.img):
                answers.append(ans)
                color = (0, 0, 255)
                cv2.putText(
                    img,
                    str(question.question_id) + ans.value,
                    (ans.x, ans.y),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.4,
                    color,
                )
            else:
                color = (0, 255, 0)

            ans.mark_answer(img, color=color, circle_thickness=2)
    cv2.imwrite("test.jpeg", img)

# TODO generate new form template - simpler version of OEE? - run all tests on new template
# TODO use gimp/googledocs? - future googledocs API integration to create new templates?
