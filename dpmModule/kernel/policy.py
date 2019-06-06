import random


class AbstractGraph():
    def __init__(self, all_elements, storage, accessible_elements = [] ) :
        self.storage = storage
        self._all_elements = all_elements
        self.accessible_elements = accessible_elements
        self._element_map = {}
        random.seed(42)
        for el in self._all_elements:
            name = el.name
            while name in self._element_map:
                name = name + '_' + str(random.randint(0,1000))
            self._element_map[name] = el
    
    def get_element(self, name):
        if name in self._element_map:
            return self._element_map[name]
        else:
            raise KeyError(f'''No element name {name} exist. Check your graph configuration, or
            check with graph.get_storage()''')
    
    def get_all(self):
        return self.accessible_elements

    def get_storage(self):
        return self.storage

class GraphScheduler():
    pass

class FetchingPolicy():
    def __init__(self, graph, *args, **kwargs):
        self.target = graph.get_all()

    def get_sorted(self):
        raise NotImplementedError('''
        Describle how to rearrange element's priority.
        You can also purpose some FILTERING in this actions, but
        it must be careful becuase following rules cannot notice filtered 
        elements had been existed in graph.''')


class TypebaseFetchingPolicy(FetchingPolicy):
    def __init__(self, graph, final_name, priority_list = [0,1,2,3]):
        super(TypebaseFetchingPolicy, self).__init__(graph)
        self.sorted = []
        for clstype in priority_list:
            self.sorted += (list(filter(lambda x:isinstance(x,clstype), self.target)))
        self.sorted.append(graph.get_element(final_name))
    
    def get_sorted(self):
        return [i for i in self.sorted]
    


class AbstractRule():
    '''Rule defines given element will be aceepted or not. This concept is somewhat simmillar with Constraint,
    but rule can constraint element 'Dynamically', which means can refer every context in judging point.
    '''
    def get_related_elements(self, reference_graph):
        raise NotImplementedError('''get_related_elements(reference_graph) will return which elements are 
        using this rule. Return : elements(list), will be hashed by unique namespace from storage.
        ''')

    def check(self, reference_graph, context = None):
        raise NotImplementedError('''check(referce_graph) will return current context / graph satisfy
        given rule or not. context not offered yet, but for future work it is given.
        ''')

    def compile(self, reference_graph):
        '''compile() is cache hint for fast running. You can get reference elements earlier, and store 
        them as object instance, and refer those elements in runtime's check() calling. Overiding this
        method is not mandatory; you can skip this method(will not raise any error)
        '''
        return

class ConcurrentRunRule(AbstractRule):
    def __init__(self, state_element, checking_element):
        self._state_element_name = state_element
        self._checking_element_name = checking_element

    