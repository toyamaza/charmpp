

class Channel(object):

    qcd_template = None
    likelihood_fit = None
    scale_factors = None
    make_plots = True
    name = ""
    lumi = ""
    label = []
    add = []
    subtract = []
    samples = []

    def __init__(self, name, label, lumi, add, subtract=[], samples=[]):
        self.name = name
        self.lumi = lumi
        # label
        if type(label) == list:
            self.label = label
        elif type(label) == str:
            self.label = [label]
        # addition
        if type(add) == list:
            self.add = add
        elif type(add) == str:
            self.add = [add]
        # subtraction
        if type(subtract) == list:
            self.subtract = subtract
        elif type(subtract) == str:
            self.subtract = [subtract]
        # samples
        if type(samples) == list:
            self.samples = samples
        elif type(samples) == str:
            self.samples = [samples]

    def set_make_plots(self, make_plots):
        self.make_plots = make_plots

    def set_qcd_template(self, qcd_template):
        self.qcd_template = qcd_template

    def set_samples(self, samples):
        self.samples = samples

    def set_likelihood_fit(self, fit):
        self.likelihood_fit = fit

    def set_scale_factors(self, scale_factors):
        self.scale_factors = scale_factors

    def get_all(self):
        return self.add + self.subtract

    def __repr__(self):
        string = "+".join(self.add)
        for c in self.subtract:
            string += "-%s" % c
        return string
