# Ownership Scale (Exact-Match Baseline)

This project estimates **ownership scale** for likely corporate-owned residential properties in Austin by grouping parcels based on an **exact match** of cleaned owner name and owner mailing address.

It is designed as a simple extension of a prior workflow that reproduced a set of likely corporate-owned properties from Travis County Appraisal District (TCAD) data. This repository does **not** reproduce that earlier filtering step. Instead, it takes the resulting parcel-level dataset as input and adds owner-scale measures.

## Project purpose

The script creates a baseline measure of ownership scale by asking:

> How many parcels are associated with the same cleaned owner name and cleaned owner mailing address?

This provides a straightforward approximation of portfolio size that can be used for exploratory analysis, mapping, and downstream urban research workflows.

## Important methodological note

This repository uses **exact matching only** after basic text cleaning. It does **not**:

- use fuzzy matching
- perform entity resolution across near-matches
- identify beneficial ownership
- recursively trace shell companies or corporate officers

As a result, the output should be interpreted as a **conservative baseline estimate** of ownership scale. Owners with slightly different name/address strings may still be split into separate groups.

## Input data

The script expects a CSV file named:

`target_properties_reproduced.csv`

Each row should represent one parcel. The dataset should already contain the subset of likely corporate-owned properties from the prior filtering workflow.

The script currently assumes the following columns exist:

- `owner_name`
- `owner_address`

Optional columns such as `situs_lat` and `situs_long` will be included in the parcel-level output if present.

## What the script does

1. Loads `target_properties_reproduced.csv`
2. Cleans owner name and owner address fields by:
   - filling missing values with empty strings
   - converting text to uppercase
   - trimming leading/trailing whitespace
   - collapsing repeated internal whitespace
3. Creates a combined owner identifier:
   - `owner_entity = owner_name_clean | owner_address_clean`
4. Groups parcels by this exact cleaned owner identifier
5. Counts the number of properties associated with each owner entity
6. Creates:
   - a parcel-level output with owner-scale variables
   - an owner-level summary table

## Outputs

The script writes two files:

### 1. `target_properties_with_owner_scale.csv`

Parcel-level output containing selected variables such as:

- cleaned owner name
- cleaned owner address
- parcel coordinates (if available)
- `num_other_properties`
- `ownership_scale_score`

### 2. `ownership_scale_per_owner.xlsx`

Owner-level summary table containing:

- `owner_entity`
- cleaned owner name
- cleaned owner address
- `num_properties`
- ownership scale category
- ownership scale score

## Ownership scale variables

### `num_properties`
The total number of parcels associated with an exact cleaned owner-name/address match.

### `num_other_properties`
`num_properties - 1`, which expresses how many additional parcels are associated with the same owner entity beyond the focal parcel.

### `ownership_scale_category`
A simple rule-based category derived from `num_properties`:

- `single-property`
- `small-scale`
- `mid-scale`
- `large-scale`
- `very-large-scale`

These thresholds are adjustable and should be treated as exploratory rather than definitive.

### `ownership_scale_score`
A continuous score defined as:

`log10(num_properties + 1)`

This compresses the distribution of portfolio sizes and may be useful for mapping or modeling.

## How to run

From the project folder:

```bash
python ownership_scale.py
```