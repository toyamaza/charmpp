#!/usr/bin/env python
from charmplot.common import utils
from charmplot.common import www
from charmplot.control import globalConfig
from charmplot.control import inputDataReader
from copy import deepcopy
import logging
import os
import ROOT
import sys

# ATLAS Style
dirname = os.path.join(os.path.dirname(__file__), "../../atlasrootstyle")
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.LoadMacro(os.path.join(dirname, "AtlasStyle.C"))
ROOT.SetAtlasStyle()

# logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


def main(options, conf, reader):

    # extra channel
    if options.extra_channel:
        cextra = conf.get_channel(options.extra_channel)
        sextra = []
        for s in cextra.samples:
            if "Loose" in conf.get_sample(s).name:
                sextra += [deepcopy(conf.get_sample(s))]
                sextra[-1].lineColor = ROOT.kRed

    # loop through all channels and variables
    for c in conf.channels:

        # filter channels
        if options.channels:
            if c.name not in options.channels.split(","):
                logging.debug(f"skipping channel {c.name}")
                continue

        # skip channels
        if not c.make_plots:
            continue

        # output root file
        if c.save_to_file:
            out_file_name = os.path.join(conf.out_name, f"histograms_{c.name}.root")
            out_file = ROOT.TFile(out_file_name, "RECREATE")
            out_file.Close()

        # keep track of first/last plot of each channel
        first_plot = True

        # samples
        if not c.samples:
            logging.critical(f"no samples given for channel {c}")
            sys.exit(1)
        samples = [conf.get_sample(s) for s in c.samples if "Loose" not in s]
        logging.info(f"making plots for channel {c} with samples {samples}")

        # list of variables
        variables = utils.get_variables(options, conf, reader, c, samples[0])

        # make channel folder if not exist
        if not os.path.isdir(os.path.join(conf.out_name, c.name)):
            os.makedirs(os.path.join(conf.out_name, c.name))
        for v in variables:

            # check if last plot
            last_plot = v == variables[-1]

            # variable object
            var = conf.get_var(v)

            # mc map
            mc_map = {s: reader.get_histogram(s, c, var) for s in samples}
            if options.extra_channel:
                mc_map_extra = {s: reader.get_histogram(s, cextra, var, suffix=c.name) for s in sextra}
                mc_map.update(mc_map_extra)
                samples = sextra + samples

            # canvas
            yaxis_label = "Entries"
            if not options.normalize:
                yaxis_label = "Normalized Entries"
            canv = utils.make_canvas_mc_ratio(mc_map[samples[0]], var, c, ratio_title=options.ratio_title, x=800, y=800,
                                              events=yaxis_label, ratio_range=[0.01, 1.99])

            # configure histograms
            canv.configure_histograms(mc_map, options.normalize)

            # save histograms to root file
            if c.save_to_file:
                utils.save_to_file(out_file_name, c, var, None, mc_map)

            # top pad
            errors = []
            canv.pad1.cd()
            for s in samples:
                fcolor = mc_map[s].GetLineColor()
                gr_mc_stat_err, _ = utils.make_stat_err(mc_map[s])
                gr_mc_stat_err.SetLineColor(fcolor)
                gr_mc_stat_err.SetFillColorAlpha(fcolor, 0.25)
                gr_mc_stat_err.SetFillStyle(1001)
                errors += [gr_mc_stat_err]
                gr_mc_stat_err.Draw("e2")
                mc_map[s].Draw("hist same")

            # make legend
            canv.make_legend(mc_map, samples, print_yields=True)

            # set maximum after creating legend
            canv.set_maximum([mc_map[s] for s in samples], var, mc_map[samples[0]])

            # find minimum
            if options.nology:
                min_negative = {}
                for s in samples:
                    if s not in mc_map:
                        continue
                    h = mc_map[s]
                    for i in range(1, h.GetNbinsX() + 1):
                        if h.GetBinContent(i) < 0:
                            if i not in min_negative:
                                min_negative[i] = 0
                            min_negative[i] += h.GetBinContent(i)
                if min_negative.values():
                    min_negative = min(min_negative.values())
                    canv.proxy_up.SetMinimum(min_negative)
                    canv.proxy_up.SetMaximum(max(abs(min_negative), canv.proxy_up.GetMaximum()))

            # bottom pad
            canv.pad2.cd()

            # ratio histograms
            ratios = []
            denominator = mc_map[samples[0]].Clone(f"{mc_map[samples[0]].GetName()}_denominator")
            for i in range(0, denominator.GetNbinsX() + 2):
                denominator.SetBinError(i, 0)
            for i in range(0, len(samples)):
                h = mc_map[samples[i]].Clone(f"{mc_map[samples[i]].GetName()}_ratio")
                if options.extra_channel:
                    if "Loose" not in samples[i].shortName:
                        chi2 = h.Chi2Test(denominator, "WW")
                        canv.add_text(f"#chi^{2} prob: {chi2:.2f}")
                        canv.pad2.cd()
                h.Divide(denominator)
                ratios += [h]
                fcolor = mc_map[samples[i]].GetLineColor()
                gr_mc_stat_err, _ = utils.make_stat_err(h)
                gr_mc_stat_err.SetLineColor(fcolor)
                gr_mc_stat_err.SetFillColorAlpha(fcolor, 0.25)
                gr_mc_stat_err.SetFillStyle(1001)
                errors += [gr_mc_stat_err]
                gr_mc_stat_err.Draw("e2")
                h.Draw("hist same")
                if c.save_to_file:
                    out_file = ROOT.TFile(out_file_name, "UPDATE")
                    out_file.cd()
                    h.Write(f"{samples[i].shortName}_{c.name}_{var.name}_ratio")
                    if var.name == "Dmeson_pt":
                        func = ROOT.TF1(f"{samples[i].shortName}_{c.name}_{var.name}_ratio_func", "pol5", 8, 98)
                        h.Fit(func, "0WR")
                        func.Write()
                    out_file.Close()
            # for i in range(0, len(samples), 2):
            #     h = mc_map[samples[i]].Clone(f"{mc_map[samples[i]].GetName()}_ratio")
            #     h.Divide(mc_map[samples[i + 1]])
            #     ratios += [h]
            #     fcolor = mc_map[samples[i]].GetLineColor()
            #     gr_mc_stat_err, _ = utils.make_stat_err(h)
            #     gr_mc_stat_err.SetLineColor(fcolor)
            #     gr_mc_stat_err.SetFillColorAlpha(fcolor, 0.25)
            #     gr_mc_stat_err.SetFillStyle(1001)
            #     errors += [gr_mc_stat_err]
            #     gr_mc_stat_err.Draw("e2")
            #     h.Draw("hist same")

            # Print out
            canv.print_all(conf.out_name, c.name, v, multipage_pdf=True, first_plot=first_plot, last_plot=last_plot, as_png=options.stage_out, logy=(not options.nology))
            first_plot = False

        # close output file
        if c.save_to_file:
            out_file.Close()


if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()

    # ----------------------------------------------------
    # arguments
    # ----------------------------------------------------
    parser.add_option('-a', '--analysis-config',
                      action="store", dest="analysis_config",
                      help="analysis config file")
    parser.add_option('-c', '--channels',
                      action="store", dest="channels",
                      help="run over a subset of channels (comma separated)")
    parser.add_option('-v', '--vars',
                      action="store", dest="vars",
                      help="run over a subset of variables (comma separated)")
    parser.add_option('--suffix',
                      action="store", dest="suffix",
                      help="suffix for the output name")
    parser.add_option('-n', '--normalize',
                      action="store_true", dest="normalize",
                      help="normalize to luminosity")
    parser.add_option('-t', '--ratio-title',
                      action="store", dest="ratio_title",
                      default="Ratio",
                      help="title of the ratio")
    parser.add_option('-e', '--extra-channel',
                      action="store", dest="extra_channel",
                      help="overlay an extra channel on all plots")
    parser.add_option('--stage-out',
                      action="store_true", dest="stage_out",
                      help="copy plots to the www folder")
    parser.add_option('--nology',
                      action="store_true", dest="nology",
                      help="no log-y plots")

    # parse input arguments
    options, args = parser.parse_args()

    # analysis configs
    config = options.analysis_config

    # output name
    out_name = config.replace(".yaml", "").replace(".yml", "")
    if options.suffix:
        out_name = out_name.split("/")
        if out_name[0] != ".":
            out_name[0] += "_" + options.suffix
            out_name = "/".join(out_name)
        else:
            out_name[1] += "_" + options.suffix
            out_name = "/".join(out_name)

    # config object
    conf = globalConfig.GlobalConfig(config, out_name)

    # make output folder if not exist
    if not os.path.isdir(out_name):
        os.makedirs(out_name)

    # read inputs
    reader = inputDataReader.InputDataReader(conf)

    # do the plotting
    main(options, conf, reader)

    # stage-out to the www folder
    if options.stage_out:
        www.stage_out_plots(options.analysis_config, conf.get_variables(), x=300, y=300)
