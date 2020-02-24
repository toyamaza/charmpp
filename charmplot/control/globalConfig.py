
from charmplot.control import channel
from charmplot.control import colorScheme
from charmplot.control import sample
from charmplot.control import tools
from charmplot.control import variable
import logging
import os


logger = logging.getLogger(__name__)


class GlobalConfig(object):

    required_arguments = [
        'data',
        'samples',
        'channels',
    ]

    # global samples configuration
    samples_config = {}

    data = None
    samples = []
    channels = []

    def get_bottom_mc(self):
        return self.samples[-1]

    def get_mc(self):
        return self.samples

    def get_data(self):
        return self.data

    def get_data_and_mc(self):
        return [self.data] + self.samples

    def get_variables(self):
        return self.variables

    def get_variable_names(self):
        return [v for v in self.variables]

    def get_var(self, v):
        if v not in self.variables:
            self.variables[v] = variable.Variable(v)
        return self.variables[v]

    def parse_confing(self, conf):
        for arg in self.required_arguments:
            if arg not in conf:
                logger.critical("argument %s not found in config!" % arg)
                raise Exception("Invalid config")

        # color scheme
        color_scheme = getattr(colorScheme, conf['colorScheme'])
        style = color_scheme()
        print(style)

        # read data
        samp = self.samples_config[conf['data']]
        self.data = sample.Sample(conf['data'], **samp)

        # read variables
        variables = {}
        for name in self.variables_config:
            var = self.variables_config[name]
            v = variable.Variable(name, **var)
            variables[name] = v
        self.variables = variables

        # read samples
        samples = []
        for name in conf['samples']:
            samp = self.samples_config[name]
            s = sample.Sample(name, **samp)
            s.set_color_scheme(style)
            samples += [s]
        self.samples = samples

        # read channels
        channels = []
        for name, val in conf['channels'].items():
            regions = val['regions']
            label = val['label'] if 'label' in val else ''
            lumi = val['lumi'] if 'lumi' in val else 0
            if type(lumi) == int:
                lumi = str(lumi)
            if type(regions) == list:
                plus = []
                minus = []
                for c in regions:
                    if c.startswith("-"):
                        minus += [c[1:]]
                    else:
                        plus += [c]
                channels += [channel.Channel(name, label, lumi, plus, minus)]
            elif type(regions) == str:
                channels += [channel.Channel(name, label, lumi, regions)]
            else:
                logger.critical("unrecognized channel type for " % name)
                raise Exception("Invalid config")
        self.channels = channels

    def __init__(self, config_name):
        # analysis specific config
        conf = tools.parse_yaml(config_name)

        # global samples config
        assert 'samplesConf' in conf
        self.samples_config = tools.parse_yaml(os.path.join('samples', conf['samplesConf']))

        # global variables config
        assert 'variablesConf' in conf
        self.variables_config = tools.parse_yaml(os.path.join('variables', conf['variablesConf']))

        # parse config
        self.parse_confing(conf)
