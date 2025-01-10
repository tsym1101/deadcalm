# -*- coding: utf-8 -*-
import dutil
import version
from global_config import g_config

from parameter import factory
from parameter.panel import Panel
from client import param_widgets_bastion

appLabel = 'load deadcalm v' + version.versionStr
dutil.logInfo(appLabel.center(48, '*'))
global_config.loadCustomConfig()
dutil.debug_level = g_config.debug_level

Panel.param_widgets = dict(factory.param_widgets, **param_widgets_bastion.param_widgets)
