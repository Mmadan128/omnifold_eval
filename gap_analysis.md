# Gap Analysis: OmniFold Weight Files

## What's in the files?

All three files share 24 observable columns plus weights_nominal and weight_mc. The nominal file is the biggest; it also has weights_dd, 100 weights_ensemble_* columns, and 50 weights_bootstrap_mc_* replicas. Sherpa has 25 bootstrap replicas and nonDY has none.

weight_mc is the raw weight the generator gave each event. OmniFold then trains a classifier to push the MC distribution toward the data, and that learned correction becomes weights_nominal (the mean of 100 ensemble runs). The bootstrap replicas are for uncertainty bands, not direct plotting.

The 24 observables are lepton kinematics (pT_ll, pT_l1/l2, eta_l1/l2, phi_l1/l2, y_ll) and track-jet variables for two jets (pT, y, phi, m, tau1/2/3, Ntracks). All kinematic floats are float32, track counts are int32.

There's also target_dd in the nominal file, looks like the classifier output score kept around for debugging. Not something you'd plot.

## What's missing?

No units. pT_* 

No event selection. 
There's no record of what cuts were applied before running OmniFold: lepton pT/eta thresholds, jet algorithm, track pT floor, overlap removal. If we apply these weights to a new MC sample that used different cuts, the result will be wrong in a subtle way.

The weights sum to 1810 in all three files and nobody says what that means. 

No generator info: no MadGraph5 version, no Sherpa version, no PDF set, no tune. tau1/2/3 are N-subjettiness but the angular measure and β parameter aren't recorded. No timestamps, no analysis ID

## Why standardizing this is hard

HDF5 is fine here, but most HEP software expects ROOT TTrees. Any standard has to either pick a format or ship converters.

Column naming drifts even within one experiment, and getting four major collaborations to agree on canonical names is genuinely painful.

Different analyses define "weight" differently: raw generator weight, normalized, ratio-to-nominal, product of several corrections. A standard needs to say exactly what you're supposed to multiply together.

This dataset itself shows the bootstrap inconsistency problem. Once files with 0 replicas exist in the wild, any script that loops over bootstrap columns silently breaks on them.

Storing all 24 observables alongside the weights is convenient for this size, but won't scale to analyses with hundreds of variables or billions of events. A standard needs to say which columns are mandatory.

