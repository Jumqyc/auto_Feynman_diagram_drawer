from dataclasses import dataclass,field
from typing import ClassVar, List, Tuple


@dataclass(order=True, frozen=True, slots=True)
class Operator:
    '''
    A class representing a quantum field operator.
    Attributes:
        pos (str): The position or label of the operator (e.g., 'x', 'y', 'p1', 'k2').
        type (str): The type of the particle (e.g., 'e' for electron, 'a' for photon).
        charge (int): The charge of the operator (1 for creation, -1 for annihilation, 0 for neutral).
        fermionic (bool): True if the operator is fermionic, False if bosonic. We will not consider some exotic statistics here.
        external (bool): True if the operator is external, False if internal.
    '''
    pos: str
    type: str
    charge: int
    fermionic: bool = False
    external: bool = False

    VALID_CHARGES: ClassVar = {1, -1, 0}

    def __post_init__(self):
        if self.charge not in self.VALID_CHARGES:
            raise ValueError("charge must be 1, -1, or 0")
    
    def __add__(self, other: 'Operator') -> 'Propagator':
        if not self.__can_contract_with__(other):
            raise TypeError("Cannot contract these operators.")
        elif self.charge == 1 and other.charge == -1:
            return Propagator(self.type, self.pos, other.pos, True)
        elif self.charge == -1 and other.charge == 1:
            return Propagator(self.type, other.pos, self.pos, True)
        else:
            return Propagator(self.type, self.pos, other.pos, False)

    def __can_contract_with__(self, other: 'Operator') -> bool:
        return (self.type == other.type and
                self.fermionic == other.fermionic and
                self.charge + other.charge == 0)

@dataclass(order=True, frozen=True, slots=True)
class Propagator:
    '''
    A class representing a propagator in a Feynman diagram.
    Attributes:
        type (str): The type of the particle (e.g., 'e' for electron, 'a' for photon).
        initial (str): The initial vertex of the propagator.
        final (str): The final vertex of the propagator.
        arrow (bool): True if the propagator has an arrow (fermionic), False otherwise (bosonic).
    '''
    type: str
    initial: str
    final: str
    arrow: bool
    def __repr__(self) -> str:
        return f"{self.type}: {self.initial}{"->-" if self.arrow else "---"}{self.final}"
    def __eq__(self:'Propagator', other: 'Propagator') -> bool:
        if self.type != other.type or self.arrow != other.arrow:
            return False
        elif self.arrow:
            return (self.initial,self.final) == (other.initial,other.final) # arrow direction matters
        else:
            return ((self.initial,self.final) == (other.initial,other.final)) or ((self.initial,self.final) == (other.final,other.initial)) # direction does not matter

@dataclass(frozen=True)
class Diagram:
    '''
    A class representing a Feynman diagram.
    Attributes:
        outer_vertices (Tuple[str, ...]): A tuple of outer vertex labels.
        inner_vertices (Tuple[str, ...]): A tuple of inner vertex labels.
        propagators (Tuple[Propagator, ...]): A tuple of Propagator objects representing the connections between vertices.
    Properties:
        list_of_particles (List[Tuple[str, bool]]): A list of unique particle types and their statistics (charged or uncharged) present in the diagram.
    Methods:
        is_equivalent(other: 'Diagram') -> bool: Check if two diagrams are equivalent (isomorphic).
    '''
    outer_vertices: Tuple[str, ...] = field(compare=True)
    inner_vertices: Tuple[str, ...] = field(compare=True)  
    propagators: Tuple[Propagator, ...] = field(compare=True)
    
    def __post_init__(self):
        object.__setattr__(self, 'propagators', tuple(sorted(self.propagators)))
    
    @property
    def list_of_particles(self) -> List[Tuple[str, bool]]:
        return list(set((p.type, p.arrow) for p in self.propagators))
    
    def __repr__(self) -> str:
        return f"""Outer vertices: {self.outer_vertices}
        Inner vertices: {self.inner_vertices}
        Propagators: {self.propagators}"""
    def is_equivalent(self, other: 'Diagram') -> bool:
        pass
    


def contraction(operators:list[Operator],LSZ_reduction:bool = False) -> list[tuple[Diagram,int]]:
    """
    Perform Wick contraction on a list of quantum field operators.
    Args:
        operators (list[Field]): A list of quantum field operators to be contracted.
        LSZ_reduction (bool): If True, treat external operators as external fields. Apply LSZ reduction by forbidding external operators contract. Default is False.
    Returns:
        diagrams (list[tuple[Diagram,int]]): A list of tuples, each containing a Diagram object representing a unique contraction and an integer representing its multiplicity.
    Raises:
        ValueError: If the number of operators is not even or if the number of creation and annihilation operators are not equal.
        ValueError: If the input is not a list of Field objects.
    Example:
    >>> from contraction import Field, contraction
    >>> operators = [Field('a','f',0), Field('b','f',0), Field('c','f',0), Field('d','f',0)]
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

    inner_vertices = tuple(set(op.pos for op in operators if not op.external))
    outer_vertices = tuple(set(op.pos for op in operators if op.external))

    operators.sort()
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
            elif LSZ_reduction and to_be_contract[0].external and to_be_contract[i].external: # if LSZ reduction is applied, we cannot contract external operators
                continue
            try:
                pair = to_be_contract[0] + to_be_contract[i]
            except TypeError:
                continue
            if to_be_contract[0].fermionic and (i % 2 == 0): # if the operator is fermionic, we need to consider the sign
                multiplicity_in_this_layer *= -1
            contract(
                to_be_contract[1:i] + to_be_contract[i+1:], # remove the two contracted operators
                contracted + [pair], # add the contracted pair to the list
                multiplicity * multiplicity_in_this_layer # update the multiplicity
            )
            multiplicity_in_this_layer = 1 # reset the multiplicity for the next iteration

        return all_possible_contraction # the multiplicity is 1 for now, we haven't implemented symmetry for internal vertices yet
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
    operators = [Operator('1','e',1,fermionic=True,external=True),
                Operator('2','e',1,fermionic=True,external=True),
                Operator('3','e',-1,fermionic=True,external=True),
                Operator('4','e',-1,fermionic=True,external=True),
                Operator('x','a',0,fermionic=False,external=False),
                Operator('y','a',0,fermionic=False,external=False),
                Operator('x','e',1,fermionic=True,external=False),
                Operator('y','e',1,fermionic=True,external=False),
                Operator('x','e',-1,fermionic=True,external=False),
                Operator('y','e',-1,fermionic=True,external=False)]
    # ee -> ee scattering with internal photon exchange
    for diagram,multiplicity in contraction(operators,LSZ_reduction=True):
        print(f"Multiplicity: {multiplicity}", diagram)
