from data import survey as data

def get_survey(user_id: int):
    return data.get_survey(user_id)


def save_survey(user_id: int, survey_result: dict):
    return data.save_survey(user_id, survey_result)