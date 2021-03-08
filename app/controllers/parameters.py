class Parameter:
    def __init__(self, input_type, value, **kwargs):
        self.input_type = input_type # text, password, email, number, url, tel, search, date, datetime, datetime-local, month, week, time, range, color
        self.value = value
        self.meta = kwargs

class ParameterCollection:
    params = {
        'resolution': Parameter('range', 32, minVal=0, maxVal=100),
        'expected_people': Parameter('range', 2, minVal=1, maxVal=10),
        'minConf': Parameter('range', .9, minVal=0, maxVal=1, step=.1),

        'n_components': Parameter('range', 100, minVal=50, maxVal=1000, step=50)
    }

    @staticmethod
    def get(*keys):
        return {key: ParameterCollection.params[key] for key in keys}