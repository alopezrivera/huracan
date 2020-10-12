from resources.fundamentals_propulsion import *

m = mach(710/3.6, 1.4, 287, 288.15)

p, t = ambient(101325, 288.15, m, 1.4)

p, t = inlet(p, t, m, 1.4, 0.96, 1)

p, t = pi_compression(3.26, 0.89, 1.4, p, t)

p, t = pi_compression(2.3, 0.88, 1.4, p, t)

p, t = pi_expansion(0.99, 0.98, 1.33, 916003.4, 582.58)

p, t = cc_w_given(916003.4, 582.58, 0.99, 5557069.68, 3452306.57, 20, 1150, 0.98, '4')

fuel_mass_flow(582.586126, 974.2920, 20, 1150, 0.98, 43e6)

p, t = turbine(5557069.68, 20+0.277935, 1150, 1.33, 0.91, t, p)

p, t = turbine(3452306.57, 20+0.277935, 1150, 1.33, 0.92, t, p)

is_nozzle_choked(101325/129377.086, 0.98, 1.33)

non_choked_nozzle(129377.086, )

flow_thrust(20+0.277935, exit_velocity_unchoked(1.33, 287, ))