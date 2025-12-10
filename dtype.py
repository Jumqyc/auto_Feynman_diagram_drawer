from dataclasses import dataclass,field
from typing import Tuple


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

    def __post_init__(self):
        if self.charge not in {1, -1, 0}:
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
        return f"{self.type}: {self.initial}{'->-' if self.arrow else '---'}{self.final}"
    def __eq__(self, other: 'Propagator') -> bool:
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
    def list_of_particles(self) -> set[Tuple[str, bool]]:
        return set((p.type, p.arrow) for p in self.propagators)
    
    def __repr__(self) -> str:
        return f"""Outer vertices: {self.outer_vertices}
        Inner vertices: {self.inner_vertices}
        Propagators: {self.propagators}"""
    def is_equivalent(self, other: 'Diagram') -> bool:
        pass

@dataclass(frozen=True)
class Uncharged_Boson(Operator):
    '''
    A class representing an uncharged scalar particle. Inherits from Operator.
    Attributes:
        pos (str): The position or label of the particle (e.g., 'x', 'y', 'p1', 'k2').
        type (str): The type of the particle (e.g., 'phi' for scalar field).
        external (bool): True if the particle is external, False if internal.
    '''
    pos: str
    type: str
    charge: int = 0
    external: bool = False
    def __post_init__(self):
        object.__setattr__(self, 'fermionic', False)

@dataclass(frozen=True)
class Charged_Boson(Operator):
    '''
    A class representing a charged bosonic particle. Inherits from Operator.
    Attributes:
        pos (str): The position or label of the particle (e.g., 'x', 'y', 'p1', 'k2').
        type (str): The type of the particle (e.g., 'W+' for W boson).
        charge (int): The charge of the particle (1 for creation, -1 for annihilation).
        external (bool): True if the particle is external, False if internal.
    '''
    pos: str
    type: str
    charge: int
    external: bool = False
    def __post_init__(self):
        if self.charge not in {1, -1}:
            raise ValueError("charge must be 1 or -1 for Charged_Boson")
        object.__setattr__(self, 'fermionic', False)


@dataclass(frozen=True)
class Fermion(Operator):
    '''
    A class representing a fermionic particle. Inherits from Operator.
    Attributes:
        pos (str): The position or label of the particle (e.g., 'x', 'y', 'p1', 'k2').
        type (str): The type of the particle (e.g., 'e' for electron).
        charge (int): The charge of the particle (1 for creation, -1 for annihilation).
        external (bool): True if the particle is external, False if internal.
    '''
    pos: str
    type: str
    charge: int
    external: bool = False
    def __post_init__(self):
        if self.charge not in {1, -1}:
            raise ValueError("charge must be 1 or -1 for Fermion")
        object.__setattr__(self, 'fermionic', True)