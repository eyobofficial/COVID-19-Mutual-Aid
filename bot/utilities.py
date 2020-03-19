from survey.models import Question, Answer


def is_form_completed(user):
    """
    Checks if the user completed filling the form.

    Returns:
        True (bool): if user completed filling the form.
        False (bool): if the user has not completed filling the form.
    """
    is_completed = True
    questions = Question.objects.all()
    for question in questions:
        try:
            answer = Answer.objects.get(user=user, question=question)
        except Answer.DoesNotExist:
            return False

    return is_completed
