import sys
import inspect


def setattr_namespace(o, namespace):
    """
    Set all variables declared in a namespace as as attributes
    of a class instance.
    ---

    1. Obtain list of module names
    2. Get namespace variables
       - Discard all variables with names starting and ending with '_'
    3. Create a dictionary of namespace variable names and values
    4. Set namespace variables as attributes of the input object
       - Given class instance _o_ will not set as attribute of itself
       - The parent class of _o_ will not be set as an attribute of _o_
         if present in the provided namespace.

    :param o: Instance of any given class.
    :param namespace: A given namespace.
                      - locals()
                      - globals()

    :type o: object
    :type namespace: dict
    """
    # List of module names
    _mods_ = list(set(sys.modules) & set(namespace))
    # List of function arguments
    _args_ = setattr_namespace.__code__.co_varnames
    # Get namespace variables:
    #    List of local variables which are not special variables nor module names
    keys = [key for key in namespace.keys() if (key[0] != '_' and key[-1] != '_') and key not in _mods_]
    # Dictionary of namespace variable names and values
    vars = {key: namespace[key] for key in keys}
    for key, value in vars.items():
        if not type(value) == type(o)\
                and not isinstance(o, value if inspect.isclass(value) else type(value)):  # Avoid _o_, parent of _o_
            # Set namespace variables as attributes of the input object
            setattr(o, key, value)
