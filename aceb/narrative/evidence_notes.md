# ACE-B / RCS-1 Evidence Notes

- **Claim:** PCM measures pre-change mastery  
  **Evidence:** `validate_pcm_construct()`

- **Claim:** CDL measures detection lag rather than isolated lucky recovery  
  **Evidence:** `validate_cdl_window_behavior()`

- **Claim:** PR measures perseveration rather than generic post-switch error  
  **Evidence:** `validate_pr_perseveration_specificity()`

- **Claim:** The metrics are non-redundant and not reducible to plain accuracy  
  **Evidence:** `validate_metric_non_redundancy()`

- **Claim:** Baseline agents show meaningful behavioral separation  
  **Evidence:** deterministic validation summary + comparison layer

- **Claim:** Similar accuracy can hide different adaptive behavior  
  **Evidence:** `tests/test_additional_validation_cases.py::test_same_accuracy_can_hide_different_cdl_and_pr`

- **Claim:** Equal post-switch error count does not imply equal perseveration  
  **Evidence:** `tests/test_additional_validation_cases.py::test_same_error_rate_can_produce_different_pr`
