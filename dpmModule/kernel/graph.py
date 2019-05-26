from collections import defaultdict, Counter


class DynamicVariableTracker():
    def __init__(self, track_target):
        self._track_target = track_target
        self._recorded_variable = []

    def __enter__(self):
        self._recorded_variable = dir(self._track_target)

    def __exit__(self, type, value, traceback):
        final_variables = dir(self._track_target)
        tracked_result = Counter(final_variables) - Counter(self._recorded_variable)
        tracked_result = [var for var, i in tracked_result.most_common()]
        self.parse_variable(tracked_result)

    def parse_variable(self, tracked_result):
        raise NotImplementedError('Method not implemented DynamicVariableTracker.parse_variable')

class VariableObjectPrecursor(object):
    def __init__(self):
        self._variable_precursor_keyword = []   

    def add_precursor_keyword(self, keyword_list):
        self._variable_precursor_keyword += keyword_list

    def transfer_as_real(self):
        '''각각의 Object를 evaluate하여 실제 값을 각 속성에
        할당합니다. 이 시점에서 가상 DynamicVariableInstance와의 연결은 끊어집니다.

        '''
        for kwd in self._variable_precursor_keyword:
            setattr(self, kwd, getattr(self, kwd).evaluate())

    def assign_storage(self):
        '''각각의 Object에 값을 당겨올 수 있는 Storage를 할당합니다.
        '''

class EvaluativeGraphElement(VariableObjectPrecursor):
    class GraphElementTracker(DynamicVariableTracker):
        def parse_variable(self, tracked_result):
            self._track_target.add_precursor_keyword(tracked_result)

    def __init__(self):
        pass      

    def dynamic_range(self):
        return EvaluativeGraphElement.GraphElementTracker(self)

    def transfer_as_real(self):
        super(EvaluativeGraphElement, self).transfer_as_real()
        pass

class AbstractDiGraphElement():
    def __init__(self):
        self._next_instance_list = []
        self._prev_instance_list = []

    #Graph parsing methods
    def add_next_instance(self, instance):
        if instance not in self._next_instance_list:
            self._next_instance_list.append(instance)
        if self not in instance.get_next_instance():
            instance._prev_instance_list.append(self)

    def add_prev_instance(self, instance):
        if instance not in self._prev_instance_list:
            self._prev_instance_list.append(instance)
        if self not in instance.get_prev_instance():
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
        def output_func(instance, param, index):    
            rec_param = func(instance, param, index)
            for idx, inst in enumerate(instance.get_next_instances()):
                output_func(inst, rec_param, idx)

        return output_func


class AbstractDynamicVariableInstance(AbstractDiGraphElement):
    def __init__(self, name = None):
        super(AbstractDynamicVariableInstance, self).__init__()
        self._namespace = None
        self.name = name
        self.storage = None

    def evaluate_override(self):
        raise NotImplementedError('''
        Please implement AbstractDynamicVariableInstance.evaluate()
        You may trying to use Abstract Instance without recoginizing what
        are you doing. Please be aware what you are trying to do.
        ''')

    def evaluate(self):
        if self.storage is not None:
            if self.storage.has_namespace(self._namespace):
                return self.storage.get(self._namespace)

        return self.evaluate_override()

    def represent(self):
        raise NotImplementedError('''
        Please implement AbstractDynamicVariableInstance.represent()
        You may trying to use Abstract Instance without recoginizing what
        are you doing. Please be aware what you are trying to do.
        ''')

    def build_namespace(self, namespace, index):
        if self.name:
            self._namespace = '/'.join([namespace, self.name])
        else:
            self._namespace = '/'.join([namespace, str(index)])
        return self._namespace

    def get_next_nodes(self):
        raise NotImplementedError('''
        Please implement ABstractDynamicVariableInstance.get_nex_nodes()
        You may trying to use Abstract Instance without recoginizing what
        are you doing. Please be aware what you are trying to do.
        ''')

    def get_namespace(self):
        return self._namespace
    
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
    def reset_namespace(self, inst, param, index):
        inst._namespace = None
        return

    @AbstractDiGraphElement.recurrent_run
    def assign_storage(self, inst, storage, index):
        inst.storage = storage
        return storage

    @AbstractDiGraphElement.recurrent_run
    def save_storage(self, inst, storage, index):
        touch_end = len(inst.get_next_instances()) == 0
        storage.set_namespace(inst.get_namespace, inst.evaluate(),
                                                touch_end = touch_end)
        return storage

 
class DynamicVariableMimicingConstant(AbstractDynamicVariableInstance):
    def __init__(self, constant):
        self._mimic_target_constant = constant

    def evaluate(self):
        return self._mimic_target_constant

    def represent(self):
        return str(self._mimic_target_constant)

    def get_next_nodes(self):
        return []


class ConfigurationStorage():
    def __init__(self, dict_obj, allow_fetch = True):
        self._origin = dict_obj
        self._allow_fetch = allow_fetch

    def has_namespace(self, namespace):
        if self._allow_fetch:
            if namespace in self._origin :
                return True
        return False

    def get_namespace(self, namespace):
        return  self._origin[namespace]

    def set_namespace(self, namespace, value, touch_end = False, override = True):
        if namespace in self._origin and not override:
            return
        else:
            self._origin[namespace] = value

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

    def evaluate(self):
        return self._eval_func(*self._args, **self._kwargs)

    def represent(self):
        return self._repr_func(self._args)

    def get_next_nodes(self):
        return self._args

    @staticmethod
    def create_ops(eval_func, repr_str):
        def ops(*args):
            return DynamicVariableOperation(args, eval_func, repr_str)
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