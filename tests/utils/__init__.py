# SPDX-FileCopyrightText: © 2024 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: MPL-2.0


from huracan.utils import join_set_distance


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
        print(s + f' {abs(prediction-measurement)/measurement*100:.2f}% of measurement.')
