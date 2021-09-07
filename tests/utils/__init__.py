from alexandria.shell import print_color
from alexandria.data_structs.string import join_set_distance


def verify(prediction, measurement, error_margin=0.001, log=False, name='Error'):
    """
    Model verification:
    - Error must stay under 0.1% of the measurement.

    :param error_margin: [>= 0] Error margin in unit fractions (1 ~ 100%).

    :type prediction:    float
    :type measurement:   float
    :type error_margin:  float
    :type log:           bool
    """
    assert abs(prediction-measurement) < measurement*error_margin, \
        f'Error = {abs(prediction-measurement)/measurement*100:.2f}% of measurement.'

    if log:
        s = join_set_distance(name, '=', 10)
        print_color(s + f' {abs(prediction-measurement)/measurement*100:.2f}% of measurement.', 'yellow')
