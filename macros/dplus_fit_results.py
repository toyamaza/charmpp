#!/usr/bin/env python
import os
import ROOT

# ATLAS Style
dirname = os.path.join(os.path.dirname(__file__), "../atlasrootstyle")
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.LoadMacro(os.path.join(dirname, "AtlasStyle.C"))
ROOT.gROOT.LoadMacro(os.path.join(dirname, "AtlasLabels.C"))
ROOT.gROOT.LoadMacro(os.path.join(dirname, "AtlasUtils.C"))
ROOT.SetAtlasStyle()

# POI names
POIs_default = ["mu_Rc", "mu_Wminus_tot"] + [f"mu_Wminus_rel_{i}" for i in range(1, 5)] + [f"mu_Wplus_rel_{i}" for i in range(1, 5)]
POIs_default2 = ["mu_Wplus_tot", "mu_Wminus_rel_5", "mu_Wplus_rel_5"]
POIs_abs = [f"mu_Wminus_{i}" for i in range(1, 6)] + [f"mu_Wplus_{i}" for i in range(1, 6)]

# make output folder
if not os.path.isdir("fit_results"):
    os.makedirs("fit_results")


# extract POIs from txt file
def extract_pois(file):
    POIs = {}
    with open(file) as f:
        for line in f:
            res = line.split()
            if not len(res):
                continue
            name = res[0]
            if "mu_" in name:
                POIs[name] = res[1:]
    return POIs


def createCanvasPads(name):
    c = ROOT.TCanvas(name, name, 1200, 1200)
    # Upper histogram plot is pad1
    pad1 = ROOT.TPad(f"pad1_{name}", f"pad1_{name}", 0, 0.45, 1, 1.0)
    pad1.SetTopMargin(0.1)
    pad1.SetBottomMargin(0.05 / 0.55)
    pad1.SetFillStyle(4000)
    pad1.Draw()
    # Middle ratio plot is pad2
    c.cd()
    pad2 = ROOT.TPad(f"pad2_{name}", f"pad2_{name}", 0, 0.25, 1, 0.55)
    pad2.SetTopMargin(0.05 / 0.30)
    pad2.SetBottomMargin(0.05 / 0.30)
    pad2.SetFillStyle(4000)
    pad2.Draw()
    # Lower ratio plot is pad3
    c.cd()
    pad3 = ROOT.TPad(f"pad3_{name}", f"pad3_{name}", 0, 0.00, 1, 0.35)
    pad3.SetTopMargin(0.05 / 0.35)
    pad3.SetBottomMargin(0.10 / 0.35)
    pad3.SetFillStyle(4000)
    pad3.Draw()

    return c, pad1, pad2, pad3


def main(options, args):

    trash = []

    # # cross section priors
    # DIR_PRIORS = "/global/cfs/cdirs/atlas/wcharm/charmplot_output/Dmeson_2022_06_15/"

    # theory predictions
    DIR_THEORY = "/global/cfs/cdirs/atlas/wcharm/Rivet/v1/processed4"

    # observables
    OBSERVABLES = {
        "pt": {
            # "fit_results": "/global/cfs/cdirs/atlas/wcharm/TRExFitter/Output/Dplus_2022_07_26/",
            "fit_results": "/global/cscratch1/sd/mmuskinj/TRExFitter/fit_2022_12_14_Dplus_new",
            "label": "#it{p}_{T}^{#it{D}}",
            "prior_var": "D_pt_fit",
            "bins": [8, 12, 20, 40, 80, 120],
            "logx": True,
            "unit": "GeV",
        },
        "eta": {
            # "fit_results": "/global/cfs/cdirs/atlas/wcharm/TRExFitter/Output/Dplus_2022_07_26/",
            "fit_results": "/global/cscratch1/sd/mmuskinj/TRExFitter/fit_2022_12_14_Dplus_new",
            "label": "#||{#eta(#it{l})}",
            "prior_var": "D_differential_lep_eta",
            "bins": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5],
            "logx": False,
        },
    }

    # theory prediction style
    THEORY_DICT = {
        "Generator_comparison": {
            "Sherpa2211_0to5": {
                "lineColor": ROOT.kRed + 4,
                "fillColor": ROOT.kRed,
                "markerStyle": 24,
                "markerStyle2": 20,
                "markerScale": 1.0,
                "legendLabel": "Sh2.2.11^{0to5}, diag. CKM, NNPDF30",
                "legendLabelFull": "Sh2.2.11^{0to5}, diag. CKM, NNPDF30",
                "offset": -1 + 1 * (2 / 5.),
            },
            "Sherpa2211_0to2": {
                "lineColor": ROOT.kRed + 3,
                "fillColor": ROOT.kRed - 9,
                "markerStyle": 42,
                "markerStyle2": 43,
                "markerScale": 1.0,
                "legendLabel": "Sh2.2.11^{0to2}, diag. CKM, NNPDF30",
                "legendLabelFull": "Sh2.2.11^{0to2}, diag. CKM, NNPDF30",
                "offset": -1 + 2 * (2 / 5.),
            },
            "MGPy8EG_A14NNPDF23LO": {
                "lineColor": ROOT.kGreen - 2,
                "fillColor": ROOT.kGreen - 4,
                "markerStyle": 28,
                "markerStyle2": 34,
                "markerScale": 1.0,
                "legendLabel": "aMC@NLO, full CKM, NNPDF30",
                "legendLabelFull": "aMC@NLO, full CKM, NNPDF30",
                "offset": -1 + 3 * (2 / 5.),
            },
            "MGPy8EG_FxFx_3jets": {
                "lineColor": ROOT.kBlue + 2,
                "fillColor": ROOT.kBlue - 9,
                "markerStyle": 32,
                "markerStyle2": 23,
                "markerScale": 1.0,
                "legendLabel": "MG FxFx, diag. CKM, NNPDF31",
                "legendLabelFull": "MG FxFx, diag. CKM, NNPDF31",
                "offset": -1 + 4 * (2 / 5.),
            },
        },
        "PDF_comparison": {
            "ABMP16_5_nnlo": {
                "lineColor": ROOT.kBlue,
                "fillColor": ROOT.kBlue - 9,
                "markerStyle": 24,
                "markerStyle2": 20,
                "markerScale": 1.0,
                "legendLabel": "ABMP16_5",
                "legendLabelFull": "ABMP16_5",
                "offset": -1 + 1 * (2 / 10.),
            },
            "ATLASpdf21_T3": {
                "lineColor": ROOT.kRed + 1,
                "fillColor": ROOT.kRed - 9,
                "markerStyle": 42,
                "markerStyle2": 43,
                "markerScale": 1.8,
                "legendLabel": "ATLASpdf21_T3",
                "legendLabelFull": "ATLASpdf21_T3",
                "offset": -1 + 2 * (2 / 10.),
            },
            "CT18ANNLO": {
                "lineColor": ROOT.kOrange + 2,
                "fillColor": ROOT.kOrange,
                "markerStyle": 25,
                "markerStyle2": 21,
                "markerScale": 1.0,
                "legendLabel": "CT18A",
                "legendLabelFull": "CT18A",
                "offset": -1 + 3 * (2 / 10.),
            },
            "CT18NNLO": {
                "lineColor": ROOT.kOrange - 6,
                "fillColor": ROOT.kOrange - 9,
                "markerStyle": 44,
                "markerStyle2": 45,
                "markerScale": 1.2,
                "legendLabel": "CT18",
                "legendLabelFull": "CT18",
                "offset": -1 + 4 * (2 / 10.),
            },
            "MSHT20nnlo_as118": {
                "lineColor": ROOT.kMagenta + 2,
                "fillColor": ROOT.kMagenta - 9,
                "markerStyle": 27,
                "markerStyle2": 33,
                "markerScale": 1.6,
                "legendLabel": "MSHT20",
                "legendLabelFull": "MSHT20",
                "offset": -1 + 5 * (2 / 10.),
            },
            "PDF4LHC21_40": {
                "lineColor": ROOT.kPink - 1,
                "fillColor": ROOT.kPink + 6,
                "markerStyle": 46,
                "markerStyle2": 47,
                "markerScale": 1.2,
                "legendLabel": "PDF4LHC21_40",
                "legendLabelFull": "PDF4LHC21_40",
                "offset": -1 + 6 * (2 / 10.),
            },
            # "NNPDF30_nnlo_as_0118_hessian": {
            #     "lineColor": ROOT.kGreen - 2,
            #     "fillColor": ROOT.kGreen - 4,
            #     "markerStyle": 28,
            #     "markerStyle2": 34,
            #     "markerScale": 1.1,
            #     "legendLabel": "NNPDF30_nnlo",
            #     "legendLabelFull": "NNPDF30_nnlo",
            #     "offset": -1 + 7 * (2/10.),
            # },
            "NNPDF31_nnlo_as_0118_hessian": {
                "lineColor": ROOT.kGreen - 2,
                "fillColor": ROOT.kGreen - 4,
                "markerStyle": 26,
                "markerStyle2": 22,
                "markerScale": 1.3,
                "legendLabel": "NNPDF31",
                "legendLabelFull": "NNPDF31",
                "offset": -1 + 7 * (2 / 10.),
            },
            "NNPDF31_nnlo_as_0118_strange": {
                "lineColor": ROOT.kGreen + 3,
                "fillColor": ROOT.kGreen + 1,
                "markerStyle": 26,
                "markerStyle2": 22,
                "markerScale": 1.3,
                "legendLabel": "NNPDF31_str",
                "legendLabelFull": "NNPDF31_str",
                "offset": -1 + 8 * (2 / 10.),
            },
            "NNPDF40_nnlo_as_01180_hessian": {
                "lineColor": ROOT.kGreen + 4,
                "fillColor": ROOT.kGreen + 2,
                "markerStyle": 32,
                "markerStyle2": 23,
                "markerScale": 1.3,
                "legendLabel": "NNPDF40",
                "legendLabelFull": "NNPDF40",
                "offset": -1 + 9 * (2 / 10.),
            },
        },
        "NLO_PDF_comparison": {
            "ABMP16_3_nlo": {
                "lineColor": ROOT.kBlue,
                "fillColor": ROOT.kBlue - 9,
                "markerStyle": 24,
                "markerStyle2": 20,
                "markerScale": 1.0,
                "legendLabel": "ABMP16_3",
                "legendLabelFull": "ABMP16_3",
                "offset": -1 + 1 * (2 / 7.),
            },
            "CT18ANLO": {
                "lineColor": ROOT.kOrange + 2,
                "fillColor": ROOT.kOrange,
                "markerStyle": 25,
                "markerStyle2": 21,
                "markerScale": 1.0,
                "legendLabel": "CT18A",
                "legendLabelFull": "CT18A",
                "offset": -1 + 2 * (2 / 7.),
            },
            "CT18NLO": {
                "lineColor": ROOT.kOrange - 6,
                "fillColor": ROOT.kOrange - 9,
                "markerStyle": 44,
                "markerStyle2": 45,
                "markerScale": 1.2,
                "legendLabel": "CT18",
                "legendLabelFull": "CT18",
                "offset": -1 + 3 * (2 / 7.),
            },
            "MSHT20nlo_as118": {
                "lineColor": ROOT.kMagenta + 2,
                "fillColor": ROOT.kMagenta - 9,
                "markerStyle": 27,
                "markerStyle2": 33,
                "markerScale": 1.6,
                "legendLabel": "MSHT20",
                "legendLabelFull": "MSHT20",
                "offset": -1 + 4 * (2 / 7.),
            },
            # "NNPDF30_nlo_as_0118_hessian": {
            #     "lineColor": ROOT.kGreen - 2,
            #     "fillColor": ROOT.kGreen - 4,
            #     "markerStyle": 28,
            #     "markerStyle2": 34,
            #     "markerScale": 1.1,
            #     "legendLabel": "NNPDF30",
            #     "legendLabelFull": "NNPDF30",
            #     "offset": -1 + 5 * (2/10.),
            # },
            "NNPDF31_nlo_as_0118_hessian": {
                "lineColor": ROOT.kGreen - 2,
                "fillColor": ROOT.kGreen - 4,
                "markerStyle": 26,
                "markerStyle2": 22,
                "markerScale": 1.3,
                "legendLabel": "NNPDF31",
                "legendLabelFull": "NNPDF31",
                "offset": -1 + 5 * (2 / 7.),
            },
            "NNPDF40_nlo_as_01180": {
                "lineColor": ROOT.kGreen + 4,
                "fillColor": ROOT.kGreen + 2,
                "markerStyle": 32,
                "markerStyle2": 23,
                "markerScale": 1.3,
                "legendLabel": "NNPDF40",
                "legendLabelFull": "NNPDF40",
                "offset": -1 + 6 * (2 / 7.),
            },
        }
    }

    # Check if Dstar is the decay mode
    if options.decay == "Dstar":

        # Set fit results path for observables
        # OBSERVABLES["pt"]["fit_results"] = "/global/cfs/cdirs/atlas/wcharm/TRExFitter/Output/Dstar_2022_08_08_pt/"
        # OBSERVABLES["eta"]["fit_results"] = "/global/cfs/cdirs/atlas/wcharm/TRExFitter/Output/Dstar_2022_08_08_eta/"
        OBSERVABLES["pt"]["fit_results"] = "/global/cscratch1/sd/mmuskinj/TRExFitter/fit_2022_12_14_Dstar_new/"
        OBSERVABLES["eta"]["fit_results"] = "/global/cscratch1/sd/mmuskinj/TRExFitter/fit_2022_12_14_Dstar_new/"

    for plot_type, theory_dict in THEORY_DICT.items():

        if not os.path.isdir(os.path.join("fit_results", plot_type, options.decay)):
            os.makedirs(os.path.join("fit_results", plot_type, options.decay))
        outfile = ROOT.TFile(f"fit_results/{plot_type}/{options.decay}/results.root", "RECREATE")

        # theory predictions for ladder plots
        ladder_dict = {}

        for obs_name, obs in OBSERVABLES.items():

            # Arithmetics
            br = 1.0
            sf = 1.0

            # Normalize to bin width
            if obs_name == "eta":
                sf = 2.0

            # Set branching ratio
            if options.decay == "Dstar":
                br *= 0.677

            # variable name
            name = "lep_abs_eta" if obs_name == "eta" else "D_pt"

            # no ticks in error bars
            ROOT.gStyle.SetEndErrorSize(0)

            # --------------------------------------------
            # Step 0: get cross section priors
            # --------------------------------------------
            if options.decay in ["Dplus", "Dstar"]:
                # f = ROOT.TFile(os.path.join(DIR_PRIORS, f"fid_eff_{obs_name}_{options.decay.lower()}_stat", "unfolding.root"))
                # h_minus = f.Get(f"Sherpa2211_WplusD_OS-SS_lep_minus_{options.decay}_Kpipi_truth_differential_{obs_name}")
                # h_plus = f.Get(f"Sherpa2211_WplusD_OS-SS_lep_plus_{options.decay}_Kpipi_truth_differential_{obs_name}")
                priors = {
                    "Wminus": 1 / (2. * br),
                    "Wminus_1": 1 / (2. * br),
                    "Wminus_2": 1 / (2. * br),
                    "Wminus_3": 1 / (2. * br),
                    "Wminus_4": 1 / (2. * br),
                    "Wminus_5": 1 / (2. * br),
                    "Wplus": 1 / (2. * br),
                    "Wplus_1": 1 / (2. * br),
                    "Wplus_2": 1 / (2. * br),
                    "Wplus_3": 1 / (2. * br),
                    "Wplus_4": 1 / (2. * br),
                    "Wplus_5": 1 / (2. * br),
                    # "Wminus": h_minus.Integral() / (2. * br),
                    # "Wminus_1": h_minus.GetBinContent(1) / (2. * br),
                    # "Wminus_2": h_minus.GetBinContent(2) / (2. * br),
                    # "Wminus_3": h_minus.GetBinContent(3) / (2. * br),
                    # "Wminus_4": h_minus.GetBinContent(4) / (2. * br),
                    # "Wminus_5": h_minus.GetBinContent(5) / (2. * br),
                    # "Wplus": h_plus.Integral() / (2. * br),
                    # "Wplus_1": h_plus.GetBinContent(1) / (2. * br),
                    # "Wplus_2": h_plus.GetBinContent(2) / (2. * br),
                    # "Wplus_3": h_plus.GetBinContent(3) / (2. * br),
                    # "Wplus_4": h_plus.GetBinContent(4) / (2. * br),
                    # "Wplus_5": h_plus.GetBinContent(5) / (2. * br),
                }
                print("============ cross section priors ============")
                for key, val in priors.items():
                    print(f"{key}: {val}")

                # --------------------------------------------
                # Step 1: parse fit results from txt files
                # --------------------------------------------
                # folder names
                obs_fit = f"WCharm_{options.decay}_lep_obs_OSSS_complete_xsec_{obs_name}"
                obs_fit2 = f"WCharm_{options.decay}_lep_obs_OSSS_complete2_xsec_{obs_name}"
                obs_fit_abs = f"WCharm_{options.decay}_lep_obs_OSSS_complete_xsec_alt_{obs_name}"
                # obs_fit = f"WCharm_lep_obs_OSSS_complete_{obs_name}"
                # obs_fit2 = f"WCharm_lep_obs_OSSS_complete2_{obs_name}"
                # obs_fit_abs = f"WCharm_lep_obs_OSSS_complete_alt_{obs_name}"

                # observed
                POIs_obs = extract_pois(os.path.join(obs["fit_results"], obs_fit, "Fits", f"{obs_fit}.txt"))
                POIs_obs.update(extract_pois(os.path.join(obs["fit_results"], obs_fit, "Fits", f"{obs_fit}_expr.txt")))
                print("============ post fit results ============")
                for key, val in POIs_obs.items():
                    print(f"{key}: {val}")

                # normalization factors
                f_result = ROOT.TFile(os.path.join(obs["fit_results"], obs_fit, "Fits", f"{obs_fit}.root"), "READ")
                f_result2 = ROOT.TFile(os.path.join(obs["fit_results"], obs_fit2, "Fits", f"{obs_fit2}.root"), "READ")
                f_result_abs = ROOT.TFile(os.path.join(obs["fit_results"], obs_fit_abs, "Fits", f"{obs_fit_abs}.root"), "READ")
                fr = f_result.Get("nll_simPdf_newasimovData_with_constr")
                fr2 = f_result2.Get("nll_simPdf_newasimovData_with_constr")
                fr_abs = f_result_abs.Get("nll_simPdf_newasimovData_with_constr")

                # stat-only normalization factors
                f_result_stat = ROOT.TFile(os.path.join(obs["fit_results"], obs_fit, "Fits", f"{obs_fit}_statOnly.root"), "READ")
                f_result2_stat = ROOT.TFile(os.path.join(obs["fit_results"], obs_fit2, "Fits", f"{obs_fit2}_statOnly.root"), "READ")
                f_result_abs_stat = ROOT.TFile(os.path.join(obs["fit_results"], obs_fit_abs, "Fits", f"{obs_fit_abs}_statOnly.root"), "READ")
                fr_stat = f_result_stat.Get("nll_simPdf_newasimovData_with_constr")
                fr2_stat = f_result2_stat.Get("nll_simPdf_newasimovData_with_constr")
                fr_abs_stat = f_result_abs_stat.Get("nll_simPdf_newasimovData_with_constr")

                # read POIs
                POIs_obs = {}
                POIs_stat = {}
                for POI in POIs_default:
                    par = fr.floatParsFinal().find(POI)
                    par_stat = fr_stat.floatParsFinal().find(POI)
                    POIs_obs[POI] = [par.getVal(), par.getErrorHi(), par.getErrorLo()]
                    POIs_stat[POI] = [par_stat.getVal(), par_stat.getErrorHi(), par_stat.getErrorLo()]
                for POI in POIs_default2:
                    par = fr2.floatParsFinal().find(POI)
                    par_stat = fr2_stat.floatParsFinal().find(POI)
                    POIs_obs[POI] = [par.getVal(), par.getErrorHi(), par.getErrorLo()]
                    POIs_stat[POI] = [par_stat.getVal(), par_stat.getErrorHi(), par_stat.getErrorLo()]
                for POI in POIs_abs:
                    par = fr_abs.floatParsFinal().find(POI)
                    par_stat = fr_abs_stat.floatParsFinal().find(POI)
                    POIs_obs[POI] = [par.getVal(), par.getErrorHi(), par.getErrorLo()]
                    POIs_stat[POI] = [par_stat.getVal(), par_stat.getErrorHi(), par_stat.getErrorLo()]

                print("============ post fit results ============")
                for key, val in POIs_obs.items():
                    print(f"{key}: {val}")

                print("============ post fit results (stat err) ============")
                for key, val in POIs_stat.items():
                    print(f"{key}: {val}")

            # --------------------------------------------
            # Step 2: make TGraph objects
            # --------------------------------------------
            for lep in ["minus", "plus"]:
                if options.decay in ["Dplus", "Dstar"]:
                    gr_obs = ROOT.TGraphAsymmErrors()
                    gr_obs_norm = ROOT.TGraphAsymmErrors()
                    gr_obs_ratio = ROOT.TGraphAsymmErrors()
                    gr_obs_norm_ratio = ROOT.TGraphAsymmErrors()
                    gr_obs_norm_ratio_stat = ROOT.TGraphAsymmErrors()
                    gr_obs_sys = ROOT.TGraphAsymmErrors()
                    gr_obs_norm_sys = ROOT.TGraphAsymmErrors()
                    for i in range(len(obs["bins"]) - 1):
                        xl = obs["bins"][i]
                        xh = obs["bins"][i + 1]
                        w = xh - xl

                        # prior relative cross section
                        y_prior = float(priors[f"W{lep}_{i + 1}"])
                        y_rel = y_prior / float(priors[f"W{lep}"])

                        y = float(POIs_obs[f"mu_W{lep}_{i + 1}"][0]) * y_prior
                        y_up = float(POIs_obs[f"mu_W{lep}_{i + 1}"][1]) * y_prior
                        y_dn = float(POIs_obs[f"mu_W{lep}_{i + 1}"][2]) * y_prior
                        y_up_stat = float(POIs_stat[f"mu_W{lep}_{i + 1}"][1]) * y_prior
                        y_dn_stat = float(POIs_stat[f"mu_W{lep}_{i + 1}"][2]) * y_prior
                        # y_up_sys = (y_up**2 - y_up_stat**2)**(0.5)
                        # y_dn_sys = (y_dn**2 - y_dn_stat**2)**(0.5)
                        y_norm = float(POIs_obs[f"mu_W{lep}_rel_{i + 1}"][0]) * y_rel
                        y_norm_up = float(POIs_obs[f"mu_W{lep}_rel_{i + 1}"][1]) * y_rel
                        y_norm_dn = float(POIs_obs[f"mu_W{lep}_rel_{i + 1}"][2]) * y_rel
                        y_norm_up_stat = float(POIs_stat[f"mu_W{lep}_rel_{i + 1}"][1]) * y_rel
                        y_norm_dn_stat = float(POIs_stat[f"mu_W{lep}_rel_{i + 1}"][2]) * y_rel
                        # y_norm_up_sys = (y_norm_up**2 - y_norm_up_stat**2)**(0.5)
                        # y_norm_dn_sys = (y_norm_dn**2 - y_norm_dn_stat**2)**(0.5)

                        # fill graphs
                        if obs["logx"]:
                            xc = ROOT.TMath.Power(10, ROOT.TMath.Log10(xl) + (ROOT.TMath.Log10(xl + w) - ROOT.TMath.Log10(xl)) / 2.)
                        else:
                            xc = xl + w / 2.
                        xc_up = xl + w - xc
                        xc_dn = xc - xl
                        gr_obs.SetPoint(i, xc, y * sf)
                        gr_obs.SetPointError(i, xc_dn, xc_up, abs(y_dn) * sf, abs(y_up) * sf)
                        gr_obs_norm.SetPoint(i, xc, y_norm * sf)
                        gr_obs_norm.SetPointError(i, xc_dn, xc_up, abs(y_norm_dn) * sf, abs(y_norm_up) * sf)
                        gr_obs_ratio.SetPoint(i, xc, 1.0)
                        gr_obs_ratio.SetPointError(i, xc_dn, xc_up, abs(y_dn / y), abs(y_up / y))
                        gr_obs_norm_ratio.SetPoint(i, xc, 1.0)
                        gr_obs_norm_ratio.SetPointError(i, xc_dn, xc_up, abs(y_norm_dn / y_norm), abs(y_norm_up / y_norm))
                        gr_obs_norm_ratio_stat.SetPoint(i, xc, 1.0)
                        gr_obs_norm_ratio_stat.SetPointError(i, xc_dn, xc_up, abs(y_norm_dn_stat / y_norm), abs(y_norm_up_stat / y_norm))
                        gr_obs_sys.SetPoint(i, xc, y * sf)
                        gr_obs_norm_sys.SetPoint(i, xc, y_norm * sf)
                        if obs["logx"]:
                            x_err_up = ROOT.TMath.Power(10, ROOT.TMath.Log10(
                                xc) + (ROOT.TMath.Log10(obs["bins"][-1]) - ROOT.TMath.Log10(obs["bins"][0])) / 200.) - xc
                            x_err_dn = xc - ROOT.TMath.Power(10, ROOT.TMath.Log10(xc) -
                                                             (ROOT.TMath.Log10(obs["bins"][-1]) - ROOT.TMath.Log10(obs["bins"][0])) / 200.)
                            gr_obs_sys.SetPointError(i, xc_dn, xc_up, abs(y_dn_stat) * sf, abs(y_up_stat) * sf)
                            gr_obs_norm_sys.SetPointError(i, xc_dn, xc_up, abs(y_norm_dn_stat) * sf, abs(y_norm_up_stat) * sf)
                        else:
                            gr_obs_sys.SetPointError(i, xc_dn, xc_up, abs(y_dn_stat) * sf, abs(y_up_stat) * sf)
                            gr_obs_norm_sys.SetPointError(i, xc_dn, xc_up, abs(y_norm_dn_stat) * sf, abs(y_norm_up_stat) * sf)

                    # line width
                    gr_obs.SetLineWidth(1)
                    gr_obs_norm.SetLineWidth(1)
                    gr_obs_sys.SetLineWidth(0)
                    gr_obs_ratio.SetLineWidth(0)
                    gr_obs_norm_ratio.SetLineWidth(0)
                    gr_obs.SetMarkerSize(1.5)
                    gr_obs_norm.SetMarkerSize(1.5)
                    gr_obs_norm.SetMarkerStyle(4)
                    gr_obs.SetMarkerStyle(4)
                    gr_obs_line_leg = gr_obs.Clone(f"{gr_obs.GetName()}_line_leg")
                    gr_obs_line_leg.SetLineWidth(2)
                    gr_obs_line = gr_obs.Clone(f"{gr_obs.GetName()}_line")
                    gr_obs_norm_line = gr_obs_norm.Clone(f"{gr_obs_norm.GetName()}_line")
                    for i in range(gr_obs_line.GetN()):
                        gr_obs_line.GetEYhigh()[i] = 0
                        gr_obs_line.GetEYlow()[i] = 0
                        gr_obs_norm_line.GetEYhigh()[i] = 0
                        gr_obs_norm_line.GetEYlow()[i] = 0

                    # fill
                    gr_obs.SetFillColor(ROOT.kGray)
                    gr_obs_norm.SetFillColor(ROOT.kGray)
                    gr_obs_sys.SetFillColor(ROOT.kGray + 2)
                    gr_obs_norm_sys.SetFillColor(ROOT.kGray + 2)
                    gr_obs_ratio.SetFillColor(ROOT.kGray)
                    # gr_obs_norm_ratio.SetFillColor(ROOT.kGray + 1)
                    gr_obs_norm_ratio.SetFillColor(ROOT.kGray)
                    gr_obs_norm_ratio_stat.SetFillColor(ROOT.kGray + 2)
                    gr_obs_norm_ratio_stat.SetLineColor(ROOT.kGray + 2)

                    # multigraph
                    mg_obs = ROOT.TMultiGraph()
                    mg_obs_norm = ROOT.TMultiGraph()
                    mg_obs_ratio = ROOT.TMultiGraph()
                    mg_obs_ratio_theory = ROOT.TMultiGraph()

                    # axis title
                    if obs_name == "pt":
                        mg_obs.GetYaxis().SetTitle(f"#lower[-0.25]{{#scale[0.5]{{#int}}}}d#sigma/d{obs['label']} [pb]")
                        mg_obs_norm.GetYaxis().SetTitle(f"#frac{{#scale[0.8]{{1}}}}{{#sigma}} #lower[-0.25]{{#scale[0.5]{{#int}}}}d#sigma/d{obs['label']}")
                        mg_obs_ratio.GetYaxis().SetTitle(f"#frac{{Theory}}{{1/#sigma #lower[-0.25]{{#scale[0.5]{{#int}}}}d#sigma/d{obs['label']}}}")
                    elif obs_name == "eta":
                        mg_obs.GetYaxis().SetTitle(f"d#sigma/d{obs['label']} [pb]")
                        mg_obs_norm.GetYaxis().SetTitle(f"#frac{{#scale[0.8]{{1}}}}{{#sigma}} d#sigma/d{obs['label']}")
                        mg_obs_ratio.GetYaxis().SetTitle(f"#frac{{Theory}}{{1/#sigma d#sigma/d{obs['label']}}}")
                    if obs_name == "pt":
                        mg_obs_ratio.GetXaxis().SetTitle(obs['label'] + " [GeV]")
                    else:
                        mg_obs_ratio.GetXaxis().SetTitle(obs['label'])

                    # label and title size
                    GLOBAL_SF = 1.4
                    mg_obs.GetXaxis().SetLabelSize(0)
                    mg_obs.GetYaxis().SetTitleSize(mg_obs.GetYaxis().GetTitleSize() * GLOBAL_SF)
                    mg_obs.GetYaxis().SetTitleOffset(mg_obs.GetYaxis().GetTitleOffset() * (1 / (GLOBAL_SF * 1.1)))
                    mg_obs.GetYaxis().SetLabelSize(mg_obs.GetYaxis().GetLabelSize() * GLOBAL_SF)

                    SF = 0.55 / 0.30
                    mg_obs_norm.GetXaxis().SetLabelSize(0)
                    mg_obs_norm.GetYaxis().SetTitleSize(mg_obs_norm.GetYaxis().GetTitleSize() * SF * GLOBAL_SF)
                    mg_obs_norm.GetYaxis().SetTitleOffset(mg_obs_norm.GetYaxis().GetTitleOffset() * (1 / (GLOBAL_SF * 1.1 * SF)))
                    mg_obs_norm.GetYaxis().SetLabelSize(mg_obs_norm.GetYaxis().GetLabelSize() * SF * GLOBAL_SF)
                    # mg_obs_norm.GetYaxis().CenterTitle()

                    SF = 0.55 / 0.35
                    mg_obs_ratio.GetYaxis().SetTitleSize(mg_obs_ratio.GetYaxis().GetTitleSize() * SF * GLOBAL_SF)
                    mg_obs_ratio.GetYaxis().SetTitleOffset(mg_obs_ratio.GetYaxis().GetTitleOffset() * (1 / (GLOBAL_SF * SF)))
                    mg_obs_ratio.GetXaxis().SetTitleSize(mg_obs_ratio.GetXaxis().GetTitleSize() * SF * GLOBAL_SF)
                    mg_obs_ratio.GetXaxis().SetTitleOffset(mg_obs_ratio.GetXaxis().GetTitleOffset() * (1 / (GLOBAL_SF * 0.6 * SF)))
                    mg_obs_ratio.GetYaxis().SetLabelSize(mg_obs_ratio.GetYaxis().GetLabelSize() * SF * GLOBAL_SF)
                    mg_obs_ratio.GetXaxis().SetLabelSize(mg_obs_ratio.GetXaxis().GetLabelSize() * SF * GLOBAL_SF)
                    mg_obs_ratio.GetYaxis().CenterTitle()

                    # tick marks
                    mg_obs.GetYaxis().SetNdivisions(506)
                    mg_obs_norm.GetYaxis().SetNdivisions(504)
                    mg_obs_ratio.GetYaxis().SetNdivisions(306)

                    # log x-axis
                    mg_obs_ratio.GetXaxis().SetMoreLogLabels()
                    mg_obs_ratio.GetXaxis().SetNoExponent()

                    # legend
                    N = 4 + len(theory_dict)
                    if plot_type in ["PDF_comparison", "NLO_PDF_comparison"]:
                        leg = ROOT.TLegend(0.48, 0.88 - (N // 2) * 0.050, 0.94, 0.88)
                        leg.SetNColumns(2)
                        leg.SetBorderSize(0)
                        leg.SetFillColor(0)
                        leg.SetFillStyle(0)
                        leg.SetTextSize(34)
                        leg.SetTextFont(43)
                        leg.AddEntry(gr_obs_line_leg, "Data", "l")
                        leg.AddEntry(gr_obs_sys, "Stat. Unc.", "f")
                        # leg.AddEntry(gr_obs_norm_ratio_stat, "Stat. Unc.", "f")
                        leg.AddEntry(gr_obs_norm_ratio, "Syst. #oplus Stat.", "f")
                    else:
                        leg = ROOT.TLegend(0.47, 0.88 - 2 * 0.050, 0.91, 0.88)
                        leg.SetNColumns(2)
                        leg.SetBorderSize(0)
                        leg.SetFillColor(0)
                        leg.SetFillStyle(0)
                        leg.SetTextSize(34)
                        leg.SetTextFont(43)
                        leg.AddEntry(gr_obs_line_leg, "Data", "l")
                        leg.AddEntry(gr_obs_sys, "Stat. Unc.", "f")
                        # leg.AddEntry(gr_obs_norm_ratio_stat, "Stat. Unc.", "f")
                        leg.AddEntry(gr_obs_norm_ratio, "Syst. #oplus Stat.", "f")

                        # separate legend for predictions
                        leg2 = ROOT.TLegend(0.47, 0.88 - (2 + len(theory_dict)) * 0.050, 0.45 + (0.91 - 0.45) / 2., 0.88 - 2 * 0.050)
                        leg2.SetBorderSize(0)
                        leg2.SetFillColor(0)
                        leg2.SetFillStyle(0)
                        leg2.SetTextSize(34)
                        leg2.SetTextFont(43)

                    # add to ratio multigraph
                    mg_obs_ratio.Add(gr_obs_norm_ratio, "0e2")
                    mg_obs_ratio.Add(gr_obs_norm_ratio_stat, "0e2")

                    # add graphs
                    mg_obs.Add(gr_obs, "0e2")
                    mg_obs.Add(gr_obs_sys, "0e2")
                    mg_obs.Add(gr_obs_line, "e0")
                    mg_obs_norm.Add(gr_obs_norm, "0e2")
                    mg_obs_norm.Add(gr_obs_norm_sys, "0e2")
                    mg_obs_norm.Add(gr_obs_norm_line, "e0")

                    # print out latex
                    print(f"================ {options.decay} {lep} {obs_name} =================")
                    # $[0.0,\,0.5]$ & 12.42 & 0.13 & $^{+0.72}_{-0.68}$ \\
                    for i in range(0, 5):
                        y = gr_obs.GetY()[i]
                        y_stat = 0.5 * (gr_obs_sys.GetErrorYhigh(i) + gr_obs_sys.GetErrorYlow(i))
                        y_sys_up = (gr_obs.GetErrorYhigh(i)**2 - y_stat**2)**0.5
                        y_sys_dn = (gr_obs.GetErrorYlow(i)**2 - y_stat**2)**0.5

                        y_norm = gr_obs_norm.GetY()[i]
                        y_norm_stat = 0.5 * (gr_obs_norm_sys.GetErrorYhigh(i) + gr_obs_norm_sys.GetErrorYlow(i))
                        y_norm_sys_up = (gr_obs_norm.GetErrorYhigh(i)**2 - y_norm_stat**2)**0.5
                        y_norm_sys_dn = (gr_obs_norm.GetErrorYlow(i)**2 - y_norm_stat**2)**0.5
                        print(
                            f" & {y:.4f} & {y_stat:.4f} & $^{{+{y_sys_up:.2f}}}_{{-{y_sys_dn:.2f}}}$ & {y_norm:.6f} & {y_norm_stat:.6f} & $^{{+{y_norm_sys_up:.4f}}}_{{-{y_norm_sys_dn:.4f}}}$ \\\\")

                    # print out yaml
                    print(f"================ {options.decay} {lep} {obs_name} =================")
                    #
                    # - errors:
                    #     - {label: stat, symerror: 0.19}
                    #     - {label: syst, asymerror: {minus: -0.75, plus: 0.79}}
                    #     value: 15.27
                    #
                    for i in range(0, 5):
                        y = gr_obs.GetY()[i]
                        y_stat = 0.5 * (gr_obs_sys.GetErrorYhigh(i) + gr_obs_sys.GetErrorYlow(i))
                        y_sys_up = (gr_obs.GetErrorYhigh(i)**2 - y_stat**2)**0.5
                        y_sys_dn = (gr_obs.GetErrorYlow(i)**2 - y_stat**2)**0.5
                        print("  - errors:")
                        print(f"    - {{label: stat, symerror: {y_stat:.2f}}}")
                        print(f"    - {{label: syst, asymerror: {{minus: -{y_sys_dn:.2f}, plus: {y_sys_up:.2f}}}}}")
                        print(f"    value: {y:.2f}")

                    print("------------------------")
                    for i in range(0, 5):
                        y_norm = gr_obs_norm.GetY()[i]
                        y_norm_stat = 0.5 * (gr_obs_norm_sys.GetErrorYhigh(i) + gr_obs_norm_sys.GetErrorYlow(i))
                        y_norm_sys_up = (gr_obs_norm.GetErrorYhigh(i)**2 - y_norm_stat**2)**0.5
                        y_norm_sys_dn = (gr_obs_norm.GetErrorYlow(i)**2 - y_norm_stat**2)**0.5
                        print("  - errors:")
                        print(f"    - {{label: stat, symerror: {y_norm_stat:.4f}}}")
                        print(f"    - {{label: syst, asymerror: {{minus: -{y_norm_sys_dn:.4f}, plus: {y_norm_sys_up:.4f}}}}}")
                        print(f"    value: {y_norm:.4f}")

                # --------------------------------------------
                # Step 2.5: theory comparisons
                # --------------------------------------------

                # file with theory predictions and uncertainties
                f_theory = ROOT.TFile(os.path.join(DIR_THEORY, "predictions.root"))
                assert f_theory

                # production fraction and hadronization uncertainties
                hName_ABMP16_3 = f"ABMP16_3_nlo_abs_{options.decay}_{name}"
                hName_ABMP16_3_herwig = f"ABMP16_3_nlo_herwig_abs_{options.decay}_{name}"
                hName_ABMP16_3_monash = f"ABMP16_3_nlo_monash_abs_{options.decay}_{name}"
                h_ABMP16_3 = f_theory.Get(f"{hName_ABMP16_3}_pdf_central")
                h_ABMP16_3_herwig = f_theory.Get(f"{hName_ABMP16_3_herwig}_pdf_central")
                h_ABMP16_3_monash = f_theory.Get(f"{hName_ABMP16_3_monash}_pdf_central")
                assert (h_ABMP16_3 and h_ABMP16_3_herwig and h_ABMP16_3_monash), (hName_ABMP16_3, hName_ABMP16_3_herwig, hName_ABMP16_3_monash)
                h_list = [h_ABMP16_3, h_ABMP16_3_herwig, h_ABMP16_3_monash]

                hName_ABMP16_3 = f"ABMP16_3_nlo_rel_{options.decay}_{name}"
                hName_ABMP16_3_herwig = f"ABMP16_3_nlo_herwig_rel_{options.decay}_{name}"
                hName_ABMP16_3_monash = f"ABMP16_3_nlo_monash_rel_{options.decay}_{name}"
                h_ABMP16_3 = f_theory.Get(f"{hName_ABMP16_3}_pdf_central")
                h_ABMP16_3_herwig = f_theory.Get(f"{hName_ABMP16_3_herwig}_pdf_central")
                h_ABMP16_3_monash = f_theory.Get(f"{hName_ABMP16_3_monash}_pdf_central")
                assert (h_ABMP16_3 and h_ABMP16_3_herwig and h_ABMP16_3_monash), (hName_ABMP16_3, hName_ABMP16_3_herwig, hName_ABMP16_3_monash)
                h_rel_list = [h_ABMP16_3, h_ABMP16_3_herwig, h_ABMP16_3_monash]

                for prediction, prediction_dict in theory_dict.items():

                    # read theory histograms
                    # absolute basis
                    hName_base = f"{prediction}_abs_{options.decay}_{name}"
                    h_theory = f_theory.Get(f"{hName_base}_pdf_central")
                    h_theory_pdf_up = f_theory.Get(f"{hName_base}_pdf_up")
                    h_theory_pdf_dn = f_theory.Get(f"{hName_base}_pdf_dn")
                    assert (h_theory and h_theory_pdf_up and h_theory_pdf_dn), hName_base

                    # relative basis
                    hName_rel_base = f"{prediction}_rel_{options.decay}_{name}"
                    h_theory_rel = f_theory.Get(f"{hName_rel_base}_pdf_central")
                    h_theory_rel_pdf_up = f_theory.Get(f"{hName_rel_base}_pdf_up")
                    h_theory_rel_pdf_dn = f_theory.Get(f"{hName_rel_base}_pdf_dn")
                    assert (h_theory_rel and h_theory_rel_pdf_up and h_theory_rel_pdf_dn), hName_rel_base

                    # save info for later
                    ladder_dict[f"{prediction}_{options.decay}_{name}"] = {
                        "nominal": h_theory_rel,
                        "pdf_up": h_theory_rel_pdf_up,
                        "pdf_dn": h_theory_rel_pdf_dn,
                        "had": h_rel_list,
                    }

                    # QCD Scale error (only available for NNPDF40_nnlo_as_01180_hessian)
                    hName_qcd_base = f"{prediction}_abs_{options.decay}_{name}"
                    if not f_theory.Get(f"{hName_base}_qcd_up"):
                        hName_qcd_base = f"NNPDF40_nnlo_as_01180_hessian_abs_{options.decay}_{name}"
                    h_theory_qcd_central = f_theory.Get(f"{hName_qcd_base}_pdf_central")
                    h_theory_qcd_up = f_theory.Get(f"{hName_qcd_base}_qcd_up")
                    h_theory_qcd_dn = f_theory.Get(f"{hName_qcd_base}_qcd_dn")
                    assert (h_theory_qcd_central and h_theory_qcd_up and h_theory_qcd_dn), hName_qcd_base
                    h_theory_qcd_central = h_theory_qcd_central.Clone(f"{h_theory_qcd_central.GetName()}_{prediction}")
                    h_theory_qcd_up = h_theory_qcd_up.Clone(f"{h_theory_qcd_up.GetName()}_{prediction}")
                    h_theory_qcd_dn = h_theory_qcd_dn.Clone(f"{h_theory_qcd_dn.GetName()}_{prediction}")

                    hName_rel_qcd_base = f"{prediction}_rel_{options.decay}_{name}"
                    if not f_theory.Get(f"{hName_rel_qcd_base}_qcd_up"):
                        hName_rel_qcd_base = f"NNPDF40_nnlo_as_01180_hessian_rel_{options.decay}_{name}"
                    h_theory_rel_qcd_central = f_theory.Get(f"{hName_rel_qcd_base}_pdf_central")
                    h_theory_rel_qcd_up = f_theory.Get(f"{hName_rel_qcd_base}_qcd_up")
                    h_theory_rel_qcd_dn = f_theory.Get(f"{hName_rel_qcd_base}_qcd_dn")
                    assert (h_theory_rel_qcd_central and h_theory_rel_qcd_up and h_theory_rel_qcd_dn), hName_rel_qcd_base
                    h_theory_rel_qcd_central = h_theory_rel_qcd_central.Clone(f"{h_theory_rel_qcd_central.GetName()}_{prediction}")
                    h_theory_rel_qcd_up = h_theory_rel_qcd_up.Clone(f"{h_theory_rel_qcd_up.GetName()}_{prediction}")
                    h_theory_rel_qcd_dn = h_theory_rel_qcd_dn.Clone(f"{h_theory_rel_qcd_dn.GetName()}_{prediction}")

                    # transform to relative error
                    h_theory_qcd_up.Divide(h_theory_qcd_central)
                    h_theory_qcd_dn.Divide(h_theory_qcd_central)
                    h_theory_rel_qcd_up.Divide(h_theory_rel_qcd_central)
                    h_theory_rel_qcd_dn.Divide(h_theory_rel_qcd_central)

                    # save info for later
                    ladder_dict[f"{prediction}_{options.decay}_{name}"].update({
                        "qcd_rel_up": h_theory_rel_qcd_up,
                        "qcd_rel_dn": h_theory_rel_qcd_dn,
                    })

                    # style
                    gr_theory = ROOT.TGraphAsymmErrors()
                    gr_theory.SetLineWidth(1)
                    gr_theory.SetLineColor(prediction_dict["lineColor"])
                    gr_theory.SetMarkerColor(prediction_dict["lineColor"])
                    gr_theory.SetFillColor(prediction_dict["fillColor"])
                    gr_theory.SetMarkerStyle(prediction_dict["markerStyle"])
                    gr_theory_norm = ROOT.TGraphAsymmErrors()
                    gr_theory_norm.SetLineWidth(1)
                    gr_theory_norm.SetLineColor(prediction_dict["lineColor"])
                    gr_theory_norm.SetMarkerColor(prediction_dict["lineColor"])
                    gr_theory_norm.SetFillColor(prediction_dict["fillColor"])
                    gr_theory_norm.SetMarkerStyle(prediction_dict["markerStyle"])

                    # fill the theory graphs
                    if options.decay in ["Dplus", "Dstar"]:
                        offset = 0 if lep == "plus" else 5
                        for i in range(5):
                            # absolute cross section
                            gr_theory.SetPoint(i, gr_obs.GetX()[i], h_theory.GetBinContent(i + 1 + offset) * sf)
                            err_pdf_up = (h_theory_pdf_up.GetBinContent(i + 1 + offset) - h_theory.GetBinContent(i + 1 + offset)) * sf
                            err_pdf_dn = (h_theory.GetBinContent(i + 1 + offset) - h_theory_pdf_dn.GetBinContent(i + 1 + offset)) * sf
                            err_qcd_up = (h_theory.GetBinContent(i + 1 + offset) * h_theory_qcd_up.GetBinContent(i +
                                          1 + offset) - h_theory.GetBinContent(i + 1 + offset)) * sf
                            err_qcd_dn = (h_theory.GetBinContent(i + 1 + offset) - h_theory.GetBinContent(i +
                                          1 + offset) * h_theory_qcd_dn.GetBinContent(i + 1 + offset)) * sf
                            vals = [h.GetBinContent(i + 1 + offset) * sf for h in h_list]
                            err_hadronization = (max(vals) - min(vals)) / 2.
                            err_prod_frac = 0.028 if options.decay == "Dplus" else 0.020
                            err_prod_frac *= h_theory.GetBinContent(i + 1 + offset) * sf
                            err_powhel = 0.03
                            err_powhel *= h_theory.GetBinContent(i + 1 + offset) * sf
                            err_up = err_pdf_up * err_pdf_up + err_qcd_up * err_qcd_up + err_hadronization * err_hadronization + err_prod_frac * err_prod_frac + err_powhel * err_powhel
                            err_dn = err_pdf_dn * err_pdf_dn + err_qcd_dn * err_qcd_dn + err_hadronization * err_hadronization + err_prod_frac * err_prod_frac + err_powhel * err_powhel
                            gr_theory.SetPointError(i, 0, 0, err_up**0.5, err_dn**0.5)

                            # normalized cross section
                            gr_theory_norm.SetPoint(i, gr_obs.GetX()[i], h_theory_rel.GetBinContent(i + 1 + offset) * sf)
                            err_pdf_up = (h_theory_rel_pdf_up.GetBinContent(i + 1 + offset) - h_theory_rel.GetBinContent(i + 1 + offset)) * sf
                            err_pdf_dn = (h_theory_rel.GetBinContent(i + 1 + offset) - h_theory_rel_pdf_dn.GetBinContent(i + 1 + offset)) * sf
                            err_qcd_up = (h_theory_rel.GetBinContent(i + 1 + offset) * h_theory_rel_qcd_up.GetBinContent(i +
                                          1 + offset) - h_theory_rel.GetBinContent(i + 1 + offset)) * sf
                            err_qcd_dn = (h_theory_rel.GetBinContent(i + 1 + offset) - h_theory_rel.GetBinContent(i +
                                          1 + offset) * h_theory_rel_qcd_dn.GetBinContent(i + 1 + offset)) * sf
                            vals = [h.GetBinContent(i + 1 + offset) * sf for h in h_rel_list]
                            err_hadronization = (max(vals) - min(vals)) / 2.
                            err_up = err_pdf_up * err_pdf_up + err_qcd_up * err_qcd_up + err_hadronization * err_hadronization
                            err_dn = err_pdf_dn * err_pdf_dn + err_qcd_dn * err_qcd_dn + err_hadronization * err_hadronization
                            gr_theory_norm.SetPointError(i, 0, 0, err_up**0.5, err_dn**0.5)

                        # offset
                        for i in range(gr_theory.GetN()):

                            xl = obs["bins"][i]
                            xh = obs["bins"][i + 1]
                            w = xh - xl
                            rel_scale_num_points = len(theory_dict) / 9.
                            rel_scale = (ROOT.TMath.Log10(xh) - ROOT.TMath.Log10(xl)) / \
                                ((ROOT.TMath.Log10(obs["bins"][-1]) - ROOT.TMath.Log10(obs["bins"][0])) / 5.) / rel_scale_num_points
                            if obs["logx"]:
                                xc = ROOT.TMath.Power(10, ROOT.TMath.Log10(xl) + (ROOT.TMath.Log10(xl + w) - ROOT.TMath.Log10(xl)) / 2. +
                                                      prediction_dict["offset"] * (ROOT.TMath.Log10(xl + w) - ROOT.TMath.Log10(xl)) / 2.)
                                x_err_up = ROOT.TMath.Power(10, ROOT.TMath.Log10(
                                    xc) + (ROOT.TMath.Log10(obs["bins"][-1]) - ROOT.TMath.Log10(obs["bins"][0])) / (150. / rel_scale)) - xc
                                x_err_dn = xc - ROOT.TMath.Power(10, ROOT.TMath.Log10(xc) -
                                                                 (ROOT.TMath.Log10(obs["bins"][-1]) - ROOT.TMath.Log10(obs["bins"][0])) / (150. / rel_scale))
                                gr_theory.GetX()[i] = ROOT.TMath.Power(10, ROOT.TMath.Log10(xc) +
                                                                       (ROOT.TMath.Log10(obs["bins"][-1]) - ROOT.TMath.Log10(obs["bins"][0])) / (150. / rel_scale)) - xc
                            else:
                                offset = prediction_dict["offset"] * gr_obs.GetEXhigh()[i]
                                xc = gr_theory.GetX()[i] + offset
                                x_err_up = w / 40. / rel_scale_num_points
                                x_err_dn = w / 40. / rel_scale_num_points
                            gr_theory.GetX()[i] = xc
                            gr_theory_norm.GetX()[i] = xc
                            gr_theory.GetEXhigh()[i] = x_err_up
                            gr_theory.GetEXlow()[i] = x_err_dn
                            gr_theory_norm.GetEXhigh()[i] = x_err_up
                            gr_theory_norm.GetEXlow()[i] = x_err_dn

                        # ratio plot
                        gr_theory_ratio = gr_theory_norm.Clone()
                        for i in range(gr_theory_ratio.GetN()):
                            gr_theory_ratio.GetY()[i] = gr_theory_norm.GetY()[i] / gr_obs_norm.GetY()[i]
                            gr_theory_ratio.GetEYhigh()[i] = gr_theory_norm.GetEYhigh()[i] / gr_obs_norm.GetY()[i]
                            gr_theory_ratio.GetEYlow()[i] = gr_theory_norm.GetEYlow()[i] / gr_obs_norm.GetY()[i]

                        # add to legend
                        if plot_type in ["PDF_comparison", "NLO_PDF_comparison"]:
                            leg.AddEntry(gr_theory_ratio, prediction_dict["legendLabel"], "pf")
                        else:
                            leg2.AddEntry(gr_theory_ratio, prediction_dict["legendLabel"], "pf")

                        # add to multigraph
                        mg_obs.Add(gr_theory, "p0e5")
                        mg_obs_norm.Add(gr_theory_norm, "p0e5")
                        mg_obs_ratio_theory.Add(gr_theory_ratio, "p0e5")

                        # save to file
                        outfile.cd()
                        gr_theory_norm.Write(f"{options.decay}_W{lep}_{prediction}_{obs_name}_norm")
                        gr_theory_ratio.Write(f"{options.decay}_W{lep}_{prediction}_{obs_name}_norm_ratio")

                # --------------------------------------------
                # Step 3: make plots
                # --------------------------------------------
                if options.decay in ["Dplus", "Dstar"]:

                    # Plot histograms: first canvas, draw OS and SS on the same plot
                    c1, pad1, pad2, pad3 = createCanvasPads(f"W{lep}_{obs_name}_{plot_type}")

                    # upper canvas
                    if obs_name == "eta":
                        Y_MIN = 4
                        Y_MAX = 25
                    else:
                        Y_MIN = 1e-3
                        Y_MAX = 30
                    pad1.cd()
                    if obs["logx"]:
                        pad1.SetLogx()
                    mg_obs.Draw("a")
                    mg_obs.GetXaxis().SetLimits(obs["bins"][0], obs["bins"][-1])
                    mg_obs.SetMinimum(Y_MIN)
                    mg_obs.SetMaximum(Y_MAX * sf)

                    # ATLAS label
                    l1 = ROOT.TLatex()
                    l1.SetNDC()
                    l1.SetTextFont(73)
                    l1.SetTextSize(36)
                    l1.DrawLatex(0.19, 0.84 - 0 * 0.06, "ATLAS")
                    l2 = ROOT.TLatex()
                    l2.SetNDC()
                    l2.SetTextFont(43)
                    l2.SetTextSize(36)
                    # l2.DrawLatex(0.305, 0.84 - 0 * 0.06, "Internal")
                    l2.DrawLatex(0.305, 0.84 - 0 * 0.06, "")
                    l2.DrawLatex(0.19, 0.84 - 1 * 0.06, "#sqrt{s} = 13 TeV, 140 fb^{-1}")
                    if options.decay == "Dstar":
                        l2.DrawLatex(0.19, 0.84 - 2 * 0.06, "#it{W}^{%s}+#it{D*}^{%s}(#rightarrow(K#pi)#pi)" %
                                     (("-" if lep == "minus" else "+"), ("+" if lep == "minus" else "-")))
                    else:
                        l2.DrawLatex(0.19, 0.84 - 2 * 0.06, "#it{W}^{%s}+#it{D}^{%s}(#rightarrowK#pi#pi)" %
                                     (("-" if lep == "minus" else "+"), ("+" if lep == "minus" else "-")))
                    if plot_type in ["PDF_comparison", "NLO_PDF_comparison"]:
                        l2.DrawLatex(0.19, 0.84 - 3 * 0.06, "#bf{Pred.}: #it{aMC@NLO}")
                        if plot_type == "NLO_PDF_comparison":
                            l2.DrawLatex(0.19, 0.84 - 4 * 0.06, "#it{Full CKM}, #it{NLO PDF}")
                        else:
                            l2.DrawLatex(0.19, 0.84 - 4 * 0.06, "#it{Full CKM}, #it{NNLO PDF}")
                    else:
                        pass
                        # l2.DrawLatex(0.19, 0.84 - 3 * 0.06, "#bf{Pred.}: #it{NNLO PDF}")

                    # vertical lines
                    lines = []
                    for i, x in enumerate(obs["bins"][1:-1]):
                        y = Y_MIN + (Y_MAX * sf - Y_MIN) * 0.6
                        line = ROOT.TLine(x, Y_MIN, x, y)
                        line.SetLineStyle(2)
                        line.Draw()
                        lines += [line]

                    # legend
                    leg.Draw()
                    if plot_type == "Generator_comparison":
                        leg2.Draw()

                    ROOT.gPad.RedrawAxis()
                    pad2.cd()
                    if obs["logx"]:
                        pad2.SetLogx()
                    # pad2.SetLogy()
                    mg_obs_norm.Draw("a")
                    mg_obs_norm.GetXaxis().SetLimits(obs["bins"][0], obs["bins"][-1])
                    if obs_name == "eta":
                        Y_MIN = 0.11
                        Y_MAX = 0.29
                    else:
                        Y_MIN = 1e-3
                        Y_MAX = 0.39
                    mg_obs_norm.SetMinimum(Y_MIN * sf)
                    mg_obs_norm.SetMaximum(Y_MAX * sf)

                    # vertical lines
                    for x in obs["bins"][1:-1]:
                        line = ROOT.TLine(x, Y_MIN * sf, x, Y_MAX * sf)
                        line.SetLineStyle(2)
                        line.Draw()
                        lines += [line]

                    ROOT.gPad.RedrawAxis()
                    pad3.cd()
                    if obs["logx"]:
                        pad3.SetLogx()
                    pad3.SetGridy()
                    mg_obs_ratio.Draw("a")
                    mg_obs_ratio.GetXaxis().SetLimits(obs["bins"][0], obs["bins"][-1])
                    if obs_name == "eta":
                        Y_MIN = 0.86
                        Y_MAX = 1.14
                    else:
                        Y_MIN = 0.83
                        Y_MAX = 1.17
                    mg_obs_ratio.SetMinimum(Y_MIN)
                    mg_obs_ratio.SetMaximum(Y_MAX)
                    line3 = ROOT.TLine(obs["bins"][0], 1, obs["bins"][-1], 1)
                    line3.Draw()
                    mg_obs_ratio_theory.Draw()

                    # vertical lines
                    for x in obs["bins"][1:-1]:
                        line = ROOT.TLine(x, Y_MIN, x, Y_MAX)
                        line.SetLineStyle(2)
                        line.Draw()
                        lines += [line]

                    ROOT.gPad.RedrawAxis()
                    c1.Print(f"fit_results/{plot_type}/{options.decay}/W{lep}_{obs_name}.pdf")

                    trash += [mg_obs]
                    trash += [mg_obs_norm]
                    trash += [mg_obs_ratio]
                    trash += [mg_obs_ratio_theory]

            # --------------------------------------------
            # Ladder plots
            # --------------------------------------------
            # ROOT.gStyle.SetEndErrorSize(8)
            proxy_pdf = ROOT.TGraph()
            proxy_pdf.SetLineColor(ROOT.kBlack)
            proxy_pdf.SetLineWidth(5)
            proxy_total = ROOT.TGraph()
            proxy_total.SetLineColor(ROOT.kGray + 1)
            proxy_total.SetLineWidth(3)
            # proxy_total.SetLineStyle(2)

            # save for Rc plot
            data = {}

            for lep in ["minus", "plus", "ratio"]:

                # only Rc combined
                if options.decay == "Dmeson" and lep in ["minus", "plus"]:
                    continue

                # index for theory prediction hist
                if lep == "plus":
                    index = 11
                elif lep == "minus":
                    index = 12
                elif lep == "ratio":
                    index = 13

                data[lep] = {}

                # data
                if lep == "minus":
                    xsec = float(POIs_obs[f"mu_W{lep}_tot"][0]) * priors[f"W{lep}"]
                    xsec_err_up = float(POIs_obs[f"mu_W{lep}_tot"][1]) * priors[f"W{lep}"]
                    xsec_err_dn = abs(float(POIs_obs[f"mu_W{lep}_tot"][2]) * priors[f"W{lep}"])
                    xsec_err_stat_up = float(POIs_stat[f"mu_W{lep}_tot"][1]) * priors[f"W{lep}"]
                    xsec_err_stat_dn = abs(float(POIs_stat[f"mu_W{lep}_tot"][2]) * priors[f"W{lep}"])
                    xsec_err_sys_up = (xsec_err_up**2 - xsec_err_stat_up**2)**0.5
                    xsec_err_sys_dn = (xsec_err_dn**2 - xsec_err_stat_dn**2)**0.5
                    limits = [37, 100]
                    lep_charge = "-"
                    meson_charge = "+"
                    obs_str = "#sigma_{fid}"
                elif lep == "plus":
                    xsec = float(POIs_obs[f"mu_W{lep}_tot"][0]) * priors[f"W{lep}"]
                    xsec_err_up = float(POIs_obs[f"mu_W{lep}_tot"][1]) * priors[f"W{lep}"]
                    xsec_err_dn = abs(float(POIs_obs[f"mu_W{lep}_tot"][2]) * priors[f"W{lep}"])
                    xsec_err_stat_up = float(POIs_stat[f"mu_W{lep}_tot"][1]) * priors[f"W{lep}"]
                    xsec_err_stat_dn = abs(float(POIs_stat[f"mu_W{lep}_tot"][2]) * priors[f"W{lep}"])
                    xsec_err_sys_up = (xsec_err_up**2 - xsec_err_stat_up**2)**0.5
                    xsec_err_sys_dn = (xsec_err_dn**2 - xsec_err_stat_dn**2)**0.5
                    limits = [37, 100]
                    lep_charge = "+"
                    meson_charge = "-"
                    obs_str = "#sigma_{fid}"
                elif lep == "ratio" and options.decay != "Dmeson":
                    xsec = float(POIs_obs["mu_Rc"][0])
                    xsec_err_up = float(POIs_obs["mu_Rc"][1])
                    xsec_err_dn = abs(float(POIs_obs["mu_Rc"][2]))
                    xsec_err_stat_up = float(POIs_stat["mu_Rc"][1])
                    xsec_err_stat_dn = abs(float(POIs_stat["mu_Rc"][2]))
                    xsec_err_sys_up = (xsec_err_up**2 - xsec_err_stat_up**2)**0.5
                    xsec_err_sys_dn = (xsec_err_dn**2 - xsec_err_stat_dn**2)**0.5
                    limits = [0.9, 1.2]
                    lep_charge = "#pm"
                    meson_charge = "#mp"
                    obs_str = "#it{R}_{#it{c}}"
                elif lep == "ratio" and options.decay == "Dmeson":
                    xsec = 0.9709292420861776
                    xsec_err_stat_up = 0.006212765099712398
                    xsec_err_stat_dn = 0.006212765099712398
                    xsec_err_sys_up = 0.010608271899824651
                    xsec_err_sys_dn = 0.010608271899824651
                    xsec_err_up = (xsec_err_sys_up**2 + xsec_err_stat_up**2)**0.5
                    xsec_err_dn = (xsec_err_sys_dn**2 + xsec_err_stat_dn**2)**0.5
                    limits = [0.9, 1.2]
                    lep_charge = "#pm"
                    meson_charge = "#mp"
                    obs_str = "#it{R}_{#it{c}}"

                print(f"--- total cross section for {lep} ---")
                print(f"{xsec} +{xsec_err_stat_up} -{xsec_err_stat_dn} (stat)")
                print(f"{xsec} +{xsec_err_up} -{xsec_err_dn} (sys + stat)")
                print(f"{xsec} +{xsec_err_sys_up} -{xsec_err_sys_dn} (sys only)")

                gr = ROOT.TGraph()
                gr.SetPoint(0, xsec, 1.0)
                gr.SetPoint(1, xsec, -1.0)
                gr.SetLineColor(ROOT.kBlack)
                gr.SetLineStyle(2)
                gr.SetLineWidth(2)

                gr_tot = ROOT.TGraphAsymmErrors()
                gr_tot.SetPoint(0, xsec, 0.0)
                gr_tot.SetPointError(0, xsec_err_up, xsec_err_dn, 1.0, 1.0)
                # gr_tot.SetFillColor(ROOT.kGreen + 1)
                gr_tot.SetFillColor(ROOT.kYellow)
                gr_tot.SetLineWidth(0)

                gr_stat = ROOT.TGraphAsymmErrors()
                gr_stat.SetPoint(0, xsec, 0.0)
                gr_stat.SetPointError(0, xsec_err_stat_up, xsec_err_stat_dn, 1.0, 1.0)
                # gr_stat.SetFillColor(ROOT.kYellow)
                gr_stat.SetFillColor(ROOT.kGreen + 1)
                gr_stat.SetLineWidth(0)

                # multi graph
                mg = ROOT.TMultiGraph()
                mg.Add(gr_tot, "e2")
                mg.Add(gr_stat, "e2")
                mg.Add(gr, "l")

                # data legend
                leg1 = ROOT.TLegend(0.37, 0.75 - 1 * (0.060), 0.90, 0.75)
                leg1.SetBorderSize(0)
                leg1.SetFillColor(0)
                leg1.SetFillStyle(0)
                leg1.SetTextSize(36)
                leg1.SetTextFont(43)
                leg1.SetNColumns(3)
                leg1.AddEntry(gr, "Data", "l")
                leg1.AddEntry(gr_stat, "Stat. Unc.", "f")
                leg1.AddEntry(gr_tot, "Syst. #oplus Stat.", "f")

                # theory legend
                N = 2 + len(theory_dict)
                leg = ROOT.TLegend(0.45, 0.62 - N * (0.041), 0.98, 0.62)
                leg.SetBorderSize(0)
                leg.SetFillColor(0)
                leg.SetFillStyle(0)
                leg.SetTextSize(36)
                leg.SetTextFont(43)
                leg_temp = leg.Clone(f"{leg.GetName()}_1")

                # theory
                for k, (prediction, prediction_dict) in enumerate(theory_dict.items()):
                    pred = ladder_dict[f"{prediction}_{options.decay}_{name}"]
                    xsec = pred["nominal"].GetBinContent(index)

                    # PDF err
                    xsec_pdf_up = pred["pdf_up"].GetBinContent(index) - xsec
                    xsec_pdf_dn = xsec - pred["pdf_dn"].GetBinContent(index)

                    # QCD err
                    xsec_up = xsec * pred["qcd_rel_up"].GetBinContent(index) - xsec
                    xsec_dn = xsec - xsec * pred["qcd_rel_dn"].GetBinContent(index)

                    # hadronization err
                    vals = [h.GetBinContent(index) for h in pred["had"]]
                    err_hadronization = (max(vals) - min(vals)) / 2.
                    err_prod_frac = 0.028 if options.decay == "Dplus" else 0.020
                    err_prod_frac *= xsec
                    err_powhel = 0.030
                    err_powhel *= xsec

                    # total error
                    xsec_up = (xsec_up**2 + xsec_pdf_up**2 + err_hadronization**2)**0.5
                    xsec_dn = (xsec_dn**2 + xsec_pdf_dn**2 + err_hadronization**2)**0.5
                    if lep != "ratio":
                        xsec_up = (xsec_up**2 + err_prod_frac**2 + err_powhel**2)**0.5
                        xsec_dn = (xsec_dn**2 + err_prod_frac**2 + err_powhel**2)**0.5

                    # save
                    data[lep][prediction] = [xsec, xsec_up, xsec_dn, xsec_pdf_up, xsec_pdf_dn]

                    # style
                    gr_theory_marker = ROOT.TGraph()
                    gr_theory_marker.SetPoint(0, xsec, 0.9 - 0.2 * (k + 1))
                    gr_theory_marker.SetMarkerSize(2.0 * prediction_dict["markerScale"])
                    gr_theory_marker.SetMarkerColor(prediction_dict["fillColor"])
                    gr_theory_marker.SetMarkerStyle(prediction_dict["markerStyle2"])

                    gr_theory_marker2 = ROOT.TGraph()
                    gr_theory_marker2.SetPoint(0, xsec, 0.9 - 0.2 * (k + 1))
                    gr_theory_marker2.SetMarkerSize(3.0 * prediction_dict["markerScale"])
                    gr_theory_marker2.SetMarkerColor(prediction_dict["lineColor"])
                    gr_theory_marker2.SetMarkerStyle(prediction_dict["markerStyle2"])

                    gr_theory = ROOT.TGraphAsymmErrors()
                    gr_theory.SetPoint(0, xsec, 0.9 - 0.2 * (k + 1))
                    gr_theory.SetPointError(0, xsec_up, xsec_dn, 0.0, 0.0)
                    gr_theory.SetLineWidth(3)
                    gr_theory.SetLineColor(ROOT.kGray)
                    # gr_theory.SetLineStyle(2)

                    gr_theory_white = gr_theory.Clone(f"{gr_theory.GetName()}_white")
                    gr_theory_white.SetLineColor(ROOT.kBlack)
                    gr_theory_white.SetLineWidth(5)

                    gr_theory_pdf = ROOT.TGraphAsymmErrors()
                    gr_theory_pdf.SetPoint(0, xsec, 0.9 - 0.2 * (k + 1))
                    gr_theory_pdf.SetPointError(0, xsec_pdf_up, xsec_pdf_dn, 0.0, 0.0)
                    gr_theory_pdf.SetLineWidth(5)
                    gr_theory_pdf.SetLineColor(ROOT.kBlack)
                    # gr_theory_pdf.SetLineColor(prediction_dict["lineColor"])

                    mg.Add(gr_theory_white, "e")
                    mg.Add(gr_theory, "e")
                    mg.Add(gr_theory_pdf, "e")
                    mg.Add(gr_theory_marker2, "p")
                    mg.Add(gr_theory_marker, "p")
                    leg.AddEntry(gr_theory_marker, prediction_dict["legendLabel"], "p")
                    leg_temp.AddEntry(gr_theory_marker2, "", "p")

                leg.AddEntry(proxy_pdf, "PDF Unc.", "l")
                leg.AddEntry(proxy_total, "PDF #oplus QCD #oplus Other Unc.", "l")
                leg_temp.AddEntry(proxy_pdf, "", "l")
                leg_temp.AddEntry(proxy_total, "", "l")

                # canvas
                c = ROOT.TCanvas(f"W{lep}Total_{plot_type}", f"W{lep}Total_{plot_type}", 1200, 900)
                c.SetLeftMargin(0.05)
                mg.Draw("a")
                mg.GetYaxis().SetLabelSize(0)
                mg.GetXaxis().SetLabelSize(mg.GetXaxis().GetLabelSize() * 1.1)
                mg.GetXaxis().SetTitleSize(mg.GetXaxis().GetTitleSize() * 1.2)
                mg.GetXaxis().SetTitleOffset(mg.GetXaxis().GetTitleOffset() / 1.2)
                unit_str = ""
                if lep != "ratio":
                    unit_str = " [pb]"
                if options.decay == "Dstar":
                    mg.GetXaxis().SetTitle("%s(#it{W}^{%s}+#it{D*}^{%s})%s" % (obs_str, lep_charge, meson_charge, unit_str))
                elif options.decay == "Dplus":
                    mg.GetXaxis().SetTitle("%s(#it{W}^{%s}+#it{D}^{%s})%s" % (obs_str, lep_charge, meson_charge, unit_str))
                elif options.decay == "Dmeson":
                    mg.GetXaxis().SetTitle("%s(#it{W}^{%s}+#it{D}^{%s})%s" % (obs_str, lep_charge, meson_charge, unit_str))
                mg.GetXaxis().SetLimits(limits[0], limits[1])
                mg.SetMinimum(-1)
                mg.SetMaximum(1)

                # ATLAS label
                l1 = ROOT.TLatex()
                l1.SetTextFont(73)
                l1.SetTextSize(40)
                l1.DrawLatex(limits[0] + (limits[1] - limits[0]) * (55 - 30) / 70., 0.85, "ATLAS")
                l2 = ROOT.TLatex()
                l2.SetTextFont(43)
                l2.SetTextSize(40)
                # l2.DrawLatex(limits[0] + (limits[1] - limits[0]) * (65 - 30) / 70., 0.85 - 0 * 0.14, "Internal")
                l2.DrawLatex(limits[0] + (limits[1] - limits[0]) * (65 - 30) / 70., 0.85 - 0 * 0.14, "")
                l2.DrawLatex(limits[0] + (limits[1] - limits[0]) * (55 - 30) / 70., 0.85 - 1 * 0.14, "#sqrt{s} = 13 TeV, 140 fb^{-1}")
                if lep != "ratio":
                    l2.DrawLatex(limits[0] + (limits[1] - limits[0]) * (55 - 30) / 70., 0.85 - 2 * 0.14,
                                 f"{obs_str} = {gr.GetX()[0]:.1f} #pm{xsec_err_stat_up:.1f} (stat.)^{{+#scale[1.2]{{{xsec_err_sys_up:.1f}}}}}_{{-#scale[1.2]{{{xsec_err_sys_dn:.1f}}}}} (syst.) pb")
                else:
                    l2.DrawLatex(limits[0] + (limits[1] - limits[0]) * (55 - 30) / 70., 0.85 - 2 * 0.14,
                                 f"{obs_str} = {gr.GetX()[0]:.3f} #pm{xsec_err_stat_up:.3f} (stat.) #pm{xsec_err_sys_up:.3f} (syst.)")
                if plot_type == "PDF_comparison":
                    l2.DrawLatex(limits[0] + (limits[1] - limits[0]) * (55 - 30) / 70., 0.85 - 4.5 * 0.14, "#bf{Pred.}: #it{aMC@NLO, full CKM, NNLO PDF}")
                elif plot_type == "NLO_PDF_comparison":
                    l2.DrawLatex(limits[0] + (limits[1] - limits[0]) * (55 - 30) / 70., 0.85 - 4.5 * 0.14, "#bf{Pred.}: #it{aMC@NLO, full CKM, NLO PDF}")

                if options.decay == "Dstar":
                    l2.DrawLatex(limits[0] + (limits[1] - limits[0]) * (80 - 30) / 70., 0.85 - 0 * 0.14,
                                 "#it{W}^{%s}+#it{D*}^{%s}(#rightarrow(K#pi)#pi)" % (lep_charge, meson_charge))
                elif options.decay == "Dplus":
                    l2.DrawLatex(limits[0] + (limits[1] - limits[0]) * (80 - 30) / 70., 0.85 - 0 * 0.14,
                                 "#it{W}^{%s}+#it{D}^{%s}(#rightarrowK#pi#pi)" % (lep_charge, meson_charge))
                elif options.decay == "Dmeson":
                    l2.DrawLatex(limits[0] + (limits[1] - limits[0]) * (80 - 30) / 70., 0.85 - 0 * 0.14,
                                 "#it{W}^{%s}+#it{D}^{%s}(#rightarrowK#pi#pi)" % (lep_charge, meson_charge))
                    l2.DrawLatex(limits[0] + (limits[1] - limits[0]) * (80 - 30) / 70., 0.85 - 1 * 0.14,
                                 "#it{W}^{%s}+#it{D*}^{%s}(#rightarrow(K#pi)#pi)" % (lep_charge, meson_charge))
                # legend
                leg1.Draw()
                leg_temp.Draw()
                leg.Draw()

                # print
                ROOT.gPad.RedrawAxis()
                c.Print(f"fit_results/{plot_type}/{options.decay}/W{lep}_tot_{obs_name}.pdf")
                trash += [mg]

        outfile.Close()


if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()

    # ----------------------------------------------------
    # arguments
    # ----------------------------------------------------
    parser.add_option('-d', '--decay',
                      action="store", dest="decay", default="Dplus",
                      help="Decay mode (defaults to Dplus)")
    # parse input arguments
    options, args = parser.parse_args()

    # run
    main(options, args)
