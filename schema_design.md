# Metadata Schema Design

## How it's laid out

The keys are ordered the way someone would ask questions: analysis = what is this, generation = how was it made, files = what do I load, weights = which column do I use, observables = what units, event_selection = what cuts were applied.

files separates nominal from systematics so if you just want to make a quick plot you only need to look at one place. Systematics are a list, so adding more variations later is just appending an entry.

Weight columns use flat string descriptions instead of nested objects. It's less machine-parseable but a lot easier to read at a glance, which matters more for a result file people will mostly open in a text editor.

## What I kept and why

Units on each observable, easiest thing to get wrong. Someone histograms pT in MeV by accident and every cross-section value is off by a million. One line fixes it.

recommended under weights: five different weight column types exist in these files and nobody should need to read a paper to know which one to pass to np.histogram.

n_bootstrap_replicas per file: the three files actually have 50 / 25 / 0 replicas, an inconsistency that's totally invisible without metadata. Documenting it at least makes the problem obvious.

event_selection as a warning rather than just missing. An explicit note saying "not stored, watch out" is more useful than just not having the field.

Provenance fields left as null, keeping them there makes the schema a checklist. Someone filling this in later knows exactly what's expected.

## What I dropped and why

Neural net hyperparameters (architecture, learning rate, epochs) belong in a training config or a paper appendix, not a result file.

Per-event uncertainty estimates are already in the bootstrap replicas in the data files, no need to duplicate.

Binning scheme is the user's call. Encoding it here would lock the schema to one specific analysis.

## How to use this file

1. Check analysis to confirm this is the measurement you want.
2. Grab files.nominal.filename, load it with pd.read_hdf(filename, key="df").
3. Use weights.recommended as your per-event weight column, that's it for a basic plot.
4. For systematics, repeat with the files under files.systematics and compare.
5. For stat. uncertainty, loop over weights_bootstrap_mc_0..N (N from n_bootstrap_replicas) and take std across the histograms.
6. Read event_selection.note before applying weights to any new MC sample.

