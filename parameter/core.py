# -*- coding: utf-8 -*-

import json
import copy

class ParameterEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Parameter):
            return {'data':o.__dict__['data']}
            # return o.__dict__
        return super(Parameter, self).default(o)

class Parameter:
    def __init__(self,data,
                 widget='lineedit',
                 visble=True,
                 editable=True,
                 alias='',
                 category='default',
                 label=True,
                 **kwargs):
        self.name = ''
        self.alias = alias
        self.data = data
        self.visible = visble
        self.editable = editable
        self.category = category
        self.widget = widget
        self.label = label

        self.kwargs = kwargs

    def __repr__(self):
        return '(name:{},data:{})'.format(self.name,str(self.data))

    def type(self):
        return type(self.data)

class ParamSet(object):
    def __init__(self):
        self.params_ = []

    def __setattr__(self, key, value):

        if isinstance(value,Parameter):
            self.params_.append(key)
            value.name = key
        else:
            if isinstance(self.__dict__.get(key), Parameter):
                self.__dict__[key].data = value
                return

        super(ParamSet, self).__setattr__(key,value)

    def __getattribute__(self, name):

        this = super(ParamSet, self).__getattribute__(name)
        if isinstance(this,Parameter):
            #
            # if name == 'option':
            #     assert not str(this.data) == '[None]', 'invalid option'

            return this.data
        return this

    def param(self,name):
        param = self.__dict__[name]
        assert isinstance(param,Parameter), 'not a parameter : {}'.format(name)
        return param

    def params(self):
        result = []
        for name in self.params_:
            result.append(self.__dict__[name])
        return result

    def setVisible(self,name,visible):
        self.__dict__[name].visible=visible

    def hideAll(self):
        for p in self.params():
            p.visible = False

    def dumps(self):
        tmp = copy.deepcopy(self.__dict__)
        del tmp["params_"]
        j = json.dumps(tmp, indent=2, cls=ParameterEncoder)
        return j

if __name__ == '__main__':

    p = Parameter('aaa',widget='lineedit',min=100,max=500,visble=False)
    print(p.kwargs)
    print(p)
    print(p.visible)
