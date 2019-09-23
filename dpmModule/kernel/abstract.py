'''
*******************************

abstract.py

This module only provides abstract module concept.
Creating these classes' instance is not recommended.
Please make sure class in this module provides good intuition for
user who want to inspect whole featur eof package.

*******************************
'''

class AbstractScenarioGraph():    

    def build_graph(self, *args):
        raise NotImplementedError("You must Implement build_graph function to create specific graph.")
    
    def get_single_network_information(self, graphel, is_list = False):
        '''Function get_single_network_information (param graphel : GraphElement)
        Return Network information about given graphel, as d3 - parsable dictionary element.
        return value is dictionary followed by below.
        
        nodes : list - of - {"name" : GraphElement._id}
        links : list - of - {"source" : index - of - source,
                            "target" : index - of - target,
                            "type" : type - of - node}
        
        '''
        if not is_list:
            nodes, links = self.getNetwork(graphel)
        else:
            nodes = [i for i in graphel]
            links = []
            for el in graphel:
                _nds , _lns = self._getNetworkRecursive(el, nodes, links)
                nodes += _nds
                links += _lns
            #refinement
            nodeSet = []
            for node in nodes:
                if node not in nodeSet:
                    nodeSet.append(node)
            nodes = nodeSet
        
        nodeIndex = []            
        for node, idx in zip(nodes, range(len(nodes))):
            node_info = {"name" : node._id, "expl" : node.get_explanation(lang = "ko"), "flag" : node._flag}
            if node._flag & 1:
                node_info["delay"] = node.skill.get_info()["delay"]
                node_info["cooltime"] = node.skill.get_info()["cooltime"]
                node_info["expl"] = node.skill.get_info(expl_level = 0)["expl"]
            if idx <= len(graphel):
                node_info["st"] = True
            else:
                node_info["st"] = False
                
            nodeIndex.append(node_info)
        #nodeIndex = [{"name" : node._id, "expl" : node.get_explanation(lang = "ko"), "flag" : node._flag} for node in nodes]
        
        linkIndex = []
        
        for link in links:
            linkIndex.append({"source" : link[0], "target" : link[1], "type" : link[2]})
            if len(link[2].split(" ")) > 1:
                linkIndex[-1]["type"] = link[2].split(" ")[0]
                linkIndex[-1]["misc"] = link[2].split(" ")[1:]
            
        for node, idx in zip(nodes, range(len(nodeIndex))):
            for link in linkIndex:
                if link["source"] == node:
                    link["source"] = idx
                if link["target"] == node:
                    link["target"] = idx
                    
        return nodeIndex, linkIndex

    def getNetwork(self, ancestor):
        nodes, links = self._getNetworkRecursive(ancestor, [ancestor], [])
        nodes.insert(0, ancestor)
        return nodes, links
        
    def _getNetworkRecursive(self, ancestor, nodes, links):
        try:
            _nodes = []
            _links = ancestor.get_link()
            _linksCandidate = ancestor.get_link()
        except AttributeError:
            raise AttributeError('Cannot find Appropriate Link. Make sure your Graph element task has correct reference')
        if len(_linksCandidate) > 0:
            for _, el, _t in _linksCandidate:
                if el not in nodes:
                    _nodes.append(el)
                    nds, lis = self._getNetworkRecursive(el, nodes + _nodes, links + _links)
                    _nodes += nds
                    _links += lis
                
        return _nodes, _links


class AbstractScheduler():
    def __init__(self, graph):
        self.graph = graph
        self.total_time_left= None
        self.total_time_initial = None

    def initialize(self, time):
        raise NotImplementedError(''' AbstractScheduler.initializer(time) must be implemented,
        this function will initialize scheduler with given Schduling total time.
        ''')

    def get_current_time(self):
        return self.total_time_initial - self.total_time_left

    def is_simulation_end(self):
        return (self.total_time_left < 0)

    def spend_time(self, time):
        '''This function might be overrided, with super().spend_time(time) calling.
        '''
        self.total_time_left -= time
        self.graph.spend_time(time)

    def dequeue(self):
        raise NotImplementedError('''Scheduler.dequeue() must be implemented,
        This function will return appropriate element that will be executed by
        Simulator, which satisfy every rule, for FetchingPolicy.
        ''')

    def get_delayed_task(self):
        raise NotImplementedError('''Scheduler.get_delayed_task() must be implemented,
        This function will return delayed task whlie previous task pending.''')

class AbstractSession():
    pass


class AbstractAnalytics():
    pass


class AbstractVEnhancer():
    def get_priority(self):
        raise NotImplementedError('''AbstractVEnhancer.get_priority must return dict like object,
        which have keys [enhance, vskill], contains list of {name : skillname}, defines which skill has priority
        when enhancing.
        ''')
    def get_reinforcement_with_register(self, index, incr, crit, target):
        raise NotImplementedError('''get_reinforcement_with_register must return CharacterModifier, with registering given skill
        as given priority, with appropriate Modifier.
        ''')

class AbstractVBuilder():
    '''Class AbstractVBuilder
    This builder class creates VEnhancer, from given settings, with given JobGenerator.
    '''
    def __init__(self):
        pass

    def build_enhancer(self, character, generator):
        raise NotImplementedError('''AbstractVBuilder.build_enhancer must return VEnhancer as as result,
        with properly handling given character and generator.
        ''')