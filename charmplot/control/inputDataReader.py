import logging
import ROOT


from charmplot.common import utils


logger = logging.getLogger(__name__)


class InputDataReader(object):

    # one input file for each sample
    input_files = {}
    channel_scale_factors = None

    def __init__(self, conf=None):
        self.config = conf
        self.read_input_files()

    def get_histogram_from_file(self, f, channel, sample, variable, c, extra_rebin=1, sys=None):
        logger.debug(f"In get_histogram_from_file with {f.GetName()} {channel.name} {sample.name}")
        # logger.debug(f"In get_histogram_from_file with {channel.name} {sample.name} {variable} {c} {f} extra_rebin: {extra_rebin}")
        h_name = "__".join([c, variable.name])
        h = None
        if sys:
            h_name_sys = "_-_".join([sys, "__".join([c, variable.name])])
            h = f.Get(h_name_sys)
            if not h:
                logger.warning(f"Systematic histogram with name {h_name_sys} not found! Using nominal instead.")
        if not h:
            h = f.Get(h_name)
        if not h:
            logger.warning(f"Histogram {h_name} not found for sample {sample}!")
            return None
        if sys:
            h = h.Clone(f"{h.GetName()}_{sys}_{f.GetName().replace('.root', '')}")
        else:
            h = h.Clone(f"{h.GetName()}_{f.GetName().replace('.root', '')}")
        h_new = utils.rebin_histogram(h, variable, extra_rebin)
        logger.info(f"Got histogram {h_new}")

        # scale histogram
        scale_factors = utils.read_scale_factors(self.channel_scale_factors)
        self.scale_histogram(h_new, sample, c, scale_factors)

        # scaling from MC config
        if sample.scaleMC and 'data' not in f.GetName():
            h_new.Scale(sample.scaleMC)
        return h_new

    def scale_histogram(self, h, sample, channel, scale_factors):
        # scale histogram if given input scale factors
        if scale_factors:
            sf = [1., 0.]
            logger.info(f"s.shortName: {sample.shortName} {channel}")
            for s in self.channel_scale_factors['scale_factors']:
                sample_channel = s.split(" | ")
                if len(sample_channel) == 2 and sample_channel[1] not in channel:
                    continue
                if sample.shortName == sample_channel[0]:
                    if self.channel_scale_factors['scale_factors'][s] in scale_factors.keys():
                        sf = scale_factors[self.channel_scale_factors['scale_factors'][s]]
            h.Scale(sf[0])
            logger.info(f"Scaling histogram {sample.name} in {channel} by {sf[0]}")

    def eff_divide(self, h_num, h_den):
        quot = h_num.Clone()
        quot.Divide(h_den)
        for i in range(h_num.GetNbinsX()):
            k = h_num.GetBinContent(i)
            n = h_den.GetBinContent(i)
            print(str(k) + ", " + str(n))
            if n > 0:
                quot.SetBinError(i, pow(k * (n - k) / (n**3), .5))
            else:
                quot.SetBinError(i, 0.0)
        return quot

    def get_histogram(self, sample, channel, variable, force_positive=False, sys=None):
        h_total = None
        h_denom = None
        # scale factors for this channel
        self.channel_scale_factors = channel.scale_factors
        extra_rebin = channel.extra_rebin
        if sample.channel:
            logging.info(f"Using channel {sample.channel} for sample {sample.name}")
            channel = self.config.get_channel(sample.channel)
        for input_file in sample.get_all():
            if input_file in sample.add:
                weight = 1.
            elif input_file in sample.subtract:
                weight = -1.
            if input_file not in self.input_files:
                logger.critical("No input file found for sample %s", sample.name)
                raise IOError("No input file found for sample %s", sample.name)
            f = self.input_files[input_file]
            for c in channel.add:
                logger.info(f"channel.add: {c} {sample.shortName}")
                h = self.get_histogram_from_file(f, channel, sample, variable, c, extra_rebin, sys)
                if not h:
                    continue
                if not h_total:
                    h_total = h.Clone("%s_%s_%s" % (sample.name, channel.name, variable.name))
                else:
                    h_total.Add(h, weight)
            for c in channel.subtract:
                logger.info(f"channel.subtract: {c} {sample.shortName}")
                h = self.get_histogram_from_file(f, channel, sample, variable, c, extra_rebin, sys)
                if not h:
                    continue
                if not h_total:
                    return None
                h_total.Add(h, -1 * weight)
            for c in channel.divide:
                print("Division occurs")
                logger.info(f"channel.divide: {c} {sample.shortName}")
                h = self.get_histogram_from_file(f, channel, sample, variable, c, extra_rebin)
                if not h:
                    continue
                if not h_denom:
                    h_denom = h.Clone("%s_%s_%s" % (sample.name, channel.name, variable.name))
                else:
                    h_denom.Add(h, weight)
        if force_positive:
            utils.set_to_positive(h_total)
        if not sample.statError:
            logger.info(f"Set stat error of {sample} to zero.")
            for i in range(0, h_total.GetNbinsX() + 2):
                h_total.SetBinError(i, 0)
        if h_denom:
            h_total = self.eff_divide(h_total, h_denom)
        return h_total

    def find_variables(self, sample, channel):
        all_vars = set()
        for input_file in sample.get_all():
            if input_file not in self.input_files:
                logger.critical("No input file found for sample %s: %s" % (sample.name, input_file))
                raise IOError("No input file found for sample %s: %s" % (sample.name, input_file))
            f = self.input_files[input_file]
            variables = {}
            for c in channel.get_all():
                logger.info(f"channel: {c}")
                for key in f.GetListOfKeys():
                    name = key.GetName()
                    var_name = name
                    if name.startswith(c):
                        var_name = var_name[len(c):]
                        while var_name.startswith("_"):
                            var_name = var_name[1:]
                        if var_name not in variables:
                            variables[var_name] = 1
                        else:
                            variables[var_name] += 1
            for var in variables:
                if variables[var] == len(channel.get_all()):
                    all_vars.add(var)
        return all_vars

    def read_input_files(self):
        for s in self.config.get_data_and_mc():
            for input_file in s.get_all():
                if input_file in self.input_files:
                    continue
                f = ROOT.TFile("%s.root" % input_file, "READ")
                if not f:
                    logger.critical("No input file found for sample %s", s.name)
                    raise IOError("No input file found for sample %s", s.name)
                else:
                    logger.info("Successfully read input file for sample %s", s.name)
                    self.input_files[input_file] = f
