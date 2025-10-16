from typing import NamedTuple

class field:
    def __init__(self,pos,type,dagger):
        self.pos = pos
        self.type = type
        self.dagger = dagger
    def __add__(self,other) -> 'field': # contraction of two operators
        if self.dagger == 1 and other.dagger == -1:
            return field(f"({self.pos}->{other.pos})", self.type, 0)
        elif self.dagger == -1 and other.dagger == 1:
            return field(f"({other.pos}<-{self.pos})", self.type, 0)
        else:
            return field(f"({self.pos}-{other.pos})",self.type, 0)
    def __eq__(self,other): # equal if pos, type and dagger are all equal
        return self.pos == other.pos and self.type == other.type and self.dagger == other.dagger
    def __lt__(self,other): # less than for sorting
        return (self.pos,self.type,self.dagger) < (other.pos,other.type,other.dagger)
    def __repr__(self):
        return str((self.pos))
        

def contraction(operators:list[field]) -> list[list]:
    """
    Perform contraction of a string of operators according to Wick's theorem.

    Parameters:
    string_of_operators (str): A string representing a sequence of creation and annihilation operators.

    Returns:
    list: A list of terms resulting from the contraction and its multiplicity.
    
    Example:
    >>> contraction("abcd")
    [['ab','cd',1], ['ac','bd',1], ['ad','bc',1]]
    """
    if len(operators) % 2 != 0:
        raise ValueError("The number of operators must be even for contraction.")
    if not isinstance(operators, list) and not all(isinstance(op, field) for op in operators):
        raise ValueError('The type of the operator must be type field in the list')
    if not sum(op.dagger for op in operators) == 0:
        raise ValueError("The number of creation and annihilation operators must be equal.")

    operators.sort()
    return_list = []
    def contract(to_be_contract:list[field],contracted:list = [])->list[list]:
        if not to_be_contract:
            return_list.append(contracted)
            return
        for i in range(1,len(to_be_contract)): # contract the first operator with the ith operator
            if ((i < len(to_be_contract)-1 
                and to_be_contract[i] == to_be_contract[i+1]) 
                or to_be_contract[0].dagger + to_be_contract[i].dagger != 0 
                or to_be_contract[0].type != to_be_contract[i].type):
                continue
            else:
                contract(
                    to_be_contract[1:i] + to_be_contract[i+1:], 
                    # remove the two contracted operators
                    contracted + [to_be_contract[0] + to_be_contract[i]] 
                    # add the contracted pair to the list
                )
        return return_list
    
    return_list:list = contract(operators)
    for term in return_list:
        term.sort()
    return_list.sort()
    
    ptr = 0
    while ptr < len(return_list)-1:
        if return_list[ptr] == return_list[ptr+1]:
            return_list.pop(ptr+1)
        else:
            ptr += 1

    return return_list

def LSZ_reduction(list_of_contraction:list[list[field]]) -> list[list[field]]:
    """
    Perform LSZ reduction on a list of contractions. We will recognize the numbers as external legs and remove them.
    Parameters:
    list_of_contraction (list): A list of contractions, where each contraction is a list of field objects.
    Returns:
    list: A list of terms resulting from the LSZ reduction.
    >>> LSZ_reduction([['(1->3)','(2->4)'], ['(1->4)','(2->3)']])
    [] # since all terms have external legs
    >>> LSZ_reduction([['(x->y)','(1->2)'], ['(x->y)']])
    [['(x->y)']]
    """
    ptr = 0
    while ptr < len(list_of_contraction):
        term :list[field] = list_of_contraction.pop(ptr)
        for pair in term:
            if pair.pos[1] in '0123456789' and pair.pos[-2] in '0123456789':
                break
        else:
            term.insert(ptr,term)
            ptr += 1
                

    return list_of_contraction
print(
    LSZ_reduction(
        contraction([
            field('1','e',1),
            field('2','A',0),   
            field('3','e',-1),
            field('4','A',0),
            field('x','e',1),
            field('x','e',-1),
            field('x','A',0),
            field('y','e',1),
            field('y','e',-1),
            field('y','A',0)
        ])
    )
)