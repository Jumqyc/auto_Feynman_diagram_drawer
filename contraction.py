class Field:
    '''
    A class representing a quantum field operator.

    Attributes:

    pos (str): The position of the operator in the diagram.
    type (str): The type of the operator (e.g., 'phi', 'psi').
    dagger (int): 1 for creation operator, -1 for annihilation operator, 0 for real field.
    statistics (bool): True for fermionic operators, False for bosonic operators.
    external (bool): True if the operator is external, False if internal.

    Methods:

    __add__(self, other): Contract two operators to form a propagator. Raises TypeError if the operators cannot be contracted.
    __eq__(self, other): Check if two operators are equal.
    __lt__(self, other): Compare two operators for sorting.
    __repr__(self): Return a string representation of the operator.
    '''
    def __init__(self,pos:str,
                 type:str,
                 dagger:int,
                 fermionic:bool=False,
                 external:bool = False)->None:
        self.pos = pos
        self.type = type
        self.dagger = dagger
        self.fermionic = fermionic
        self.external = external
        if dagger not in [1,-1,0]:
            raise ValueError("dagger must be 1 (particle), -1 (antiparticle) or 0 (real).")
    def __add__(self:'Field',other:'Field') -> 'Propagator': # contraction of two operators to a propagator
        if self.type != other.type or self.dagger + other.dagger != 0:
            raise TypeError("Cannot contract these operators.")
        
        if self.dagger == 1 and other.dagger == -1:
            return Propagator(type=self.type,
                              initial=self.pos,
                              final=other.pos,
                              arrow=True)
        elif self.dagger == -1 and other.dagger == 1:
            return Propagator(type=self.type,
                              initial=other.pos,
                              final=self.pos,
                              arrow=True)
        else:
            return Propagator(type=self.type,
                              initial=self.pos,
                              final=other.pos,
                              arrow=False)
    def __eq__(self,other): # equal if pos, type and dagger are all equal
        return self.pos == other.pos and self.type == other.type and self.dagger == other.dagger
    def __lt__(self,other): # less than for sorting
        return (self.pos,self.type,self.dagger) < (other.pos,other.type,other.dagger)
    def __repr__(self):
        return str((self.pos))
    
class Propagator:
    def __init__(self,type:str,arrow:bool,initial:str,final:str):
        self.type = type
        self.initial = initial
        self.final = final
        self.arrow = arrow
    def __eq__(self:'Propagator',other:'Propagator'):
        return (self.type,self.initial,self.final,self.arrow) == (other.type,other.initial,other.final,other.arrow)
    def __lt__(self:'Propagator',other:'Propagator'):
        return (self.type,self.initial,self.final,self.arrow) < (other.type,other.initial,other.final,other.arrow)
    def __repr__(self)-> str:
        if self.arrow:
            return f"{self.type}({self.initial}->-{self.final})"
        else:
            return f"{self.type}({self.initial}---{self.final})"
        
class Diagram:
    '''
    A class describing  the structure of Feynman Diagrams.
    '''
    def __init__(self,outer_vertices:set[str],
                 inner_vertices:set[str],
                 propagators:list[Propagator]):
        self.outer_vertices = outer_vertices
        self.inner_vertices = inner_vertices
        self.propagators = propagators

        self.list_of_particles = list(set((p.type,p.arrow) for p in propagators))

    def __eq__(self:'Diagram',other:'Diagram') -> bool:
        if self.outer_vertices != other.outer_vertices or self.inner_vertices != other.inner_vertices:
            return False
        if not self.propagators.sort() == other.propagators.sort():
            return False
        # we haven't implement the symmetry for internal vertices yet
        return True
    def __repr__(self)->str:
        return f'''     Outer vertices: {self.outer_vertices}
        Inner vertices: {self.inner_vertices}
        Propagators: {self.propagators}'''

def contraction(operators:list[Field]) -> list[tuple[Diagram,int]]:
    """
    Perform Wick contraction on a list of quantum field operators.
    Args:
        operators (list[Field]): A list of quantum field operators to be contracted.
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
    if not isinstance(operators, list) and not all(isinstance(op, Field) for op in operators):
        raise ValueError('The type of the operator must be type field in the list')
    if not sum(op.dagger for op in operators) == 0:
        raise ValueError("The number of creation and annihilation operators must be equal.")

    
    inner_vertices = set(op.pos for op in operators if not op.external)
    outer_vertices = set(op.pos for op in operators if op.external)

    operators.sort()
    all_possible_contraction = []
    def contract(to_be_contract:list[Field],
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
        return_list.append(
            (Diagram(outer_vertices,inner_vertices,propagators),
             multiplicity))
        
    return return_list

for diagram,multiplicity in contraction([Field('a','f',0,fermionic=True),
            Field('b','f',0,fermionic=True),
            Field('c','f',0,fermionic=True),
            Field('d','f',0,fermionic=True)]):
    print(f"Multiplicity: {multiplicity}", diagram)
