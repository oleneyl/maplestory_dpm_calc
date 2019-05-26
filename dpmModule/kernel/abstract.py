'''
*******************************

abstract.py

This module only provides abstract module concept.
Creating these classes' instance is not recommended.
Please make sure class in this module provides good intuition for
user who want to inspect whole featur eof package.

*******************************
'''

class AbstractGraphElement():




class AbstractStore():







class AbstractTrackableOperation():
    def __init__(self):


    def 



class AbstractGraphBuilder():
    def __init__(self):
        self._trackable_elements = {}
        pass
    
    def package(self):
        raise NotImplementedError("Implement AbstractGraphBuilder.package to return type of AbstractGraph")

    def start_element_scope(self):
        

    def track_element(self, graph_element : AbstractGraphElement):


    def 



class AbstractScenarioGraph():
    def __init__(self, *store_parameter):
        self.store = Store(*store_parameter)
        pass
    
    def build_graph(self, *args):
        raise NotImplementedError("You must Implement build_graph function to create specific graph.")
    
    def get_single_network_information(self, graphel, isList = False):
        '''Function get_single_network_information (param graphel : GraphElement)
        Return Network information about given graphel, as d3 - parsable dictionary element.
        return value is dictionary followed by below.
        
        nodes : list - of - {"name" : GraphElement._id}
        links : list - of - {"source" : index - of - source,
                            "target" : index - of - target,
                            "type" : type - of - node}
        
        '''
        if not isList:
            nodes, links = self.getNetwork(graphel)
        else:
            nodes = [i[0] for i in graphel]
            links = []
            for el in graphel:
                _nds , _lns = self._getNetworkRecursive(el[0], nodes, links)
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


class AbstractSession():



class AbstractAnalytics():

