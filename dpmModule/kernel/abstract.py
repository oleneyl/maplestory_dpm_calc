"""
*******************************

abstract.py

This module only provides abstract module concept.
Creating these classes' instance is not recommended.
Please make sure class in this module provides good intuition for
user who wants to inspect whole feature of package.

*******************************
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import GraphElement, AbstractSkill, CharacterModifier
    from ..character.characterKernel import AbstractCharacter, JobGenerator

    Link = Tuple[GraphElement, GraphElement, str]


class AbstractScenarioGraph:
    def build_graph(self, *args) -> None:
        raise NotImplementedError("You must Implement build_graph function to create specific graph.")

    def get_single_network_information(self, graphel: Union[GraphElement, List[GraphElement]],
                                       is_list: bool = False) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Function get_single_network_information (param graphel : GraphElement)
        Return Network information about given graphel, as d3 - parsable dictionary element.
        return value is dictionary followed by below.

        nodes : list - of - {"name" : GraphElement._id}
        links : list - of - {"source" : index - of - source,
                            "target" : index - of - target,
                            "type" : type - of - node}

        """
        if not is_list:
            nodes, links = self.get_network(graphel)
        else:
            nodes: List[GraphElement] = [i for i in graphel if i is not None]
            links: List[Link] = []
            for el in graphel:
                if el is not None:
                    _nds, _lns = self._get_network_recursive(el, nodes, links)
                    nodes += _nds
                    links += _lns
            # refinement
            nodeSet = []
            for node in nodes:
                if node not in nodeSet:
                    nodeSet.append(node)
            nodes = nodeSet

        nodeIndex: List[Dict[str, Any]] = []
        for node, idx in zip(nodes, range(len(nodes))):
            node_info = {"name": node._id, "expl": node.get_explanation(lang="ko"), "flag": node._flag}
            if node._flag & 1:
                node_info["delay"] = node.skill.get_info()["delay"]
                node_info["cooltime"] = node.skill.get_info()["cooltime"]
                node_info["expl"] = node.skill.get_info(expl_level=0)["expl"]
            if idx <= len(graphel):
                node_info["st"] = True
            else:
                node_info["st"] = False

            nodeIndex.append(node_info)
        # nodeIndex = [{"name" : node._id, "expl" : node.get_explanation(lang = "ko"), "flag" : node._flag} for node in nodes]

        linkIndex: List[Dict[str, Any]] = []
        for link in links:
            linkIndex.append({"source": link[0], "target": link[1], "type": link[2]})
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

    def get_network(self, ancestor: GraphElement) -> Tuple[List[GraphElement], List[Link]]:
        nodes, links = self._get_network_recursive(ancestor, [ancestor], [])
        nodes.insert(0, ancestor)
        return nodes, links

    def _get_network_recursive(self, ancestor: GraphElement, nodes: List[GraphElement], links: List[Link])\
            -> Tuple[List[GraphElement], List[Link]]:
        try:
            _nodes: List[GraphElement] = []
            _links = ancestor.get_link()
            _linksCandidate = ancestor.get_link()
        except AttributeError:
            raise AttributeError(f'''Cannot find Appropriate Link. Make sure your Graph element task 
                    has correct reference. This was raised with ancestor {ancestor}''')
        if len(_linksCandidate) > 0:
            for _, el, _t in _linksCandidate:
                if el not in nodes:
                    _nodes.append(el)
                    nds, lis = self._get_network_recursive(el, nodes + _nodes, links + _links)
                    _nodes += nds
                    _links += lis

        return _nodes, _links


class AbstractSession:
    pass


class AbstractAnalytics:
    pass


class AbstractVEnhancer:
    def get_priority(self) -> Dict[str, List[Dict[str, Any]]]:
        raise NotImplementedError('''AbstractVEnhancer.get_priority must return dict like object,
        which have keys [enhance, vskill], contains list of {name : skillname}, defines which skill has priority
        when enhancing.
        ''')

    def get_reinforcement_with_register(self, index: int, incr, crit: bool, target: AbstractSkill) -> CharacterModifier:
        raise NotImplementedError('''get_reinforcement_with_register must return CharacterModifier, with registering given skill
        as given priority, with appropriate Modifier.
        ''')

    def getV(self, use_index: int, upgrade_index: int) -> int:
        raise NotImplementedError()


class AbstractVBuilder:
    """Class AbstractVBuilder
    This builder class creates VEnhancer, from given settings, with given JobGenerator.
    """

    def __init__(self) -> None:
        pass

    def build_enhancer(self, character: AbstractCharacter, generator: JobGenerator) -> AbstractVEnhancer:
        raise NotImplementedError('''AbstractVBuilder.build_enhancer must return VEnhancer as as result,
        with properly handling given character and generator.
        ''')
