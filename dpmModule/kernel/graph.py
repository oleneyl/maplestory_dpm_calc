import json
from collections import Counter
from typing import Any, Dict, Iterable, List, Optional, TextIO

'''
global properties

- unsafe_global_storage
- unsafe_channel_callback
- unsafe_global_namespace_do_not_access_direct
- unsafe_global_evaluative_graph_element_controls
'''


def initialize_global_properties() -> None:
    global unsafe_global_collection_do_not_access_direct
    unsafe_global_collection_do_not_access_direct = GlobalCollection()


def _unsafe_access_global_storage() -> 'GlobalCollection':
    global unsafe_global_collection_do_not_access_direct
    return unsafe_global_collection_do_not_access_direct


class NamespaceObject:
    def __init__(self, namespace: Optional[str] = None) -> None:
        self.namespace: Optional[str] = namespace
        self.inheritted_namespace: Optional[str] = None
        self.assigned_namespace: Optional[str] = None

    def inherit_namespace(self, namespace: Optional[str]) -> None:
        self.inheritted_namespace = namespace

    def get_my_namespace(self, namespace_from_parent: Optional[str], index: int) -> str:
        if self.namespace:
            true_namespace = self.namespace
        else:
            if self.inheritted_namespace is None:
                true_namespace = '/'.join([namespace_from_parent, str(index)])
            else:
                true_namespace = '/'.join([namespace_from_parent, self.inheritted_namespace])
        self.assigned_namespace = true_namespace
        return true_namespace

    def get_assigned_namespace(self) -> str:
        if self.assigned_namespace is None:
            raise ValueError('No namespace was assigned yet')
        return self.assigned_namespace


class GlobalOperation:
    @classmethod
    def assign_storage(cls) -> None:
        _unsafe_access_global_storage().assign_storage()

    @classmethod
    def save_storage(cls) -> None:
        _unsafe_access_global_storage().save_storage()

    @classmethod
    def attach_namespace(cls) -> None:
        _unsafe_access_global_storage().attach_namespace()

    @classmethod
    def convert_to_static(cls) -> None:
        _unsafe_access_global_storage().convert_to_static()

    @classmethod
    def revert_to_dynamic(cls) -> None:
        _unsafe_access_global_storage().revert_to_dynamic()

    @classmethod
    def notify_dynamic_object_added(cls, obj: 'DynamicObject') -> None:
        _unsafe_access_global_storage().add_dynamic_object(obj)

    @classmethod
    def export_collection(cls) -> 'GlobalCollection':
        collection = _unsafe_access_global_storage()
        initialize_global_properties()
        return collection

    @classmethod
    def set_storage(cls, storage: 'AbstractStorage') -> None:
        _unsafe_access_global_storage().set_storage(storage)

    @classmethod
    def export_storage_without_complex_option(cls) -> 'GlobalCollection':
        GlobalOperation.assign_storage()
        GlobalOperation.attach_namespace()
        GlobalOperation.save_storage()
        GlobalOperation.convert_to_static()
        return GlobalOperation.export_collection()


class GlobalCollection:
    historical_track_prefix: str = '_temporal_save_'

    def __init__(self) -> None:
        self._found_dynamic_object: 'List[DynamicObject]' = []
        self._storage: 'AbstractStorage' = DeepConfigurationStorage({})

    def get_storage(self) -> 'AbstractStorage':
        return self._storage

    def get_dynamic_objects(self) -> 'List[DynamicObject]':
        return self._found_dynamic_object

    def set_storage(self, storage: 'AbstractStorage'):
        self._storage = storage

    def add_dynamic_object(self, obj: 'DynamicObject') -> None:
        self._found_dynamic_object.append(obj)

    def assign_storage(self) -> None:
        for obj in self._found_dynamic_object:
            for kwd in obj.get_dynamic_variables():
                try:
                    getattr(obj, kwd).assign_storage_head(self._storage)
                except AttributeError:
                    raise AttributeError(f'''{kwd} at {obj}({obj.name}) is not Dynamic object. Check whether you
                    had been dangerously override given property.''')

    def save_storage(self) -> None:
        for obj in self._found_dynamic_object:
            for kwd in obj.get_dynamic_variables():
                getattr(obj, kwd).save_storage_head(self._storage)

    def attach_namespace(self) -> None:
        for obj in self._found_dynamic_object:
            obj.attach_namespace()

    def convert_to_static(self) -> None:
        for obj in self._found_dynamic_object:
            for kwd in obj.get_dynamic_variables():
                if not isinstance(getattr(obj, kwd), AbstractDynamicVariableInstance):
                    if not type(getattr(obj, kwd)) in [str, float, int, bool, type(None)]:
                        raise TypeError(f'''Trying to evaluate non - dynamic variable [{obj}({obj._namespace})/{kwd}] into static.
                        Tryed element type : {type(getattr(obj, kwd))}
                        This error was raised to prevent consistency problem.''')
                setattr(obj, self.historical_track_prefix + kwd, getattr(obj, kwd))
                setattr(obj, kwd, getattr(obj, kwd).evaluate())

    def revert_to_dynamic(self) -> None:
        for obj in self._found_dynamic_object:
            for kwd in obj.get_dynamic_variables():
                try:
                    setattr(obj, kwd, getattr(obj, self.historical_track_prefix + kwd))
                except AttributeError:
                    raise AttributeError('Cannot find saved object before evalute. Check whether you have had \
                        called convert_to_static()')


class DynamicVariableTracker:
    def __init__(self, track_target, callback=[], options={}) -> None:
        self._track_target = track_target
        self._recorded_variable = []
        self._callback = callback
        self.options = options

    def __enter__(self) -> None:
        self._recorded_variable = dir(self._track_target)

    def __exit__(self, type, value, traceback) -> None:
        final_variables = dir(self._track_target)
        tracked_result = Counter(final_variables) - Counter(self._recorded_variable)
        tracked_result = [var for var, i in tracked_result.most_common()]
        self.parse_variable(tracked_result)

    def parse_variable(self, tracked_result) -> None:
        raise NotImplementedError('Method not implemented DynamicVariableTracker.parse_variable')


class AbstractDiGraphElement(NamespaceObject):
    def __init__(self, namespace: Optional[str] = None) -> None:
        super(AbstractDiGraphElement, self).__init__(namespace=namespace)
        self._next_instance_list = []
        self._prev_instance_list = []

    # Graph parsing methods
    def add_next_instance(self, instance):
        if instance not in self._next_instance_list:
            self._next_instance_list.append(instance)
        if self not in instance.get_next_instances():
            instance._prev_instance_list.append(self)

    def add_prev_instance(self, instance):
        if instance not in self._prev_instance_list:
            self._prev_instance_list.append(instance)
        if self not in instance.get_prev_instances():
            instance._next_instance_list.append(self)

    def get_next_instances(self):
        return [i for i in self._next_instance_list]

    def get_prev_instance(self):
        return [i for i in self._prev_instance_list]

    @staticmethod
    def recurrent_run(func):
        """This function is decorator.
        Use this method to func(instance, param, index) -> action, return recursive param
        """

        def output_func(self, instance: 'AbstractDiGraphElement', param, index):
            rec_param = func(self, instance, param, index)
            for idx, inst in enumerate(instance.get_next_instances()):
                output_func(self, inst, rec_param, idx)

        return output_func


class AbstractDynamicVariableInstance(AbstractDiGraphElement):
    def __init__(self, namespace: Optional[str] = None) -> None:
        super(AbstractDynamicVariableInstance, self).__init__(namespace=namespace)
        self.storage: Optional[AbstractStorage] = None
        self._already_finalized: bool = False

    def evaluate_override(self) -> Any:
        raise NotImplementedError('''
        Please implement AbstractDynamicVariableInstance.evaluate()
        You may trying to use Abstract Instance without recoginizing what
        are you doing. Please be aware what you are trying to do.
        ''')

    def evaluate(self) -> Any:
        if self.storage is not None:
            if self.storage.has_namespace(self.assigned_namespace):
                return self.storage.get_namespace(self.assigned_namespace)

        return self.evaluate_override()

    def represent(self) -> str:
        raise NotImplementedError('''
        Please implement AbstractDynamicVariableInstance.represent()
        You may trying to use Abstract Instance without recoginizing what
        are you doing. Please be aware what you are trying to do.
        ''')

    def build_namespace(self, namespace: Optional[str], index: int) -> str:
        my_namespace = self.get_my_namespace(namespace, index)
        return my_namespace

    def get_next_nodes(self):
        raise NotImplementedError('''
        Please implement ABstractDynamicVariableInstance.get_next_nodes()
        You may trying to use Abstract Instance without recoginizing what
        are you doing. Please be aware what you are trying to do.
        ''')

    def finalize(self, storage: 'AbstractStorage') -> None:
        if self._already_finalized:
            return
        else:
            if hasattr(self, '_finalizing_action'):
                self._finalizing_action(storage)
            self._already_finalized = True
            map(lambda x: x.finalize(), self.get_next_nodes())

    def initialize_finalized_state(self) -> None:
        if self._already_finalized:
            self._already_finalized = False
            map(lambda x: x.reset_finalized_variable(), self.get_next_nodes())

    @AbstractDiGraphElement.recurrent_run
    def attach_namespace(self, inst: 'AbstractDynamicVariableInstance', namespace: Optional[str], index: int) -> str:
        my_namespace = inst.build_namespace(namespace, index)
        return my_namespace

    @AbstractDiGraphElement.recurrent_run
    def assign_storage(self, inst: 'AbstractDynamicVariableInstance', storage: 'AbstractStorage', index: int) -> 'AbstractStorage':
        inst.storage = storage
        return storage

    @AbstractDiGraphElement.recurrent_run
    def save_storage(self, inst: 'AbstractDynamicVariableInstance', storage: 'AbstractStorage', index: int) -> 'AbstractStorage':
        touch_end = len(inst.get_next_instances()) == 0
        try:
            storage.set_namespace(inst.get_assigned_namespace(), inst.evaluate(),
                                  touch_end=touch_end)
        except Exception as e:
            raise ValueError(f'''
            Error raised from instance {inst} [{inst.get_assigned_namespace()}].
            This error might be raised by incompatibel value passing to DynamicVariable.

            Original Error : {e}''')
        return storage

    def attach_namespace_head(self, namespace: Optional[str]) -> None:
        self.attach_namespace(self, namespace, 0)

    def save_storage_head(self, storage: 'AbstractStorage') -> None:
        self.save_storage(self, storage, 0)

    def assign_storage_head(self, storage: 'AbstractStorage') -> None:
        self.assign_storage(self, storage, 0)


class DynamicConversionTool:
    """CONVERT_ATTR is a hint, that converts non - dynamic instance into
    dynamic instance automatically. Without this hint, unknown element will
    emit WARNING that program can cause data consistancy error.

    You can define your custom object with CONVERT_ATTR as a instance method name.
    In that function, you must write as below ::
    (1) Write how to convert element if element is not a dynamic variable.
    (2) if given element is already dynamic, make method return None.
    """
    CONVERT_ATTR: str = '_dynamic_variable_hint'

    @classmethod
    def wrap_non_dynamic_variable(cls, target):
        ret_target = target
        if not isinstance(target, AbstractDynamicVariableInstance):
            if not type(target) in [str, float, int, bool, type(None)]:
                if hasattr(target, DynamicConversionTool.CONVERT_ATTR):
                    return getattr(target, DynamicConversionTool.CONVERT_ATTR)(target)
                else:
                    print(f'''Warning : Trying to convert none - static variable {target} into MimicDynamicVariable. This can
                    raise consistency problem.''')
            return DynamicVariableMimicingConstant(ret_target)
        else:
            return None


class DynamicObject:
    def __init__(self, namespace: Optional[str] = None) -> None:
        self._variable_precursor_keyword = []
        self.namespace: Optional[str] = namespace
        GlobalOperation.notify_dynamic_object_added(self)

    def add_precursor_keyword(self, keyword_list: List) -> None:
        filtered_keywords = []
        # Force tracked keywords as Dynamic Variable
        for kwd in keyword_list:
            # to prevent recurrent cascaded DynamicObject, DynamicObject will be tracked only once.
            if isinstance(getattr(self, kwd), DynamicObject):
                continue
            wrapped = DynamicConversionTool.wrap_non_dynamic_variable(getattr(self, kwd))
            if wrapped is not None:
                setattr(self, kwd, wrapped)  # Force attribute convert into Dynamic
            filtered_keywords.append(kwd)
        self._variable_precursor_keyword += filtered_keywords

    def get_dynamic_variables(self):
        return self._variable_precursor_keyword

    def attach_namespace(self) -> None:
        for kwd in self._variable_precursor_keyword:
            var = getattr(self, kwd)
            var.inherit_namespace(kwd)
            var.attach_namespace_head(self.namespace)
            # getattr(obj, kwd).attach_namespace_head('/'.join([obj.namespace,kwd]))


class EvaluativeGraphElement(DynamicObject):
    class GraphElementTracker(DynamicVariableTracker):
        def parse_variable(self, tracked_result) -> None:
            self._track_target.add_precursor_keyword(tracked_result)

    def __init__(self, namespace: Optional[str] = None) -> None:
        super(EvaluativeGraphElement, self).__init__(namespace=namespace)

    def dynamic_range(self, options={}) -> GraphElementTracker:
        return EvaluativeGraphElement.GraphElementTracker(self, options=options)


class AbstractStorage:
    def __init__(self, allow_fetch: bool = True, override: bool = True) -> None:
        self._allow_fetch: bool = allow_fetch
        self.override: bool = override

    def has_namespace(self, namespace: Optional[str]) -> bool:
        raise NotImplementedError('''has_namespace function call
        will return whether value exist in given namespace.
        ''')

    def get_namespace(self, namespace: Optional[str]):
        raise NotImplementedError('''get_namespace function call 
        will return value in given namespace.''')

    def set_namespace(self, namespace: Optional[str], value, touch_end: bool = False):
        raise NotImplementedError('''set_namespace function call
        will set given DynamicVariable into given namespace.

        Options::
        touch_end(bool) : if True, only return value if given namespace is 'End of tree', which means
        there is no other namespace under given namespace.

        ''')

    def write(self, fp: TextIO, only_endpoint: bool = True) -> None:
        """This function call
        will write current storage state into given fp(FILE pointer). """
        json.dump(self.export(only_endpoint=only_endpoint), fp)

    def export(self, only_endpoint: bool = True) -> None:
        raise NotImplementedError('''export() 
        Options::
        only_endpoint(bool) : If True, only save values that points variable chain's endpoint.
        If False, save all variable chain elemnt. It might contain a lot of redundant values.
        ''')


class ConfigurationStorage(AbstractStorage):
    def __init__(self, dict_obj, allow_fetch: bool = True, override: bool = True) -> None:
        super(ConfigurationStorage, self).__init__(allow_fetch=allow_fetch, override=override)
        self._origin = dict_obj

    def has_namespace(self, namespace: str) -> bool:
        if self._allow_fetch:
            if namespace in self._origin:
                return True
        return False

    def get_namespace(self, namespace: str):
        return self._origin[namespace]

    def set_namespace(self, namespace: str, value, touch_end: bool = False) -> None:
        if namespace in self._origin and not self.override:
            return
        else:
            self._origin[namespace] = value

    def export(self, only_endpoint: bool = True):
        if not only_endpoint:
            return self._origin
        else:
            kwds = list(self._origin.keys())
            avail_kwds = []
            for kwd in self._origin:
                count = 0
                for kwd_check in kwds:
                    if kwd in kwd_check:
                        count += 1
                        if count > 1:
                            break
                if count > 1:
                    continue
                else:
                    avail_kwds.append(kwd)
            endpoints = {k: self._origin[k] for k in avail_kwds}
            return endpoints


class DeepConfigurationStorage(AbstractStorage):
    DATA_KEYWORD: str = '_data_keyword_'

    def __init__(self, key_value_map, allow_fetch: bool = True, override: bool = True) -> None:
        super(DeepConfigurationStorage, self).__init__(allow_fetch=allow_fetch, override=override)
        self.space_generator: type(Dict) = dict
        self._origin = self.space_generator()

    def parse_namespace_to_address(self, namespace: str):
        return namespace.split('/')

    def get_variable_by_address(self, address: Iterable[str]):
        position = self._origin
        for kwd in address:
            try:
                position = position[kwd]
            except Exception:
                raise KeyError(f'Given address {"/".join(address)} not exist in storage')
        return position[DeepConfigurationStorage.DATA_KEYWORD]

    def save_variable_by_address(self, address: Iterable[str], variable) -> bool:
        position = self._origin
        for kwd in address:
            if kwd not in position:
                position[kwd] = self.space_generator()
            position = position[kwd]
        if not self.override:
            if DeepConfigurationStorage.DATA_KEYWORD in position:
                return False
        position[DeepConfigurationStorage.DATA_KEYWORD] = variable
        return True

    def has_namespace(self, namespace: str):
        address = self.parse_namespace_to_address(namespace)
        position = self._origin
        for kwd in address:
            if kwd not in position:
                return False
            else:
                position = position[kwd]
        return DeepConfigurationStorage.DATA_KEYWORD in position

    def get_namespace(self, namespace: str):
        address = self.parse_namespace_to_address(namespace)
        return self.get_variable_by_address(address)

    def set_namespace(self, namespace: str, value, touch_end: bool = False) -> None:
        address = self.parse_namespace_to_address(namespace)
        self.save_variable_by_address(address, value)

    def export(self, only_endpoint: bool = True):
        def recurrent_copy(copial_target, copy_point, parent, parent_key) -> None:
            for kwd in copial_target:
                if kwd == DeepConfigurationStorage.DATA_KEYWORD:
                    if len(copial_target) == 1:
                        parent[parent_key] = copial_target[DeepConfigurationStorage.DATA_KEYWORD]
                else:
                    copy_point[kwd] = {}
                    recurrent_copy(copial_target[kwd], copy_point[kwd], copy_point, kwd)

        copial = {}
        recurrent_copy(self._origin, copial, None, None)
        return copial


class DynamicVariableFromConfigurationStorage(AbstractDynamicVariableInstance):
    def __init__(self, fetch_origin, fetch_name: str) -> None:
        super().__init__()
        self._fetch_origin = fetch_origin
        self._fetch_name: str = fetch_name

        # Get last namespace as name to synchronize
        self.name: Optional[str] = self._fetch_name.split('/')[-1]
        if type(self.name) == int:
            self.name = None

    def __repr__(self) -> str:
        return f"DynamicVariable({self._fetch_name})"

    def evaluate_override(self):
        try:
            return self._fetch_origin[self._fetch_name]
        except Exception:
            raise KeyError(f"No given key exist from fetch_origin.\nRaised from {self}")

    def represent(self) -> str:
        return f'''<{self._fetch_name}>'''

    def get_next_nodes(self):
        return []


class DynamicVariableOperation(AbstractDynamicVariableInstance):
    def __init__(self, args, eval_func, repr_func, inheritted_namespace: Optional[str] = None) -> None:
        super(DynamicVariableOperation, self).__init__()
        self.inheritted_namespace: Optional[str] = inheritted_namespace
        self._args = args
        for arg in args:
            self.add_next_instance(arg)
        self._eval_func = eval_func
        self._repr_func = repr_func

    def evaluate_override(self) -> None:
        try:
            return self._eval_func(*self._args)
        except Exception as e:
            raise TypeError(f'''
            Evaluation failure, given argument {[x.assigned_namespace for x in self._args]}
            Evaluated value may be 
            {[x.evaluate() for x in self._args]}

            Check given arguments passed correctly.

            Original Error : {e}
            ''')

    def represent(self):
        return self._repr_func(self._args)

    @classmethod
    def wrap_argument(cls, arg):
        wrapped = DynamicConversionTool.wrap_non_dynamic_variable(arg)
        if wrapped is not None:
            return wrapped
        else:
            return arg

    @classmethod
    def reveal_argument(cls, arg):
        if isinstance(arg, DynamicVariableMimicingConstant):
            return arg._mimic_target_constant
        else:
            return arg

    @classmethod
    def wrap_arguments(cls, args: Iterable[Any]):
        return [cls.wrap_argument(a) for a in args]

    @staticmethod
    def create_ops(eval_func, repr_str, name: Optional[str] = None):
        def ops(*args) -> DynamicVariableOperation:
            wrapped_args = DynamicVariableOperation.wrap_arguments(args)
            return DynamicVariableOperation(wrapped_args, eval_func, repr_str, name)

        return ops

    @staticmethod
    def add(*args) -> 'DynamicVariableOperation':
        def add_func(*ops_args):
            li = [var.evaluate() for var in ops_args]
            sum_value = li[0]
            for v in li[1:]:
                sum_value += v
            return sum_value

        def add_repr(*ops_args):
            return "+".join([var.represent() for var in ops_args])

        return DynamicVariableOperation.create_ops(add_func, add_repr, 'add')(*args)

    @staticmethod
    def mult(a, b) -> 'DynamicVariableOperation':
        def add_func(_a, _b):
            return _a.evaluate() * _b.evaluate()

        def add_repr(_a, _b):
            return "*".join([var.represent() for var in [_a, _b]])

        return DynamicVariableOperation.create_ops(add_func, add_repr, 'mult')(a, b)

    @staticmethod
    def floor(a, b) -> 'DynamicVariableOperation':
        def add_func(_a, _b):
            return int(_a.evaluate() / _b.evaluate())

        def add_repr(_a, _b):
            return 'floor(' + ','.join([var.represent() for var in [_a, _b]]) + ')'

        return DynamicVariableOperation.create_ops(add_func, add_repr)(a, b)


class DynamicVariableInstance(AbstractDynamicVariableInstance):
    def __add__(self, arg) -> DynamicVariableOperation:
        return DynamicVariableOperation.add(self, arg)

    def __iadd__(self, arg) -> DynamicVariableOperation:
        return DynamicVariableOperation.add(self, arg)

    def __mul__(self, arg) -> DynamicVariableOperation:
        return DynamicVariableOperation.mult(self, arg)

    def __rmul__(self, arg) -> DynamicVariableOperation:
        return DynamicVariableOperation.mult(self, arg)


class DynamicVariableMimicingConstant(DynamicVariableInstance):
    def __init__(self, constant) -> None:
        super(DynamicVariableMimicingConstant, self).__init__()
        self._mimic_target_constant = constant

    def evaluate_override(self):
        return self._mimic_target_constant

    def represent(self):
        return str(self._mimic_target_constant)

    def get_next_nodes(self):
        return []


class AbstractGraphBuilder:
    def psuedo_building_sequence(self, storage: AbstractStorage = None) -> None:
        initialize_global_properties()
        if storage is not None:
            GlobalOperation.set_storage(storage)
        # Create graph
        # Build graph(Unstaged)
        GlobalOperation.assign_storage()
        GlobalOperation.attach_namespace()
        GlobalOperation.save_storage()
        GlobalOperation.convert_to_static()


def generate_graph_safely(graph_generator):
    initialize_global_properties()

    base_element, all_elements = graph_generator()

    GlobalOperation.assign_storage()
    GlobalOperation.attach_namespace()
    GlobalOperation.save_storage()

    GlobalOperation.convert_to_static()

    collection = GlobalOperation.export_collection()

    return base_element, all_elements, collection
