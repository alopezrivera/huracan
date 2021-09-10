## Welcome to the Huracan API documentation!

Huracan is an open source, 0-dimensional, object-oriented airbreathing engine 
modelling package for preliminary analysis and design of airbreathing engines, 
divulgation and educational purposes.

## Engine modelling
In the diagram below can be seen how Huracan models an engine. Fundamentally:

* Work is distributed through the shafts
* Each stream posesses a gas instance which undergoes a series of processes.

## Important assumptions
* Ideal gas model
* Adiabatic compression and expansion
* Isobaric heat exchanges (albeit a pressure ratio can be provided in these cases)

## Key ideas
* Compartmentalization of the gas model, thermodynamic process methods and component classes
* Gas splitting and merging operations are conducted at runtime
* Stream functions overtaken by system functions at runtime when a system is created

## Engine modelling diagram
---

.. include:: ../docs/diagrams/turbofan_flow_diagram.svg