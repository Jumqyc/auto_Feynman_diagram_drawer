from dtype import *

def contraction(operators:list[Operator],LSZ_reduction:bool = False) -> list[tuple[Diagram,int]]:
    """
    Perform Wick contraction on a list of quantum field operators.
    Args:
        operators (list[Operator]): A list of quantum field operators to be contracted.
        LSZ_reduction (bool): If True, treat external operators as external fields. Apply LSZ reduction by forbidding external operators contract. Default is False.
    Returns:
        diagrams (list[tuple[Diagram,int]]): A list of tuples, each containing a Diagram object representing a unique contraction and an integer representing its multiplicity.
    Raises:
        ValueError: If the number of operators is not even or if the number of creation and annihilation operators are not equal.
        ValueError: If the input is not a list of Operator objects.
    Example:
    >>> from contraction import Operator, contraction
    >>> operators = [Operator('a','f',0), Operator('b','f',0), Operator('c','f',0), Operator('d','f',0)]
    >>> diagrams = contraction(operators)
    >>> for diagram, multiplicity in diagrams:
            print(f"Diagram: {diagram}, Multiplicity: {multiplicity}")
        Diagram: Outer vertices: {'a', 'b', 'c', 'd'}
            Inner vertices: set()
            Propagators: [f(a---b), f(c---d)], Multiplicity: 1
        Diagram: Outer vertices: {'a', 'b', 'c', 'd'}
            Inner vertices: set()
            Propagators: [f(a---c), f(b---d)], Multiplicity: 1
        Diagram:Outer vertices: {'a', 'b', 'c', 'd'}
            Inner vertices: set()
            Propagators: [f(a---d), f(b---c)], Multiplicity: 1
        ####################
    >>> for diagram,multiplicity in contraction([Field('a','f',0,fermionic=True),
            Field('b','f',0,fermionic=True),
            Field('c','f',0,fermionic=True),
            Field('d','f',0,fermionic=True)]):
            print(f"Multiplicity: {multiplicity}", diagram)
        Multiplicity: 1      Outer vertices: set()
            Inner vertices: {'d', 'a', 'b', 'c'}
            Propagators: [f(a---b), f(c---d)]
        Multiplicity: -1      Outer vertices: set()
            Inner vertices: {'d', 'a', 'b', 'c'}
            Propagators: [f(a---c), f(b---d)]
        Multiplicity: 1      Outer vertices: set()
            Inner vertices: {'d', 'a', 'b', 'c'}
            Propagators: [f(a---d), f(b---c)]
    """
    if len(operators) % 2 != 0:
        raise ValueError("The number of operators must be even for contraction.")
    if not isinstance(operators, list) and not all(isinstance(op, Operator) for op in operators):
        raise ValueError('The type of the operator must be type field in the list')
    if not sum(op.charge for op in operators) == 0:
        raise ValueError("The number of creation and annihilation operators must be equal.")

    operators.sort()

    inner_vertices = tuple(set(op.pos for op in operators if not op.external))
    outer_vertices = tuple(set(op.pos for op in operators if op.external))

    all_possible_contraction = []

    def contract(to_be_contract:list[Operator],
                 contracted:list[Propagator] = [],
                 multiplicity:int = 1)->list[tuple[list[Propagator],int]]:
        if len(to_be_contract) == 2: # if there is only one pair left, contract them
            pair = to_be_contract[0] + to_be_contract[1]
            all_possible_contraction.append((contracted + [pair],multiplicity))
            return # return to the previous level of recursion
        multiplicity_in_this_layer = 1 # initialize the multiplicity for this layer of recursion
        for i in range(1,len(to_be_contract)): # contract the first operator with the ith operator
            if (i < len(to_be_contract) - 1) and (to_be_contract[i] == to_be_contract[i+1]): # if the two operators are the same, we skip the next one to avoid double counting
                multiplicity_in_this_layer += 1
                continue
            elif LSZ_reduction and to_be_contract[0].external and to_be_contract[i].external: # if LSZ reduction is applied, we will not contract external operators
                continue
            try:
                pair = to_be_contract[0] + to_be_contract[i]
            except TypeError:
                continue
            if to_be_contract[0].fermionic and (i % 2 == 0): # if the operator is fermionic, we need to consider the sign
                multiplicity_in_this_layer *= -1
            contract(
                to_be_contract[1:i] + to_be_contract[i+1:],  # remove the two contracted operators
                contracted + [pair],                         # add the contracted pair to the list
                multiplicity * multiplicity_in_this_layer    # update the multiplicity
            )
            multiplicity_in_this_layer = 1  # reset the multiplicity for the next iteration

        return all_possible_contraction     # the multiplicity is 1 for now, 
                                            # we haven't implemented symmetry for internal vertices yet
    return_list = []
    for propagators , multiplicity in contract(operators):
        if len(propagators) != len(operators) // 2:
            continue
        return_list.append(
            (Diagram(outer_vertices,inner_vertices,tuple(propagators)),
             multiplicity))
    if return_list == []:
        raise ValueError("No valid contraction found. Please check the input operators.")
    return return_list

if __name__ == "__main__":
    operators = [Fermion('1','e',1,external=True),
                Fermion('2','e',1,external=True),
                Fermion('3','e',-1,external=True),
                Fermion('4','e',-1,external=True),
                Uncharged_Boson('x','a'),
                Uncharged_Boson('y','a'),
                Fermion('x','e',1),
                Fermion('y','e',1),
                Fermion('x','e',-1),
                Fermion('y','e',-1)]
    # ee -> ee scattering with internal photon exchange
    for diagram,multiplicity in contraction(operators,LSZ_reduction=True):
        print(f"Multiplicity: {multiplicity}", diagram)