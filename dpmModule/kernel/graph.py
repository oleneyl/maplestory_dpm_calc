from collections import defaultdict, Counter

'''
global properties

- unsafe_global_storage
- unsafe_channel_callback
- unsafe_global_namespace_do_not_access_direct
- unsafe_global_evaluative_graph_element_controls
'''
def initialize_global_properties():
    global unsafe_global_collection_do_not_access_direct
    unsafe_global_collection_do_not_access_direct = GlobalCollection()

def _unsafe_access_global_storage():
    global unsafe_global_collection_do_not_access_direct
    return unsafe_global_collection_do_not_access_direct

class NamespaceObject():
    def __init__(self, namespace = None):
        self.namespace = namespace
        self.inheritted_namespace = None
        self.assigned_namespace = None
    
    def inherit_namespace(self, namespace):
        self.inheritted_namespace = namespace

    def get_my_namespace(self, namespace_from_parent, index):
        if self.namespace:
            true_namespace = self.namespace
        else:
            if self.inheritted_namespace is None:
                true_namespace = '/'.join([namespace_from_parent, str(index)])
            else:
                true_namespace = '/'.join([namespace_from_parent, self.inheritted_namespace])
        self.assigned_namespace = true_namespace
        return true_namespace

    def get_assigned_namespace(self):
        if self.assigned_namespace is None:
            raise ValueError('No namespace was assigned yet')
        return self.assigned_namespace

class GlobalOperation():
    @classmethod
    def assign_storage(self):
        _unsafe_access_global_storage().assign_storage()

    @classmethod
    def save_storage(self):
        _unsafe_access_global_storage().save_storage()

    @classmethod
    def attach_namespace(self):
        _unsafe_access_global_storage().attach_namespace()

    @classmethod
    def convert_to_static(self):
        _unsafe_access_global_storage().convert_to_static()

    @classmethod
    def revert_to_dynamic(self):
        _unsafe_access_global_storage().revert_to_dynamic()

    @classmethod
    def notify_dynamic_object_added(self, obj):
        _unsafe_access_global_storage().add_dynamic_object(obj)

    @classmethod
    def export_collection(self):
        collection = _unsafe_access_global_storage()
        initialize_global_properties()
        return collection
    
    @classmethod
    def set_storage(self, storage):
        _unsafe_access_global_storage().set_storage(storage)


class GlobalCollection():
    historical_track_prefix = '_temporal_save_'
    def __init__(self):
        self._found_dynamic_object = []
        self._storage = DeepConfigurationStorage({})

    def set_storage(self, storage):
        self._storage = storage

    def add_dynamic_object(self, obj):
        self._found_dynamic_object.append(obj)
    
    def assign_storage(self):
        for obj in self._found_dynamic_object:
            for kwd in obj.get_dynamic_variables():
                getattr(obj, kwd).assign_storage_head(self._storage)

    def save_storage(self):
        for obj in self._found_dynamic_object:
            for kwd in obj.get_dynamic_variables():
                getattr(obj, kwd).save_storage_head(self._storage)
                
    def attach_namespace(self):
        for obj in self._found_dynamic_object:
            for kwd in obj.get_dynamic_variables():
                obj.attach_namespace()

    def convert_to_static(self):
        for obj in self._found_dynamic_object:       
            for kwd in obj.get_dynamic_variables():
                if not isinstance(getattr(obj, kwd), AbstractDynamicVariableInstance):
                    if not type(getattr(obj, kwd)) in [str, float, int, bool, type(None)]:
                        raise TypeError(f'''Trying to evaluate non - dynamic variable [{obj}({obj._namespace})/{kwd}] into static.
                        Tryed element type : {type(getattr(obj, kwd))}
                        This error was raised to prevent consistency problem.''')
                setattr(obj, self.historical_track_prefix + kwd, getattr(obj, kwd))
                setattr(obj, kwd, getattr(obj, kwd).evaluate())

    def revert_to_dynamic(self):
        for obj in self._found_dynamic_object:
            for kwd in obj.get_dynamic_variables():
                try:
                    setattr(obj, kwd, getattr(obj, self.historical_track_prefix + kwd))
                except AttributeError:
                    raise AttributeError('Cannot find saved object before evalute. Check whether you have had \
                        called convert_to_static()')


class DynamicVariableTracker():
    def __init__(self, track_target, callback = [], options = {}):
        self._track_target = track_target
        self._recorded_variable = []
        self._callback = callback
        self.options = options

    def __enter__(self):
        self._recorded_variable = dir(self._track_target)

    def __exit__(self, type, value, traceback):
        final_variables = dir(self._track_target)
        tracked_result = Counter(final_variables) - Counter(self._recorded_variable)
        tracked_result = [var for var, i in tracked_result.most_common()]
        self.parse_variable(tracked_result)

    def parse_variable(self, tracked_result):
        raise NotImplementedError('Method not implemented DynamicVariableTracker.parse_variable')
   

class AbstractDiGraphElement(NamespaceObject):
    def __init__(self, namespace = None):
        super(AbstractDiGraphElement, self).__init__(namespace=namespace)
        self._next_instance_list = []
        self._prev_instance_list = []

    #Graph parsing methods
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
        '''This function is decorator.
        Use this method to func(instance, param, index) -> action, return recursive param
        '''
        def output_func(self, instance, param, index):    
            rec_param = func(self, instance, param, index)
            for idx, inst in enumerate(instance.get_next_instances()):
                output_func(self, inst, rec_param, idx)

        return output_func


class AbstractDynamicVariableInstance(AbstractDiGraphElement):
    def __init__(self, namespace = None):
        super(AbstractDynamicVariableInstance, self).__init__(namespace=namespace)
        self.storage = None

    def evaluate_override(self):
        raise NotImplementedError('''
        Please implement AbstractDynamicVariableInstance.evaluate()
        You may trying to use Abstract Instance without recoginizing what
        are you doing. Please be aware what you are trying to do.
        ''')

    def evaluate(self):
        if self.storage is not None:
            if self.storage.has_namespace(self.assigned_namespace):
                return self.storage.get_namespace(self.assigned_namespace)

        return self.evaluate_override()

    def represent(self):
        raise NotImplementedError('''
        Please implement AbstractDynamicVariableInstance.represent()
        You may trying to use Abstract Instance without recoginizing what
        are you doing. Please be aware what you are trying to do.
        ''')

    def build_namespace(self, namespace, index):
        my_namespace = self.get_my_namespace(namespace, index)
        return my_namespace
        
    def get_next_nodes(self):
        raise NotImplementedError('''
        Please implement ABstractDynamicVariableInstance.get_next_nodes()
        You may trying to use Abstract Instance without recoginizing what
        are you doing. Please be aware what you are trying to do.
        ''')
    
    def finalize(self, storage):
        if self._already_finalized:
            return
        else:
            if hasattr(self, '_finalizing_action'):
                self._finalizing_action(storage)
            self._already_finalized = True
            map(lambda x:x.finalize(), self.get_next_nodes())

    def initialize_finalized_state(self):
        if self._already_finalized:
            self._already_finalized = False
            map(lambda x:x.reset_finalized_variable(), self.get_next_nodes())

    @AbstractDiGraphElement.recurrent_run
    def attach_namespace(self, inst, namespace, index):
        my_namespace = inst.build_namespace(namespace, index)
        return my_namespace

    @AbstractDiGraphElement.recurrent_run
    def assign_storage(self, inst, storage, index):
        inst.storage = storage
        return storage

    @AbstractDiGraphElement.recurrent_run
    def save_storage(self, inst, storage, index):
        touch_end = len(inst.get_next_instances()) == 0
        storage.set_namespace(inst.get_assigned_namespace(), inst.evaluate(),
                                                touch_end = touch_end)
        return storage

    def attach_namespace_head(self, namespace):
        self.attach_namespace(self, namespace, 0)

    def save_storage_head(self, storage):
        self.save_storage(self, storage, 0) 

    def assign_storage_head(self, storage):
        self.assign_storage(self, storage, 0)

class DynamicConversionTool():
    '''CONVERT_ATTR is a hint, that converts non - dynamic instance into
    dynamic instance automatically. Without this hint, unknown element will
    emit WARNING that program can cause data consistancy error.

    You can define your custom object with CONVERT_ATTR as a instance method name.
    In that function, you must write as below ::
    (1) Write how to convert element if element is not a dynamic variable.
    (2) if given element is already dynamic, make method return None.
    '''
    CONVERT_ATTR = '_dynamic_variable_hint'
    @classmethod
    def wrap_non_dynamic_variable(self, target):
        ret_target = target
        if not isinstance((target), AbstractDynamicVariableInstance):
            if not type(target) in [str, float, int, bool, type(None)]:
                if hasattr(target, DynamicConversionTool.CONVERT_ATTR):
                    return getattr(target, DynamicConversionTool.CONVERT_ATTR)(target)
                else:
                    print(f'''Warning : Trying to convert none - static variable {target} into MimicDynamicVariable. This can
                    raise consistency problem.''')
            return DynamicVariableMimicingConstant(ret_target)
        else:
            return None
    

class DynamicObject(object):
    def __init__(self, namespace = None):
        self._variable_precursor_keyword = []   
        self.namespace = namespace
        GlobalOperation.notify_dynamic_object_added(self)

    def add_precursor_keyword(self, keyword_list):
        
        filtered_keywords = []
        #Force tracked keywords as Dynamic Variable
        for kwd in keyword_list:
            #to prevent recurrent cascaded DynamicObject, DynamicObject will be tracked only once.
            if isinstance(getattr(self, kwd), DynamicObject): continue   
            wrapped = DynamicConversionTool.wrap_non_dynamic_variable(getattr(self, kwd))  
            if wrapped is not None:
                setattr(self, kwd, wrapped) #Force attribute convert into Dynamic
            filtered_keywords.append(kwd)
        self._variable_precursor_keyword += filtered_keywords

    def get_dynamic_variables(self):
        return self._variable_precursor_keyword

    def attach_namespace(self):
        for kwd in self._variable_precursor_keyword:
            var = getattr(self, kwd)
            var.inherit_namespace(kwd)
            var.attach_namespace_head(self.namespace)
            #getattr(obj, kwd).attach_namespace_head('/'.join([obj.namespace,kwd]))

class EvaluativeGraphElement(DynamicObject):
    class GraphElementTracker(DynamicVariableTracker):
        def parse_variable(self, tracked_result):
            self._track_target.add_precursor_keyword(tracked_result)
            
    def __init__(self, namespace = None):
        super(EvaluativeGraphElement, self).__init__(namespace=namespace)

    def dynamic_range(self, options = {}):
        return EvaluativeGraphElement.GraphElementTracker(self, options = options)


class AbstactStorage():
    def __init__(self, allow_fetch = True, override = True):
        self._allow_fetch = allow_fetch
        self.override = override
    
    def has_namespace(self, namespace : str) -> bool:
        raise NotImplementedError('''has_namespace function call
        will return whether value exist in given namespace.
        ''')
    
    def get_namespace(self, namespace : str) -> AbstractDynamicVariableInstance:
        raise NotImplementedError('''get_namespace function call 
        will return value in given namespace.''')

    def set_namespace(self, namespace : str, value, touch_end : bool = False):
        raise NotImplementedError('''set_namespace function call
        will set given DynamicVariable into given namespace.

        Options::
        touch_end(bool) : if True, only return value if given namespace is 'End of tree', which means
        there is no other namespace under given namespace.

        ''')


class ConfigurationStorage(AbstactStorage):
    def __init__(self, dict_obj, allow_fetch = True, override = True):
        super(ConfigurationStorage, self).__init__(allow_fetch = allow_fetch, override = override)
        self._origin = dict_obj
        

    def has_namespace(self, namespace):
        if self._allow_fetch:
            if namespace in self._origin :
                return True
        return False

    def get_namespace(self, namespace):
        return  self._origin[namespace]

    def set_namespace(self, namespace, value, touch_end = False):
        if namespace in self._origin and not self.override:
            return
        else:
            self._origin[namespace] = value

class DeepConfigurationStorage(AbstactStorage):
    DATA_KEYWORD = '_data_keyword_'
    def __init__(self, key_value_map, allow_fetch = True, override = True):
        super(DeepConfigurationStorage, self).__init__(allow_fetch = allow_fetch, override = override)
        self.space_generator = dict
        self._origin = self.space_generator()

    def parse_namespace_to_address(self, namespace):
        return namespace.split('/')

    def get_variable_by_address(self, address):
        position = self._origin
        for kwd in address:
            try:
                position = position[kwd]
            except:
                raise KeyError(f'Given address {"/".join(address)} not exist in storage')
        return position[DeepConfigurationStorage.DATA_KEYWORD]
    
    def save_variable_by_address(self, address, variable):
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

    def has_namespace(self, namespace):
        address = self.parse_namespace_to_address(namespace)
        position = self._origin
        for kwd in address:
            if kwd not in position:
                return False
            else:
                position = position[kwd]
        return (DeepConfigurationStorage.DATA_KEYWORD in position)

    def get_namespace(self, namespace):
        address = self.parse_namespace_to_address(namespace)
        return self.get_variable_by_address(address)

    def set_namespace(self, namespace, value, touch_end = False):
        address = self.parse_namespace_to_address(namespace)
        self.save_variable_by_address(address, value)


class DynamicVariableFromConfigurationStorage(AbstractDynamicVariableInstance):
    def __init__(self, fetch_origin, fetch_name):
        self._fetch_origin = fetch_origin
        self._fetch_name = fetch_name

        #Get last namespace as name to synchronize
        self.name = self._fetch_name.split('/')[-1]
        if type(self.name) == int:
            self.name = None

    def __repr__(self):
        return f"DynamicVariable({self._fetch_name})"

    def evaluate(self):
        try:
            return self._fetch_origin[self._fetch_name]
        except:
            raise KeyError(f"No given key exist from fetch_origin.\nRaised from {self}")

    def represent(self):
        return f'''<{self._fetch_name}>'''

    def get_next_nodes(self):
        return []

class DynamicVariableOperation(AbstractDynamicVariableInstance):
    def __init__(self, args, eval_func, repr_func):
        self._args = args
        self._eval_func = eval_func
        self._repr_func = repr_func

    def evaluate_override(self):
        return self._eval_func(*self._args)

    def represent(self):
        return self._repr_func(self._args)

    def get_next_nodes(self):
        return self._args

    @classmethod
    def wrap_argument(self, arg):
        wrapped = DynamicConversionTool.wrap_non_dynamic_variable(arg)
        if wrapped is not None:
            return wrapped
        else:
            return arg
        
    @classmethod
    def wrap_arguments(self, args : list):
        return [self.wrap_argument(a) for a in args]

    @staticmethod
    def create_ops(eval_func, repr_str):
        def ops(*args):
            wrapped_args = DynamicVariableOperation.wrap_arguments(args)
            return DynamicVariableOperation(wrapped_args, eval_func, repr_str)
        return ops
    
    @staticmethod
    def add(*args):
        def add_func(*ops_args):
            return sum([var.evaluate() for var in ops_args])
        def add_repr(*ops_args):
            return "+".join([var.represent() for var in ops_args])
        return DynamicVariableOperation.create_ops(add_func, add_repr)(*args)

    @staticmethod
    def mult(a, b):
        def add_func(a, b):
            return a.evaluate() * b.evaluate()
        def add_repr(a, b):
            return "*".join([var.represent() for var in [a,b]])
        return DynamicVariableOperation.create_ops(add_func, add_repr)(a, b)

    @staticmethod
    def floor(a, b):
        def add_func(a, b):
            return int(a.evaluate() / b.evaluate())
        def add_repr(a, b):
            return 'floor('+','.join([var.represent() for var in [a,b]]) + ')'
        return DynamicVariableOperation.create_ops(add_func, add_repr)(a, b)

class DynamicVariableInstance(AbstractDynamicVariableInstance, object):
    def __add__(self, arg):
        return DynamicVariableOperation.add(self, arg)

    def __mul__(self, arg):
        return DynamicVariableOperation.mult(self, arg)

    def __rmul__(self, arg):
        return DynamicVariableOperation.mult(self, arg)


class DynamicVariableMimicingConstant(DynamicVariableInstance):
    def __init__(self, constant):
        super(DynamicVariableMimicingConstant, self).__init__()
        self._mimic_target_constant = constant

    def evaluate_override(self):
        return self._mimic_target_constant

    def represent(self):
        return str(self._mimic_target_constant)

    def get_next_nodes(self):
        return []

class AbstractGraphBuilder():
    def psuedo_building_sequence(storage = None):
        initialize_global_properties()
        if storage is not None:
            GlobalOperation.set_storage(storage)
        #Create graph
        #Build graph(Unstaged)
        GlobalOperation.assign_storage()
        GlobalOperation.attach_namespace()
        GlobalOperation.save_storage()
        GlobalOperation.convert_to_static()